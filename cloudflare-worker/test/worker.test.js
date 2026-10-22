import test from "node:test";
import assert from "node:assert/strict";

import worker from "../src/index.js";

function createEnv() {
  const store = new Map();

  return {
    store,
    env: {
      BOT_TOKEN: "test-token",
      GAMES: {
        async get(key) {
          return store.get(key) ?? null;
        },
        async put(key, value) {
          store.set(key, value);
        },
      },
    },
  };
}

function installTelegramMock(t) {
  const calls = [];
  const originalFetch = globalThis.fetch;

  globalThis.fetch = async (url, options) => {
    const method = String(url).split("/").pop();
    const payload = JSON.parse(options.body);
    calls.push({ method, payload });

    const result = method === "sendMessage" ? { message_id: 100 } : true;
    return new Response(JSON.stringify({ ok: true, result }), {
      headers: { "content-type": "application/json" },
    });
  };

  t.after(() => {
    globalThis.fetch = originalFetch;
  });

  return calls;
}

async function sendUpdate(env, update) {
  const request = new Request("https://worker.example/", {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify(update),
  });

  return worker.fetch(request, env);
}

test("starting a game stores it and opening a cell edits the message", async (t) => {
  const calls = installTelegramMock(t);
  const { env, store } = createEnv();

  const startResponse = await sendUpdate(env, {
    update_id: 1,
    message: {
      message_id: 1,
      chat: { id: 42 },
      text: "/start",
    },
  });

  assert.equal(startResponse.status, 200);

  const startCall = calls.find((call) => call.method === "sendMessage");
  assert.ok(startCall);
  assert.match(startCall.payload.text, /Minesweeper Game/);

  const saved = JSON.parse(store.get("game:42"));
  assert.equal(saved.messageId, 100);
  assert.equal(saved.status, "ready");

  await sendUpdate(env, {
    update_id: 2,
    callback_query: {
      id: "callback-1",
      data: "1",
      from: { id: 42 },
      message: {
        message_id: 100,
        chat: { id: 42 },
      },
    },
  });

  const answers = calls.filter((call) => call.method === "answerCallbackQuery");
  assert.ok(answers.length > 0);
  assert.ok(calls.some((call) => call.method === "editMessageText"));

  const updated = JSON.parse(store.get("game:42"));
  assert.notEqual(updated.status, "ready");
  assert.ok(updated.revealed.length > 0);
});

test("the flag button switches modes", async (t) => {
  const calls = installTelegramMock(t);
  const { env, store } = createEnv();

  await sendUpdate(env, {
    update_id: 3,
    message: {
      message_id: 2,
      chat: { id: 7 },
      text: "/start",
    },
  });

  await sendUpdate(env, {
    update_id: 4,
    callback_query: {
      id: "callback-2",
      data: "flag",
      from: { id: 7 },
      message: {
        message_id: 100,
        chat: { id: 7 },
      },
    },
  });

  const updated = JSON.parse(store.get("game:7"));
  assert.equal(updated.mode, "flag");

  const answer = calls.find(
    (call) =>
      call.method === "answerCallbackQuery" &&
      call.payload.text === "Flag mode enabled",
  );
  assert.ok(answer);
});

test("stale buttons are rejected", async (t) => {
  const calls = installTelegramMock(t);
  const { env } = createEnv();

  await sendUpdate(env, {
    update_id: 5,
    message: {
      message_id: 3,
      chat: { id: 9 },
      text: "/start",
    },
  });

  await sendUpdate(env, {
    update_id: 6,
    callback_query: {
      id: "callback-3",
      data: "1",
      from: { id: 9 },
      message: {
        message_id: 999,
        chat: { id: 9 },
      },
    },
  });

  const answer = calls.find(
    (call) =>
      call.method === "answerCallbackQuery" &&
      call.payload.text === "Start again",
  );
  assert.ok(answer);
  assert.equal(answer.payload.show_alert, true);
});

test("the webhook secret is checked when configured", async (t) => {
  installTelegramMock(t);
  const { env } = createEnv();
  env.WEBHOOK_SECRET = "super-secret";

  const request = new Request("https://worker.example/", {
    method: "POST",
    headers: {
      "content-type": "application/json",
      "X-Telegram-Bot-Api-Secret-Token": "wrong",
    },
    body: JSON.stringify({ update_id: 7 }),
  });

  const response = await worker.fetch(request, env);
  assert.equal(response.status, 401);
});
