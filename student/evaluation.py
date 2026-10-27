import chess

from .strategies.evaluation import eval_MVP, eval_v2


def evaluate_board(board: chess.Board, brain: str) -> float:
    if brain == "MVP":
        return eval_MVP.evaluate_board(board)
    if brain in ("v2", "tapered"):
        return eval_v2.evaluate_board(board)
    raise ValueError(f"Unknown evaluation brain: {brain}")
