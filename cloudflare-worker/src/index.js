import {
  buildKeyboard,
  createGame,
  gameText,
  openCell,
  toggleFlag,
  TOTAL_CELLS,
} from "./game.js";

const DESCRIPTION = `Minesweeper: Overview and How to Play

Objective:
The goal of Minesweeper is to clear a grid of hidden mines without detonating any. The numbers revealed on the grid indicate how many mines are adjacent to that square, helping you deduce where the mines are hidden.

How to Play:
   - Use /start to start new game
   - The first click will definitely reveal a number or an empty space. An empty space indicates no adjacent mines.
   - Each number on a revealed square shows how many mines are adjacent to it (including diagonals). Use this information to figure out where the mines might be.
   - If you click on a mine, the game is over.
   - The game is won when all non-mine squares are revealed.
   - You can click on the Flag button below the game to mark mines (click again to remove flag). You can open cells by clicking on the mine button.

Tips:
- Start with corners or edges to get better information.
- If you're unsure, guess, but be cautious!
- The mine counter is based on the number of your flags.

Enjoy the challenge and improve your strategy with practice!`;

const GAME_TTL_SECONDS = 60 * 60 * 24 * 7;

function gameKey(chatId) {
  return `game:${chatId}`;
}

async function telegram(env, method, payload) {
  if (!env.BOT_TOKEN) {
    throw new Error("BOT_TOKEN secret is not configured");
  }

  const response = await fetch(
    `https://api.telegram.org/bot${env.BOT_TOKEN}/${method}`,
    {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify(payload),
    },
  );

  let data;
  try {
    data = await response.json();
  } catch {
    data = { ok: false, description: `HTTP ${response.status}` };
  }

  if (!data.ok) {
    console.error(`Telegram ${method} failed:`, data.description || data);
  }

  return data;
}

async function loadGame(env, chatId) {
  const raw = await env.GAMES.get(gameKey(chatId));
  if (!raw) return null;

  try {
    return JSON.parse(raw);
  } catch {
    return null;
  }
}

async function saveGame(env, game) {
  await env.GAMES.put(gameKey(game.chatId), JSON.stringify(game), {
    expirationTtl: GAME_TTL_SECONDS,
  });
}

async function editGameMessage(env, game) {
  return telegram(env, "editMessageText", {
    chat_id: game.chatId,
    message_id: game.messageId,
    text: gameText(game),
    reply_markup: buildKeyboard(game),
  });
}

async function answerCallback(env, callbackQueryId, text, showAlert = false) {
  return telegram(env, "answerCallbackQuery", {
    callback_query_id: callbackQueryId,
    text,
    show_alert: showAlert,
  });
}

async function handleStart(env, message) {
  const game = createGame(message.chat.id);

  const sent = await telegram(env, "sendMessage", {
    chat_id: message.chat.id,
    text: gameText(game),
    reply_markup: buildKeyboard(game),
  });

  if (sent.ok) {
    game.messageId = sent.result.message_id;
    await saveGame(env, game);
  }
}

async function handleCallback(env, query) {
  const chatId = query.message?.chat?.id;
  const messageId = query.message?.message_id;
  const data = query.data || "";

  if (chatId === undefined || messageId === undefined) {
    await answerCallback(env, query.id, "Start again", true);
    return;
  }

  const game = await loadGame(env, chatId);

  if (!game || game.messageId !== messageId) {
    await answerCallback(env, query.id, "Start again", true);
    return;
  }

  if (data === "done" || game.status === "won" || game.status === "lost") {
    await answerCallback(env, query.id, "Your game is done. use /start");
    return;
  }

  if (data === "flag" || data === "bomb") {
    const nextMode = data === "flag" ? "flag" : "bomb";

    if (game.mode === nextMode) {
      await answerCallback(
        env,
        query.id,
        nextMode === "flag"
          ? "Flag mode already enabled"
          : "Bomb mode already enabled",
      );
      return;
    }

    game.mode = nextMode;
    await saveGame(env, game);
    await editGameMessage(env, game);
    await answerCallback(
      env,
      query.id,
      nextMode === "flag" ? "Flag mode enabled" : "Mine mode enabled",
    );
    return;
  }

  const index = Number(data) - 1;
  if (!Number.isInteger(index) || index < 0 || index >= TOTAL_CELLS) {
    await answerCallback(env, query.id, "Unknown action");
    return;
  }

  if (game.mode === "flag") {
    const result = toggleFlag(game, index);

    if (result.result === "already-opened") {
      await answerCallback(env, query.id, "Cell already opened");
      return;
    }

    if (result.result === "invalid" || result.result === "done") {
      await answerCallback(env, query.id, "Start again", true);
      return;
    }

    await saveGame(env, game);
    await editGameMessage(env, game);
    await answerCallback(
      env,
      query.id,
      result.result === "flagged" ? "Flag added" : "Flag removed",
    );
    return;
  }

  const result = openCell(game, index);

  if (result.result === "flagged") {
    await answerCallback(env, query.id, "It's Flag! you have to remove it first");
    return;
  }

  if (result.result === "already-opened") {
    await answerCallback(env, query.id, "Cell already opened");
    return;
  }

  if (result.result === "invalid" || result.result === "done") {
    await answerCallback(env, query.id, "Your game is done. use /start");
    return;
  }

  await saveGame(env, game);
  await editGameMessage(env, game);

  if (result.result === "lost") {
    await answerCallback(env, query.id, "You lost");
    await celebrate(env, game, "🔥", "💣");
    return;
  }

  if (result.result === "won") {
    await answerCallback(env, query.id, "Game won");
    await celebrate(env, game, "🎉", "🎉");
    return;
  }

  await answerCallback(env, query.id, "New cell opened");
}

async function celebrate(env, game, reaction, text) {
  try {
    await telegram(env, "setMessageReaction", {
      chat_id: game.chatId,
      message_id: game.messageId,
      reaction: [{ type: "emoji", emoji: reaction }],
      is_big: true,
    });
  } catch (error) {
    console.error("Unable to set reaction:", error);
  }

  try {
    await telegram(env, "sendMessage", {
      chat_id: game.chatId,
      text,
    });
  } catch (error) {
    console.error("Unable to send result message:", error);
  }
}

async function handleUpdate(env, update) {
  if (update.message?.text) {
    const command = update.message.text.trim().split(/\s+/)[0];

    if (command === "/start" || command.startsWith("/start@")) {
      await handleStart(env, update.message);
      return;
    }

    if (command === "/info" || command.startsWith("/info@")) {
      await telegram(env, "sendMessage", {
        chat_id: update.message.chat.id,
        text: DESCRIPTION,
      });
    }

    return;
  }

  if (update.callback_query) {
    await handleCallback(env, update.callback_query);
  }
}

export default {
  async fetch(request, env) {
    if (request.method === "GET") {
      return new Response("Telegram Minesweeper bot is running.", {
        headers: { "content-type": "text/plain; charset=utf-8" },
      });
    }

    if (request.method !== "POST") {
      return new Response("Method Not Allowed", { status: 405 });
    }

    if (env.WEBHOOK_SECRET) {
      const received = request.headers.get("X-Telegram-Bot-Api-Secret-Token");
      if (received !== env.WEBHOOK_SECRET) {
        return new Response("Unauthorized", { status: 401 });
      }
    }

    let update;
    try {
      update = await request.json();
    } catch {
      return new Response("Bad Request", { status: 400 });
    }

    try {
      await handleUpdate(env, update);
    } catch (error) {
      console.error("Failed to handle update:", error);
    }

    return new Response("ok", {
      headers: { "content-type": "text/plain; charset=utf-8" },
    });
  },
};
