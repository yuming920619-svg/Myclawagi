// epl_ecc_decoder.v
`include "EPLFFRAM02_spec.vh"

module epl_ecc_decoder (
           input  wire                    pCLK_i,
           input  wire                    nRST_i,
           input  wire                    pREAD_i,
           input  wire [`TWORD_WIDTH-1:0] pPARITYDATA_i,
           output reg  [`WORD_WIDTH-1:0]  pDATA_o,
           output reg                     pERROR_o
       );

// -----------------------------------------------------------------------------
// Mainstream BCH decoder flow for shortened BCH(15,5,t=3):
//   1) Compute syndromes S1..S6 in GF(2^4)
//   2) Berlekamp-Massey to get error-locator polynomial Lambda(x)
//   3) Chien search over 15 bit positions
//   4) Correct bits when root-count == locator degree
// -----------------------------------------------------------------------------

// ---------- GF(16) arithmetic (primitive polynomial p(x)=x^4 + x + 1 = 5'b1_0011) ----------
function [3:0] gf_mul4;
    input [3:0] a;
    input [3:0] b;
    reg   [7:0] p;
    integer i;
begin
    p = 8'h00;
    for (i = 0; i < 4; i = i + 1)
        if (b[i]) p = p ^ (a << i);

    // reduce modulo x^4 + x + 1
    for (i = 7; i >= 4; i = i - 1)
        if (p[i]) p = p ^ (8'b0001_0011 << (i-4));

    gf_mul4 = p[3:0];
end
endfunction

function [3:0] gf_pow_alpha;
    input [3:0] exp_mod15; // 0..14
begin
    case (exp_mod15)
        4'd0:  gf_pow_alpha = 4'h1;
        4'd1:  gf_pow_alpha = 4'h2;
        4'd2:  gf_pow_alpha = 4'h4;
        4'd3:  gf_pow_alpha = 4'h8;
        4'd4:  gf_pow_alpha = 4'h3;
        4'd5:  gf_pow_alpha = 4'h6;
        4'd6:  gf_pow_alpha = 4'hC;
        4'd7:  gf_pow_alpha = 4'hB;
        4'd8:  gf_pow_alpha = 4'h5;
        4'd9:  gf_pow_alpha = 4'hA;
        4'd10: gf_pow_alpha = 4'h7;
        4'd11: gf_pow_alpha = 4'hE;
        4'd12: gf_pow_alpha = 4'hF;
        4'd13: gf_pow_alpha = 4'hD;
        4'd14: gf_pow_alpha = 4'h9;
        default: gf_pow_alpha = 4'h0;
    endcase
end
endfunction

function [3:0] gf_inv4;
    input [3:0] a;
begin
    case (a)
        4'h0: gf_inv4 = 4'h0;
        4'h1: gf_inv4 = 4'h1;
        4'h2: gf_inv4 = 4'h9;
        4'h3: gf_inv4 = 4'hE;
        4'h4: gf_inv4 = 4'hD;
        4'h5: gf_inv4 = 4'hB;
        4'h6: gf_inv4 = 4'h7;
        4'h7: gf_inv4 = 4'h6;
        4'h8: gf_inv4 = 4'hF;
        4'h9: gf_inv4 = 4'h2;
        4'hA: gf_inv4 = 4'hC;
        4'hB: gf_inv4 = 4'h5;
        4'hC: gf_inv4 = 4'hA;
        4'hD: gf_inv4 = 4'h4;
        4'hE: gf_inv4 = 4'h3;
        4'hF: gf_inv4 = 4'h8;
        default: gf_inv4 = 4'h0;
    endcase
end
endfunction

function [3:0] gf_div4;
    input [3:0] a;
    input [3:0] b;
begin
    if (b == 4'h0) gf_div4 = 4'h0;
    else           gf_div4 = gf_mul4(a, gf_inv4(b));
end
endfunction

// ---------- combinational decode ----------
reg [`TWORD_WIDTH-1:0] corrected_code_w;
reg [`WORD_WIDTH-1:0]  pNextData_w;
reg                    pNextError_w;
reg                    pValid_w;

integer i, n, j;

reg [3:0] S [1:6];
reg [3:0] C [0:3];
reg [3:0] B [0:3];
reg [3:0] T [0:3];

reg [3:0] discr_w;
reg [3:0] coef_w;
reg [3:0] x_w;
reg [3:0] x2_w;
reg [3:0] x3_w;
reg [3:0] eval_w;

integer L_w;
integer m_w;
reg [3:0] b_w;
integer root_count_w;
reg syndrome_nonzero_w;
reg uncorrectable_w;

always @(*)
begin
    corrected_code_w = pPARITYDATA_i;
    pNextData_w      = {`WORD_WIDTH{1'b0}};
    pNextError_w     = 1'b0;
    pValid_w         = 1'b0;

    if (pREAD_i)
    begin
        // 1) Syndrome computation: S_k = r(alpha^k), k=1..6
        for (n = 1; n <= 6; n = n + 1)
        begin
            S[n] = 4'h0;
            for (i = 0; i < `TWORD_WIDTH; i = i + 1)
            begin
                if (pPARITYDATA_i[i])
                    S[n] = S[n] ^ gf_pow_alpha((n*i) % 15);
            end
        end

        syndrome_nonzero_w = (S[1]!=0) | (S[2]!=0) | (S[3]!=0) | (S[4]!=0) | (S[5]!=0) | (S[6]!=0);

        if (!syndrome_nonzero_w)
        begin
            // no error
            corrected_code_w = pPARITYDATA_i;
            pNextError_w     = 1'b0;
        end
        else
        begin
            // 2) Berlekamp-Massey for t=3
            C[0] = 4'h1; C[1] = 4'h0; C[2] = 4'h0; C[3] = 4'h0;
            B[0] = 4'h1; B[1] = 4'h0; B[2] = 4'h0; B[3] = 4'h0;
            L_w  = 0;
            m_w  = 1;
            b_w  = 4'h1;

            for (n = 0; n < 6; n = n + 1)
            begin
                discr_w = S[n+1];
                for (j = 1; j <= L_w; j = j + 1)
                    discr_w = discr_w ^ gf_mul4(C[j], S[n+1-j]);

                if (discr_w != 4'h0)
                begin
                    T[0] = C[0]; T[1] = C[1]; T[2] = C[2]; T[3] = C[3];
                    coef_w = gf_div4(discr_w, b_w);

                    if ((0+m_w) <= 3) C[0+m_w] = C[0+m_w] ^ gf_mul4(coef_w, B[0]);
                    if ((1+m_w) <= 3) C[1+m_w] = C[1+m_w] ^ gf_mul4(coef_w, B[1]);
                    if ((2+m_w) <= 3) C[2+m_w] = C[2+m_w] ^ gf_mul4(coef_w, B[2]);
                    if ((3+m_w) <= 3) C[3+m_w] = C[3+m_w] ^ gf_mul4(coef_w, B[3]);

                    if ((2*L_w) <= n)
                    begin
                        L_w = n + 1 - L_w;
                        B[0] = T[0]; B[1] = T[1]; B[2] = T[2]; B[3] = T[3];
                        b_w  = discr_w;
                        m_w  = 1;
                    end
                    else
                    begin
                        m_w = m_w + 1;
                    end
                end
                else
                begin
                    m_w = m_w + 1;
                end
            end

            // 3) Chien search: evaluate Lambda(alpha^{-pos})
            corrected_code_w = pPARITYDATA_i;
            root_count_w     = 0;

            for (i = 0; i < `TWORD_WIDTH; i = i + 1)
            begin
                if (i == 0)
                    x_w = gf_pow_alpha(4'd0);      // alpha^0
                else
                    x_w = gf_pow_alpha(15 - i);    // alpha^{-i} = alpha^(15-i)

                x2_w = gf_mul4(x_w, x_w);
                x3_w = gf_mul4(x2_w, x_w);

                eval_w = 4'h1
                       ^ gf_mul4(C[1], x_w)
                       ^ gf_mul4(C[2], x2_w)
                       ^ gf_mul4(C[3], x3_w);

                if (eval_w == 4'h0)
                begin
                    corrected_code_w[i] = ~corrected_code_w[i];
                    root_count_w = root_count_w + 1;
                end
            end

            // 4) Correction validity check
            uncorrectable_w = 1'b0;
            if ((L_w < 0) || (L_w > 3))
                uncorrectable_w = 1'b1;
            else if (root_count_w != L_w)
                uncorrectable_w = 1'b1;

            if (uncorrectable_w)
            begin
                corrected_code_w = pPARITYDATA_i; // keep raw when uncorrectable
                pNextError_w     = 1'b1;
            end
            else
            begin
                // corrected (or detectable error corrected)
                pNextError_w     = 1'b1;
            end
        end

        // shortened payload mapping: payload5 = {0, data[3:0]} at codeword[14:10]
        pNextData_w = corrected_code_w[13:10];
        pValid_w    = 1'b1;
    end
end

always @(posedge pCLK_i or negedge nRST_i)
begin
    if (!nRST_i)
    begin
        pDATA_o  <= {`WORD_WIDTH{1'b0}};
        pERROR_o <= 1'b0;
    end
    else if (pValid_w)
    begin
        pDATA_o  <= pNextData_w;
        pERROR_o <= pNextError_w;
    end
    else
    begin
        pDATA_o  <= {`WORD_WIDTH{1'b0}};
        pERROR_o <= 1'b0;
    end
end

endmodule
