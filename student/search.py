import chess

from .strategies.search import search_MVP, search_v2


def find_best_move(
    board: chess.Board,
    soft_ms: int,
    hard_ms: int,
    brain: dict[str, str],
) -> chess.Move:
    """soft_ms: time the search should use; hard_ms: time it must never exceed."""
    search_brain = brain["search"]
    eval_brain = brain["eval"]
    if search_brain == "MVP":
        return search_MVP.find_best_move(board, soft_ms, eval_brain)
    if search_brain == "v2":
        return search_v2.find_best_move(board, soft_ms, hard_ms, eval_brain)
    raise ValueError(f"Unknown search brain: {search_brain}")
