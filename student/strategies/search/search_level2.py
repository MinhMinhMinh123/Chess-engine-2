"""Level 2 search: MVP search plus PVS, transposition table, quiescence,
null-move pruning, late move reduction, reverse futility pruning, SEE,
check extension and killer/history move ordering.

The evaluation function must return a score in centipawns from the point of
view of the side to move (positive = good for the side to move).
"""

import time

import chess

from ...evaluation import evaluate_board

BRAIN = "v2"

MATE_SCORE = 100_000
MATE_THRESHOLD = MATE_SCORE - 1_000
DRAW_SCORE = 0
INFINITY = MATE_SCORE + 1

MAX_DEPTH = 64
MAX_PLY = 128
CHECK_EVERY_NODES = 256
MIN_TIME_MS = 10

TT_MAX_ENTRIES = 300_000
NULL_MOVE_REDUCTION = 2
RFP_MAX_DEPTH = 3
RFP_MARGIN = 120
LMR_MIN_DEPTH = 3
LMR_MIN_MOVE_INDEX = 3
DELTA_MARGIN = 200

EXACT, LOWER_BOUND, UPPER_BOUND = 0, 1, 2

# Only used for move ordering, SEE and delta pruning, not for evaluation.
ORDER_VALUES = {
    chess.PAWN: 100,
    chess.KNIGHT: 320,
    chess.BISHOP: 330,
    chess.ROOK: 500,
    chess.QUEEN: 900,
    chess.KING: 20_000,
}

TT_MOVE_BONUS = 10_000_000
GOOD_CAPTURE_BONUS = 1_000_000
PROMOTION_BONUS = 900_000
KILLER_BONUS = 800_000
HISTORY_MAX = 700_000
BAD_CAPTURE_PENALTY = -1_000_000

# Kept between moves of the same game: key -> (depth, score, flag, move, generation).
_tt: dict[int, tuple[int, float, int, chess.Move | None, int]] = {}
_generation = 0


class SearchTimeout(Exception):
    pass


def _victim_type(board: chess.Board, move: chess.Move) -> chess.PieceType:
    if board.is_en_passant(move):
        return chess.PAWN
    return board.piece_type_at(move.to_square) or chess.PAWN


def _mvv_lva(board: chess.Board, move: chess.Move) -> int:
    attacker = board.piece_type_at(move.from_square) or chess.PAWN
    return 10 * ORDER_VALUES[_victim_type(board, move)] - ORDER_VALUES[attacker]


def see(board: chess.Board, move: chess.Move) -> int:
    """Static exchange evaluation: material won by ``move`` if both sides keep
    recapturing on the target square with their least valuable attacker."""
    to_square = move.to_square
    occupied = board.occupied ^ chess.BB_SQUARES[move.from_square]
    if board.is_en_passant(move):
        occupied ^= chess.BB_SQUARES[to_square + (-8 if board.turn == chess.WHITE else 8)]
        gains = [ORDER_VALUES[chess.PAWN]]
    else:
        victim = board.piece_type_at(to_square)
        gains = [ORDER_VALUES[victim] if victim else 0]

    on_square = board.piece_type_at(move.from_square) or chess.PAWN
    if move.promotion:
        gains[0] += ORDER_VALUES[move.promotion] - ORDER_VALUES[chess.PAWN]
        on_square = move.promotion

    side = not board.turn
    while True:
        attackers = board.attackers_mask(side, to_square, occupied) & occupied
        if not attackers:
            break
        for piece_type in (chess.PAWN, chess.KNIGHT, chess.BISHOP, chess.ROOK, chess.QUEEN, chess.KING):
            candidates = attackers & board.pieces_mask(piece_type, side)
            if candidates:
                break
        square = chess.lsb(candidates)
        if piece_type == chess.KING:
            # The king may only recapture if the square is no longer defended.
            if board.attackers_mask(not side, to_square, occupied ^ chess.BB_SQUARES[square]) & occupied:
                break
        gains.append(ORDER_VALUES[on_square] - gains[-1])
        on_square = piece_type
        occupied ^= chess.BB_SQUARES[square]
        side = not side

    for index in range(len(gains) - 1, 0, -1):
        gains[index - 1] = -max(-gains[index - 1], gains[index])
    return gains[0]


