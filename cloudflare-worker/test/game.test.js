import test from "node:test";
import assert from "node:assert/strict";

import {
  HIDDEN,
  MINE_COUNT,
  TOTAL_CELLS,
  buildKeyboard,
  computeCounts,
  createGame,
  gameText,
  openCell,
  placeMines,
  renderCells,
  toggleFlag,
} from "../src/game.js";

test("a new game starts hidden and in mine mode", () => {
  const game = createGame(123);
  const cells = renderCells(game);

  assert.equal(game.status, "ready");
  assert.equal(game.mode, "bomb");
  assert.equal(cells.length, TOTAL_CELLS);
  assert.ok(cells.every((cell) => cell === HIDDEN));
  assert.match(gameText(game), /Mine mode/);
});

test("the first click is always safe and places ten mines", () => {
  for (let run = 0; run < 100; run += 1) {
    const firstClick = run % TOTAL_CELLS;
    const game = createGame(1);

    openCell(game, firstClick);

    assert.equal(game.mines.length, MINE_COUNT);
    assert.ok(!game.mines.includes(firstClick));
    assert.ok(game.revealed.includes(firstClick));
    assert.notEqual(game.status, "lost");
  }
});

test("mine counts match the number of adjacent mines", () => {
  const mines = [0, 1, 2, 3, 4, 5, 6, 7];
  const counts = computeCounts(mines);

  assert.equal(counts[8], 2);
  assert.equal(counts[9], 3);
  assert.equal(counts[63], 0);
});

test("flags can be added and removed, and block opening", () => {
  const game = createGame(1);
  const index = 9;

  assert.equal(toggleFlag(game, index).result, "flagged");
  assert.deepEqual(game.flags, [index]);
  assert.equal(openCell(game, index).result, "flagged");

  assert.equal(toggleFlag(game, index).result, "unflagged");
  assert.deepEqual(game.flags, []);
});

test("opening a safe area reveals cells until numbers are reached", () => {
  const game = createGame(1);
  const mines = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9];

  game.mines = mines;
  game.counts = computeCounts(mines);
  game.status = "playing";
  game.startedAt = Date.now();

  const result = openCell(game, 63);

  assert.equal(result.result, "won");
  assert.equal(game.status, "won");
  assert.equal(game.revealed.length, TOTAL_CELLS - MINE_COUNT);
  assert.match(gameText(game), /won the game/);
});

test("clicking a mine loses the game and shows the board", () => {
  const game = createGame(1);
  const mines = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9];

  game.mines = mines;
  game.counts = computeCounts(mines);
  game.status = "playing";
  game.startedAt = Date.now();

  assert.equal(openCell(game, 0).result, "lost");
  assert.equal(game.status, "lost");
  assert.equal(game.exploded, 0);

  const cells = renderCells(game);
  assert.equal(cells[0], "🧨");
  assert.equal(cells[1], "💣");
});

test("the finished keyboard disables every cell", () => {
  const game = createGame(1);
  game.status = "lost";

  const keyboard = buildKeyboard(game).inline_keyboard;
  const buttons = keyboard.flat();

  assert.equal(keyboard.length, 8);
  assert.ok(buttons.every((button) => button.callback_data === "done"));
});

test("placeMines ignores the first click", () => {
  const mines = placeMines(31, () => 0.5);

  assert.equal(mines.length, MINE_COUNT);
  assert.ok(!mines.includes(31));
});
