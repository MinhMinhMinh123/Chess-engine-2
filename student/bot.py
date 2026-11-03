import chess

from chesslab_sdk import BotConfig, SearchContext
from .search import find_best_move
from .time_manager import allocate_time_window


class StudentBot:
    """The only class imported by the local runner and official grader."""

    def __init__(self, config: BotConfig) -> None:
        self.config = config
        self.brain = "level2"

    def choose_move(self, board: chess.Board, context: SearchContext) -> chess.Move:
        legal_moves = list(board.legal_moves)
        try:
            soft_ms, hard_ms = allocate_time_window(context)
            move = find_best_move(board, soft_ms, hard_ms, self.brain)
            if move in legal_moves:
                return move
        except Exception:
            pass
        # Never crash and never return an illegal move: that loses the game.
        return legal_moves[0]