def sort_moves(
    board: chess.Board,
    moves: list[chess.Move],
    tt_move: chess.Move | None = None,
    killers: list[chess.Move | None] | None = None,
    history: dict[tuple[bool, int, int], int] | None = None,
) -> list[chess.Move]:
    """Order moves: TT move, winning/equal captures (MVV-LVA), promotions,
    killers, history, and losing captures (negative SEE) last."""

    def score(move: chess.Move) -> int:
        if move == tt_move:
            return TT_MOVE_BONUS
        if board.is_capture(move):
            attacker = board.piece_type_at(move.from_square) or chess.PAWN
            victim = _victim_type(board, move)
            # A capture of an equal or bigger piece can never lose material.
            if ORDER_VALUES[attacker] > ORDER_VALUES[victim] and see(board, move) < 0:
                return BAD_CAPTURE_PENALTY + _mvv_lva(board, move)
            return GOOD_CAPTURE_BONUS + _mvv_lva(board, move)
        if move.promotion:
            return PROMOTION_BONUS + ORDER_VALUES[move.promotion]
        if killers and move in killers:
            return KILLER_BONUS
        if history:
            return min(HISTORY_MAX, history.get((board.turn, move.from_square, move.to_square), 0))
        return 0

    return sorted(moves, key=score, reverse=True)


def _score_to_tt(score: float, ply: int) -> float:
    # Mate scores are stored relative to the node, not to the root.
    if score >= MATE_THRESHOLD:
        return score + ply
    if score <= -MATE_THRESHOLD:
        return score - ply
    return score


def _score_from_tt(score: float, ply: int) -> float:
    if score >= MATE_THRESHOLD:
        return score - ply
    if score <= -MATE_THRESHOLD:
        return score + ply
    return score


def _has_non_pawn_material(board: chess.Board) -> bool:
    us = board.occupied_co[board.turn]
    pieces = board.knights | board.bishops | board.rooks | board.queens
    return bool(us & pieces)


def _position_key(board: chess.Board) -> int:
    return hash(board._transposition_key())


def _make_room_in_tt() -> None:
    """Drop entries from earlier moves first, then shallow ones, then everything."""
    global _tt
    _tt = {key: entry for key, entry in _tt.items() if entry[4] == _generation}
    if len(_tt) >= TT_MAX_ENTRIES:
        _tt = {key: entry for key, entry in _tt.items() if entry[0] > 1}
    if len(_tt) >= TT_MAX_ENTRIES:
        _tt.clear()


def _store_tt(key: int, depth: int, score: float, flag: int, move: chess.Move | None) -> None:
    old = _tt.get(key)
    if old is None:
        if len(_tt) >= TT_MAX_ENTRIES:
            _make_room_in_tt()
    elif old[4] == _generation and depth < old[0] and flag != EXACT:
        # Keep the deeper entry of this move; a stale or shallower one is replaced.
        return
    _tt[key] = (depth, score, flag, move, _generation)


