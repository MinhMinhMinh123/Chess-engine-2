import chess

from .strategies.search import search_level2, search_MVP


def find_best_move(
    board: chess.Board,
    time_limit_ms: int,
    brain: str,
) -> chess.Move:
    if brain == "MVP":
        return search_MVP.find_best_move(board, time_limit_ms)
    if brain == "level2":
        return search_level2.find_best_move(board, time_limit_ms)
    raise ValueError(f"Unknown search brain: {brain}")
