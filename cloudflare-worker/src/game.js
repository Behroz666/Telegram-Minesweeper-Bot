export const SIZE = 8;
export const TOTAL_CELLS = SIZE * SIZE;
export const MINE_COUNT = 10;

export const HIDDEN = "▫️";
export const FLAG = "🚩";
export const MINE = "💣";
export const EXPLODED = "🧨";
export const EMPTY = "➖";

const NUMBER_EMOJI = ["➖", "1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣"];

export function createGame(chatId, messageId = null) {
  return {
    chatId: String(chatId),
    messageId,
    mode: "bomb",
    status: "ready",
    mines: null,
    counts: null,
    revealed: [],
    flags: [],
    exploded: null,
    startedAt: null,
  };
}

export function neighbors(index) {
  const row = Math.floor(index / SIZE);
  const col = index % SIZE;
  const result = [];

  for (let dr = -1; dr <= 1; dr += 1) {
    for (let dc = -1; dc <= 1; dc += 1) {
      if (dr === 0 && dc === 0) continue;

      const nextRow = row + dr;
      const nextCol = col + dc;
      if (nextRow >= 0 && nextRow < SIZE && nextCol >= 0 && nextCol < SIZE) {
        result.push(nextRow * SIZE + nextCol);
      }
    }
  }

  return result;
}

export function placeMines(firstClick, rng = Math.random) {
  const pool = [];
  for (let i = 0; i < TOTAL_CELLS; i += 1) {
    if (i !== firstClick) pool.push(i);
  }

  for (let i = 0; i < MINE_COUNT; i += 1) {
    const j = i + Math.floor(rng() * (pool.length - i));
    [pool[i], pool[j]] = [pool[j], pool[i]];
  }

  return pool.slice(0, MINE_COUNT);
}

export function computeCounts(mines) {
  const mineSet = new Set(mines);
  const counts = new Array(TOTAL_CELLS).fill(0);

  for (let i = 0; i < TOTAL_CELLS; i += 1) {
    if (mineSet.has(i)) continue;

    for (const neighbor of neighbors(i)) {
      if (mineSet.has(neighbor)) counts[i] += 1;
    }
  }

  return counts;
}

function revealFrom(game, start) {
  const queue = [start];
  const queued = new Set(queue);
  const revealed = new Set(game.revealed);
  const flags = new Set(game.flags);

  while (queue.length > 0) {
    const index = queue.shift();

    if (revealed.has(index) || flags.has(index)) continue;

    revealed.add(index);
    game.revealed.push(index);

    if (game.counts[index] !== 0) continue;

    for (const neighbor of neighbors(index)) {
      if (!revealed.has(neighbor) && !flags.has(neighbor) && !queued.has(neighbor)) {
        queued.add(neighbor);
        queue.push(neighbor);
      }
    }
  }
}

export function isWon(game) {
  return game.revealed.length === TOTAL_CELLS - MINE_COUNT;
}

export function openCell(game, index, rng = Math.random) {
  if (game.status === "won" || game.status === "lost") {
    return { result: "done" };
  }

  if (!Number.isInteger(index) || index < 0 || index >= TOTAL_CELLS) {
    return { result: "invalid" };
  }

  if (game.flags.includes(index)) {
    return { result: "flagged" };
  }

  if (game.revealed.includes(index)) {
    return { result: "already-opened" };
  }

  if (game.status === "ready") {
    game.mines = placeMines(index, rng);
    game.counts = computeCounts(game.mines);
    game.status = "playing";
    game.startedAt = Date.now();
  }

  if (game.mines.includes(index)) {
    game.status = "lost";
    game.exploded = index;
    return { result: "lost" };
  }

  revealFrom(game, index);

  if (isWon(game)) {
    game.status = "won";
    return { result: "won" };
  }

  return { result: "opened" };
}

export function toggleFlag(game, index) {
  if (game.status !== "ready" && game.status !== "playing") {
    return { result: "done" };
  }

  if (!Number.isInteger(index) || index < 0 || index >= TOTAL_CELLS) {
    return { result: "invalid" };
  }

  if (game.revealed.includes(index)) {
    return { result: "already-opened" };
  }

  const flagIndex = game.flags.indexOf(index);
  if (flagIndex === -1) {
    game.flags.push(index);
    return { result: "flagged" };
  }

  game.flags.splice(flagIndex, 1);
  return { result: "unflagged" };
}

export function renderCells(game) {
  const cells = new Array(TOTAL_CELLS);
  const revealed = new Set(game.revealed);
  const flags = new Set(game.flags);
  const mines = new Set(game.mines || []);

  for (let i = 0; i < TOTAL_CELLS; i += 1) {
    if (revealed.has(i)) {
      cells[i] = NUMBER_EMOJI[game.counts[i]] || EMPTY;
    } else if (game.status === "lost" && mines.has(i)) {
      cells[i] = i === game.exploded ? EXPLODED : MINE;
    } else if (game.status === "won" && mines.has(i)) {
      cells[i] = MINE;
    } else if (flags.has(i)) {
      cells[i] = FLAG;
    } else {
      cells[i] = HIDDEN;
    }
  }

  return cells;
}

export function minesLeft(flagCount) {
  const left = MINE_COUNT - flagCount;
  if (left < 0) {
    return `You have found ${Math.abs(left)} more mine(s) than possible`;
  }
  return String(left);
}

export function gameText(game) {
  if (game.status === "won") {
    const elapsed = ((Date.now() - game.startedAt) / 1000).toFixed(2);
    return `Minesweeper Game 🪖\n\nCongratulation!! You won the game 🥳\nElapsed time: ${elapsed}s`;
  }

  if (game.status === "lost") {
    return "Minesweeper Game 🪖\n\nYou lost the game. start new game with /start";
  }

  const mode = game.mode === "flag" ? "Flag mode 🚩" : "Mine mode 💣";
  return `Minesweeper Game 🪖\n\nMines left: ${minesLeft(game.flags.length)}\nCurrent state: ${mode}`;
}

export function buildKeyboard(game) {
  const cells = renderCells(game);
  const inlineKeyboard = [];
  const finished = game.status === "won" || game.status === "lost";

  for (let row = 0; row < SIZE; row += 1) {
    const buttons = [];
    for (let col = 0; col < SIZE; col += 1) {
      const index = row * SIZE + col;
      buttons.push({
        text: cells[index],
        callback_data: finished ? "done" : String(index + 1),
      });
    }
    inlineKeyboard.push(buttons);
  }

  if (!finished) {
    inlineKeyboard.push([
      { text: MINE, callback_data: "bomb" },
      { text: FLAG, callback_data: "flag" },
    ]);
  }

  return { inline_keyboard: inlineKeyboard };
}