class Searcher:
    def __init__(self, time_limit_ms: int) -> None:
        self.start = time.perf_counter()
        self.time_limit_s = max(MIN_TIME_MS, int(time_limit_ms or 0)) / 1000
        self.deadline = self.start + self.time_limit_s
        self.nodes = 0
        self.killers: list[list[chess.Move | None]] = [[None, None] for _ in range(MAX_PLY + 1)]
        self.history: dict[tuple[bool, int, int], int] = {}
        # Keys of the positions leading to the current node (None = null move barrier).
        self.keys: list[int | None] = []

    def elapsed(self) -> float:
        return time.perf_counter() - self.start

    def _tick(self) -> None:
        self.nodes += 1
        if self.nodes % CHECK_EVERY_NODES == 0 and time.perf_counter() >= self.deadline:
            raise SearchTimeout

    def _evaluate(self, board: chess.Board) -> float:
        return evaluate_board(board, BRAIN)

    def _load_game_history(self, board: chess.Board) -> None:
        """Collect the keys of earlier positions that can still be repeated."""
        history = board.copy()
        keys: list[int] = []
        while history.move_stack and len(keys) < board.halfmove_clock:
            history.pop()
            keys.append(_position_key(history))
        self.keys = list(reversed(keys))

    def _is_repetition(self, key: int, halfmove_clock: int) -> bool:
        # Only positions with the same side to move and no irreversible move since.
        oldest = max(0, len(self.keys) - halfmove_clock)
        for index in range(len(self.keys) - 1, oldest - 1, -1):
            previous = self.keys[index]
            if previous is None:
                return False
            if (len(self.keys) - index) % 2 == 0 and previous == key:
                return True
        return False

    def search(self, board: chess.Board) -> chess.Move:
        global _generation
        _generation += 1
        self._load_game_history(board)

        root_moves = list(board.legal_moves)
        if len(root_moves) == 1:
            return root_moves[0]
        entry = _tt.get(_position_key(board))
        root_moves = sort_moves(board, root_moves, entry[3] if entry else None)
        best_move = root_moves[0]

        for depth in range(1, MAX_DEPTH + 1):
            try:
                scored = self._search_root(board, depth, root_moves)
            except SearchTimeout:
                break
            scored.sort(key=lambda item: item[1], reverse=True)
            best_move, best_score = scored[0]
            root_moves = [move for move, _ in scored]
            if abs(best_score) >= MATE_THRESHOLD:
                break
            # The next depth usually costs several times more than this one.
            if self.elapsed() >= self.time_limit_s / 2:
                break
        return best_move

    def _search_root(
        self,
        board: chess.Board,
        depth: int,
        root_moves: list[chess.Move],
    ) -> list[tuple[chess.Move, float]]:
        alpha = -INFINITY
        scored: list[tuple[chess.Move, float]] = []
        self.keys.append(_position_key(board))
        try:
            for index, move in enumerate(root_moves):
                board.push(move)
                try:
                    if index == 0:
                        score = -self._negamax(board, depth - 1, -INFINITY, -alpha, 1)
                    else:
                        # Principal variation search: try a null window first.
                        score = -self._negamax(board, depth - 1, -alpha - 1, -alpha, 1)
                        if score > alpha:
                            score = -self._negamax(board, depth - 1, -INFINITY, -alpha, 1)
                finally:
                    board.pop()
                scored.append((move, score))
                alpha = max(alpha, score)
        finally:
            self.keys.pop()
        return scored

    def _negamax(
        self,
        board: chess.Board,
        depth: int,
        alpha: float,
        beta: float,
        ply: int,
        allow_null: bool = True,
    ) -> float:
        self._tick()

        key = _position_key(board)
        if board.halfmove_clock >= 100 or self._is_repetition(key, board.halfmove_clock):
            return DRAW_SCORE
        if chess.popcount(board.occupied) <= 4 and board.is_insufficient_material():
            return DRAW_SCORE
        if ply >= MAX_PLY:
            return self._evaluate(board)

        # Mate distance pruning.
        alpha = max(alpha, -MATE_SCORE + ply)
        beta = min(beta, MATE_SCORE - ply - 1)
        if alpha >= beta:
            return alpha

        in_check = board.is_check()
        if in_check:
            depth += 1
        if depth <= 0:
            return self._quiescence(board, alpha, beta, ply)

        tt_move: chess.Move | None = None
        entry = _tt.get(key)
        if entry is not None:
            entry_depth, entry_score, entry_flag, tt_move, _ = entry
            if entry_depth >= depth:
                score = _score_from_tt(entry_score, ply)
                if entry_flag == EXACT:
                    return score
                if entry_flag == LOWER_BOUND and score >= beta:
                    return score
                if entry_flag == UPPER_BOUND and score <= alpha:
                    return score

        is_pv = beta - alpha > 1
        can_prune = not is_pv and not in_check and abs(beta) < MATE_THRESHOLD
        static_eval: float | None = None

        # Reverse futility pruning: far above beta near the leaves, assume a cutoff.
        if can_prune and depth <= RFP_MAX_DEPTH:
            static_eval = self._evaluate(board)
            if static_eval - RFP_MARGIN * depth >= beta:
                return static_eval

        # Null move pruning. Skipped when the side to move has only king and pawns,
        # because zugzwang is common there and passing would be a lie.
        if allow_null and can_prune and depth >= 3 and _has_non_pawn_material(board):
            if static_eval is None:
                static_eval = self._evaluate(board)
            if static_eval >= beta:
                board.push(chess.Move.null())
                self.keys.append(None)
                try:
                    score = -self._negamax(
                        board, depth - 1 - NULL_MOVE_REDUCTION, -beta, -beta + 1, ply + 1, False
                    )
                finally:
                    self.keys.pop()
                    board.pop()
                if score >= beta:
                    return beta

        moves = list(board.legal_moves)
        if not moves:
            return -MATE_SCORE + ply if in_check else DRAW_SCORE

        killers = self.killers[ply]
        ordered = sort_moves(board, moves, tt_move, killers, self.history)

        alpha_orig = alpha
        best_score = -INFINITY
        best_move: chess.Move | None = None
        self.keys.append(key)
        try:
            for index, move in enumerate(ordered):
                is_quiet = not board.is_capture(move) and not move.promotion
                board.push(move)
                try:
                    if index == 0:
                        score = -self._negamax(board, depth - 1, -beta, -alpha, ply + 1)
                    else:
                        # Late move reduction: quiet moves ordered late are rarely best,
                        # so search them shallower first and re-search if they surprise.
                        reduction = 0
                        if (
                            depth >= LMR_MIN_DEPTH
                            and index >= LMR_MIN_MOVE_INDEX
                            and is_quiet
                            and not in_check
                            and move not in killers
                            and not board.is_check()
                        ):
                            reduction = 1 if index < 6 else 2
                            reduction = min(reduction, depth - 2)
                        score = -self._negamax(
                            board, depth - 1 - reduction, -alpha - 1, -alpha, ply + 1
                        )
                        if reduction and score > alpha:
                            score = -self._negamax(board, depth - 1, -alpha - 1, -alpha, ply + 1)
                        if alpha < score < beta:
                            score = -self._negamax(board, depth - 1, -beta, -alpha, ply + 1)
                finally:
                    board.pop()

                if score > best_score:
                    best_score = score
                    best_move = move
                if score > alpha:
                    alpha = score
                if alpha >= beta:
                    if is_quiet:
                        if killers[0] != move:
                            killers[1] = killers[0]
                            killers[0] = move
                        history_key = (board.turn, move.from_square, move.to_square)
                        self.history[history_key] = self.history.get(history_key, 0) + depth * depth
                    break
        finally:
            self.keys.pop()

        if best_score <= alpha_orig:
            flag = UPPER_BOUND
        elif best_score >= beta:
            flag = LOWER_BOUND
        else:
            flag = EXACT
        _store_tt(key, depth, _score_to_tt(best_score, ply), flag, best_move)
        return best_score

    def _quiescence(self, board: chess.Board, alpha: float, beta: float, ply: int) -> float:
        """Search captures (and check evasions) until the position is quiet."""
        self._tick()

        if ply >= MAX_PLY:
            return self._evaluate(board)

        in_check = board.is_check()
        if in_check:
            moves = list(board.legal_moves)
            if not moves:
                return -MATE_SCORE + ply
            moves = sort_moves(board, moves)
            best_score = -INFINITY
        else:
            stand_pat = self._evaluate(board)
            if stand_pat >= beta:
                return stand_pat
            alpha = max(alpha, stand_pat)
            best_score = stand_pat
            moves = []
            for move in board.legal_moves:
                if move.promotion == chess.QUEEN:
                    moves.append(move)
                    continue
                if not board.is_capture(move):
                    continue
                # Delta pruning: even winning the victim for free cannot reach alpha.
                victim_value = ORDER_VALUES[_victim_type(board, move)]
                if stand_pat + victim_value + DELTA_MARGIN <= alpha:
                    continue
                # Skip captures that lose material in the exchange.
                if see(board, move) < 0:
                    continue
                moves.append(move)
            moves.sort(
                key=lambda move: _mvv_lva(board, move) if board.is_capture(move) else 0,
                reverse=True,
            )

        for move in moves:
            board.push(move)
            try:
                score = -self._quiescence(board, -beta, -alpha, ply + 1)
            finally:
                board.pop()
            if score > best_score:
                best_score = score
            if score > alpha:
                alpha = score
            if alpha >= beta:
                break
        return best_score


def find_best_move(board: chess.Board, time_limit_ms: int) -> chess.Move:
    """Return the best move found within ``time_limit_ms`` milliseconds.

    The search runs on a copy, so ``board`` is never modified. If time runs out,
    the best move of the last fully searched depth is returned.
    """
    if not any(board.legal_moves):
        raise ValueError("No legal moves in this position")
    return Searcher(time_limit_ms).search(board.copy())
