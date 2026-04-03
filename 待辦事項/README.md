# OpenClaw Todo Hub

雲端部署的待辦網站，讓你用網頁管理待辦，也讓 OpenClaw 透過 Bearer token API 代你新增、刪除、完成與還原任務。

## Stack

- Next.js App Router
- Supabase Auth + Postgres
- Vercel-ready deployment
- REST API for OpenClaw

## Features

- Magic link 登入，限制單一擁有者帳號
- 待辦欄位：標題、說明、可空截止日、完成狀態、分類標籤
- 軟刪除與還原
- 繁體中文操作介面
- OpenClaw 專用 Bearer token API

## Environment Variables

將 `.env.example` 複製成 `.env.local`，填入以下值：

```bash
NEXT_PUBLIC_SITE_URL=http://localhost:3000
NEXT_PUBLIC_SUPABASE_URL=
NEXT_PUBLIC_SUPABASE_ANON_KEY=
SUPABASE_SERVICE_ROLE_KEY=
APP_OWNER_EMAIL=you@example.com
OPENCLAW_API_TOKEN=replace-with-a-long-random-string
```

## Supabase Setup

1. 建立一個 Supabase 專案。
2. 在 SQL Editor 執行 [supabase/migrations/202604030001_init_tasks.sql](/C:/Users/user/Desktop/Cowork/Vibecoding/待辦事項/supabase/migrations/202604030001_init_tasks.sql)。
3. 在 Authentication 啟用 Email OTP / Magic Link。
4. 建議關閉公開註冊，只允許你的 `APP_OWNER_EMAIL` 登入。
5. 將 `NEXT_PUBLIC_SUPABASE_URL`、`NEXT_PUBLIC_SUPABASE_ANON_KEY`、`SUPABASE_SERVICE_ROLE_KEY` 填入環境變數。

## Local Development

```bash
npm install
npm run dev
```

應用程式啟動後：

- `/login` 提供你本人登入
- `/` 顯示待辦儀表板
- `/api/tasks` 與 `/api/tasks/:id` 提供 OpenClaw 或已登入網頁使用

## API Examples

完整 OpenAPI 規格在 [docs/openclaw-api.openapi.yaml](C:\Users\user\Desktop\Cowork\Vibecoding\待辦事項\docs\openclaw-api.openapi.yaml)。

新增待辦：

```bash
curl -X POST http://localhost:3000/api/tasks \
  -H "Authorization: Bearer YOUR_OPENCLAW_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title":"買牛奶","description":"無糖豆漿也可以","dueDate":null,"tags":["家務"]}'
```

標記完成：

```bash
curl -X PATCH http://localhost:3000/api/tasks/TASK_ID \
  -H "Authorization: Bearer YOUR_OPENCLAW_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"isCompleted":true}'
```

軟刪除：

```bash
curl -X DELETE http://localhost:3000/api/tasks/TASK_ID \
  -H "Authorization: Bearer YOUR_OPENCLAW_TOKEN"
```

還原：

```bash
curl -X POST http://localhost:3000/api/tasks/TASK_ID/restore \
  -H "Authorization: Bearer YOUR_OPENCLAW_TOKEN"
```

## Verification

可用的檢查指令：

```bash
npm run typecheck
npm run test
npm run build
```

如果要部署到 Vercel，請同步設定所有環境變數，並把 `NEXT_PUBLIC_SITE_URL` 改成正式網址。
