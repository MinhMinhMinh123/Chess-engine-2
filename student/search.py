import chess

from .strategies.search import search_level2, search_MVP


def find_best_move(
    board: chess.Board,
    soft_ms: int,
    hard_ms: int,
    brain: str,
) -> chess.Move:
    """soft_ms: time the search should use; hard_ms: time it must never exceed."""
    if brain == "MVP":
        return search_MVP.find_best_move(board, soft_ms)
    if brain == "level2":
        return search_level2.find_best_move(board, soft_ms, hard_ms)
    raise ValueError(f"Unknown search brain: {brain}")
