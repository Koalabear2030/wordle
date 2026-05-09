#!/usr/bin/env python3
"""Terminal Wordle — 6 guesses, daily word seeded by date."""

import sys
import datetime
from words import ANSWERS, VALID_GUESSES

# ANSI color codes
GREEN  = "\033[42m\033[30m"
YELLOW = "\033[43m\033[30m"
GRAY   = "\033[100m\033[37m"
RESET  = "\033[0m"
BOLD   = "\033[1m"
DIM    = "\033[2m"

MAX_GUESSES = 6
WORD_LEN = 5


def pick_word() -> str:
    """Pick today's word, cycling through ANSWERS list by date."""
    origin = datetime.date(2024, 1, 1)
    delta = (datetime.date.today() - origin).days
    return ANSWERS[delta % len(ANSWERS)]


def score_guess(guess: str, answer: str) -> list[str]:
    """
    Return a list of 'green', 'yellow', or 'gray' for each letter.
    Handles duplicate letters correctly.
    """
    result = ["gray"] * WORD_LEN
    answer_pool = list(answer)

    # First pass: greens
    for i, (g, a) in enumerate(zip(guess, answer)):
        if g == a:
            result[i] = "green"
            answer_pool[i] = None  # consumed

    # Second pass: yellows
    for i, g in enumerate(guess):
        if result[i] == "green":
            continue
        if g in answer_pool:
            result[i] = "yellow"
            answer_pool[answer_pool.index(g)] = None

    return result


def render_row(guess: str, colors: list[str]) -> str:
    color_map = {"green": GREEN, "yellow": YELLOW, "gray": GRAY}
    cells = []
    for letter, color in zip(guess, colors):
        cells.append(f"{color_map[color]} {letter.upper()} {RESET}")
    return " ".join(cells)


def render_empty_row() -> str:
    return " ".join(f"{DIM}[ ]{RESET}" for _ in range(WORD_LEN))


def render_keyboard(used: dict[str, str]) -> str:
    rows = ["qwertyuiop", "asdfghjkl", "zxcvbnm"]
    color_map = {"green": GREEN, "yellow": YELLOW, "gray": GRAY}
    lines = []
    for row in rows:
        parts = []
        for ch in row:
            state = used.get(ch)
            if state:
                parts.append(f"{color_map[state]}{ch.upper()}{RESET}")
            else:
                parts.append(ch.upper())
        lines.append("  ".join(parts))
    return "\n".join(lines)


def update_keyboard(used: dict[str, str], guess: str, colors: list[str]):
    priority = {"green": 3, "yellow": 2, "gray": 1}
    for letter, color in zip(guess, colors):
        current = used.get(letter)
        if current is None or priority[color] > priority[current]:
            used[letter] = color


def clear_screen():
    print("\033[2J\033[H", end="")


def print_board(guesses: list[tuple[str, list[str]]], num_guesses: int, used: dict[str, str]):
    clear_screen()
    print(f"\n  {BOLD}WORDLE{RESET}  —  {datetime.date.today()}\n")

    for i in range(MAX_GUESSES):
        if i < len(guesses):
            guess, colors = guesses[i]
            print("  " + render_row(guess, colors))
        else:
            print("  " + render_empty_row())

    print(f"\n{render_keyboard(used)}\n")


def get_guess(attempt: int, valid: set[str]) -> str:
    while True:
        try:
            raw = input(f"  Guess {attempt}/{MAX_GUESSES}: ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            print("\n  Goodbye!")
            sys.exit(0)

        if len(raw) != WORD_LEN:
            print(f"  Please enter a {WORD_LEN}-letter word.")
            continue
        if raw not in valid:
            print(f"  '{raw}' is not in the word list. Try again.")
            continue
        return raw


def play():
    answer = pick_word()
    guesses: list[tuple[str, list[str]]] = []
    used: dict[str, str] = {}

    print_board(guesses, 0, used)

    for attempt in range(1, MAX_GUESSES + 1):
        guess = get_guess(attempt, VALID_GUESSES)
        colors = score_guess(guess, answer)
        guesses.append((guess, colors))
        update_keyboard(used, guess, colors)
        print_board(guesses, attempt, used)

        if guess == answer:
            msgs = ["Genius!", "Magnificent!", "Impressive!", "Splendid!", "Great!", "Phew!"]
            print(f"  {BOLD}{msgs[attempt - 1]}{RESET}  You got it in {attempt}!\n")
            return

    print(f"  Better luck tomorrow! The word was {BOLD}{answer.upper()}{RESET}.\n")


if __name__ == "__main__":
    play()
