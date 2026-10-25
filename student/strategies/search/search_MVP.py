import chess

from ...evaluation import evaluate_board


def find_best_move(board: chess.Board, time_limit_ms: int) -> chess.Move:
    legal_moves: list[chess.Move] = list(board.legal_moves)
    best_move: chess.Move | None = None
    best_score: float = float("-inf")
    depth: int = 1
    ...
