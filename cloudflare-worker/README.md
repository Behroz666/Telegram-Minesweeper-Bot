# Telegram Minesweeper Bot (Cloudflare Workers)

A JavaScript port of the Telegram Minesweeper bot that runs entirely on Cloudflare Workers.

Unlike the Python version (which uses long polling), this version receives updates through a Telegram webhook. Game state is stored in a Cloudflare KV namespace, so no server or database is required.

## Features

- 8x8 board with 10 mines
- Safe first click
- Flood-fill opening of empty cells
- Mine mode and flag mode buttons
- Win/loss detection with elapsed time
- `/start` and `/info` commands
- Optional secret token verification for the webhook
- Pure game logic with unit tests
- Free-tier friendly (Workers + KV)

## Project structure

```
cloudflare-worker/
├── src/
│   ├── game.js       # Game rules and board rendering
│   └── index.js      # Worker, Telegram API and webhook handling
├── test/
│   └── game.test.js  # Game logic tests
├── wrangler.toml     # Worker and KV configuration
├── package.json
└── README.md
```

## Requirements

- A Cloudflare account
- Node.js 18 or newer
- A Telegram bot token from [@BotFather](https://t.me/BotFather)

## Setup guide

### 1. Install dependencies

```bash
cd cloudflare-worker
npm install
```

### 2. Log in to Cloudflare

```bash
npx wrangler login
```

### 3. Create the KV namespace

```bash
npx wrangler kv namespace create GAMES
```

The command prints an `id`. Open `wrangler.toml` and replace the placeholder:

```toml
[[kv_namespaces]]
binding = "GAMES"
id = "REPLACE_WITH_YOUR_KV_NAMESPACE_ID"
```

with the id returned by Wrangler.

### 4. Add the bot token

```bash
npx wrangler secret put BOT_TOKEN
```

Paste the token from BotFather when prompted.

### 5. (Recommended) Add a webhook secret

Generate a random string, for example:

```bash
openssl rand -hex 32
```

Store it as a Worker secret:

```bash
npx wrangler secret put WEBHOOK_SECRET
```

Keep this value — it is also used when registering the webhook in step 7.

If you skip this step, do not set `WEBHOOK_SECRET`; the worker will accept unsigned webhook requests.

### 6. Deploy the worker

```bash
npm run deploy
```

Wrangler prints the deployed URL, for example:

```
https://telegram-minesweeper-bot.<your-subdomain>.workers.dev
```

### 7. Register the Telegram webhook

Replace `<BOT_TOKEN>`, `<WORKER_URL>` and `<WEBHOOK_SECRET>` with your values. `<WORKER_URL>` is the full deployed URL including `https://` and the trailing slash, for example `https://telegram-minesweeper-bot.my-name.workers.dev/`.

```bash
curl -X POST "https://api.telegram.org/bot<BOT_TOKEN>/setWebhook" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "<WORKER_URL>",
    "secret_token": "<WEBHOOK_SECRET>",
    "allowed_updates": ["message", "callback_query"]
  }'
```

If you did not configure `WEBHOOK_SECRET`, remove the `secret_token` field.

Check the result:

```bash
curl "https://api.telegram.org/bot<BOT_TOKEN>/getWebhookInfo"
```

The response should contain your worker URL and no `last_error_message`.

### 8. Play

Open your bot in Telegram and send:

- `/start` — start a new game
- `/info` — show the game instructions

Click a cell to open it. Use the `💣` and `🚩` buttons to switch between mine mode and flag mode.

## Local development

Run the game logic tests:

```bash
npm test
```

Run the worker locally:

```bash
npx wrangler dev
```

For local secrets, create a `.dev.vars` file (do not commit it):

```
BOT_TOKEN=123456:your-token
WEBHOOK_SECRET=your-secret
```

Telegram cannot reach `localhost` directly, so either use a tunnel such as Cloudflare Tunnel and point the webhook at the tunnel URL, or deploy the worker to test the full flow.

## Configuration reference

| Name | Type | Required | Description |
| --- | --- | --- | --- |
| `BOT_TOKEN` | Secret | Yes | Telegram bot token from BotFather |
| `WEBHOOK_SECRET` | Secret | No | Must match the `secret_token` used in `setWebhook` |
| `GAMES` | KV binding | Yes | Stores each chat's game state under `game:<chat id>` |

Game state expires automatically after 7 days. Sending `/start` replaces any existing game in that chat.

## Updating the worker

After changing the code:

```bash
npm test
npm run deploy
```

The webhook URL does not change, so there is no need to call `setWebhook` again.

## Troubleshooting

**The bot does not respond**

- Verify the webhook: `curl "https://api.telegram.org/bot<BOT_TOKEN>/getWebhookInfo"`
- Make sure the webhook URL ends with `/` and uses `https://`.
- Check worker logs with `npm run tail`.

**`Unauthorized` responses in the webhook**

- `WEBHOOK_SECRET` is set in the worker but the webhook was registered without `secret_token`, or the two values differ.
- Re-run `setWebhook` with the same value, or remove the secret from the worker.

**`BOT_TOKEN secret is not configured`**

- Run `npx wrangler secret put BOT_TOKEN` and redeploy if necessary.

**`KV namespace not found` or `GAMES is undefined`**

- Create the namespace with `npx wrangler kv namespace create GAMES`.
- Copy its `id` into `wrangler.toml` and run `npm run deploy` again.

**Old buttons stop working**

- Each `/start` creates a new game message. Buttons from older messages are intentionally rejected with `Start again`.

**Telegram retries or duplicate responses**

- The worker always returns HTTP 200 after processing an update to avoid duplicate retries. Inspect `npm run tail` for errors from the Telegram API.

## Notes

- Cloudflare KV is eventually consistent. If several users click the same board at exactly the same time, a rare lost update is possible. Normal single-player use is unaffected.
- Telegram limits callback data to 64 bytes; this bot uses short strings such as `12`, `flag`, `bomb` and `done`.
- Keep your bot token and webhook secret private. Never commit them to the repository.
