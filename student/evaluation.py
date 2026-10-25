import chess

from .strategies.evaluation import eval_MVP


def evaluate_board(board: chess.Board, brain: str) -> float:
    if brain == "MVP":
        return eval_MVP.evaluate_board(board)
    raise ValueError(f"Unknown evaluation brain: {brain}")
