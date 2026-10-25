import chess

from chesslab_sdk import BotConfig, SearchContext
from .search import find_best_move
from .time_manager import allocate_time


class StudentBot:
    """The only class imported by the local runner and official grader."""

    def __init__(self, config: BotConfig) -> None:
        self.config = config

    def choose_move(self, board: chess.Board, context: SearchContext) -> chess.Move:
        time_limit_ms = allocate_time(context)
        return find_best_move(board, time_limit_ms)