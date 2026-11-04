import chess

from .pawn_structure import evaluate_pawn_structure
from .pst import (
    KING_EG,
    KING_MG,
    PHASE_WEIGHTS,
    PIECE_VALUES_EG,
    PIECE_VALUES_MG,
    TABLES_EG,
    TABLES_MG,
    TOTAL_PHASE,
)

# HẰNG SỐ ĐẶC THÙ CHO KHAI CUỘC 960 & MOP-UP TÀN CUỘC

CASTLING_RIGHT_BONUS = 25       # Thưởng cho mỗi cánh còn quyền nhập thành
MINOR_DEV_BONUS = 15            # Thưởng mỗi Mã/Tượng rời hàng đáy tham chiến
EARLY_QUEEN_PENALTY = 25        # Phạt xuất Hậu khi các quân nhẹ chưa phát triển


def _mop_up_eval(winning_king: int, losing_king: int) -> int:
    """Tính điểm dồn ép Vua ở cờ tàn:
    1. Đẩy Vua địch ra xa trung tâm (sát mép hoặc góc bàn cờ).
    2. Kéo Vua mình lại gần Vua địch để che chắn và chiếu hết.
    """
    # 1. Khoảng cách của Vua thua cuộc tới trung tâm (Manhattan distance tới 4 ô trung tâm: 0 -> 6)
    los_f = chess.square_file(losing_king)     # Cột của Vua địch (0..7: từ cột a -> h)
    los_r = chess.square_rank(losing_king)     # Hàng của Vua địch (0..7: từ hàng 1 -> 8)
    center_dist = max(3 - los_f, los_f - 4) + max(3 - los_r, los_r - 4)    # Khoảng cách Manhattan từ Vua thua cuộc tới 4 ô trung tâm. Giá trị nhỏ (0-6) nghĩa là Vua gần trung tâm, lớn là ở rìa/góc.

    # 2. Khoảng cách giữa 2 Vua (Chebyshev distance: 1 -> 7)
    win_f = chess.square_file(winning_king)    # Cột của Vua thắng (0..7: từ cột a -> h)
    win_r = chess.square_rank(winning_king)    # Hàng của Vua thắng (0..7: từ hàng 1 -> 8)
    kings_dist = max(abs(win_f - los_f), abs(win_r - los_r))    # Khoảng cách Chebyshev (tối đa bước đi của Vua) giữa 2 Vua. Giá trị nhỏ (1-2) nghĩa là 2 Vua rất gần nhau, lớn là ở xa nhau.

    return center_dist * 15 + (7 - kings_dist) * 10


def evaluate_board(board: chess.Board) -> float:
    """Lượng giá thế cờ toàn diện v3:
    - Tapered + PST thủ công
    - Bitboard Cached Pawn Structure (Tốt thông, chồng, cô lập, liên kết)
    - Đặc thù khai cuộc Chess960 (Nhập thành, phát triển quân nhẹ, tránh xuất Hậu sớm)
    - Mop-up tàn cuộc và nhận diện hòa lý thuyết
    - Chuẩn Negamax
    """
    # 1. NHẬN DIỆN HÒA LÝ THUYẾT (Thiếu quân chiếu hết: K vs K, K+N vs K, K+B vs K)
    if board.is_insufficient_material():
        return 0.0

    mg_white = 0
    mg_black = 0
    eg_white = 0
    eg_black = 0
    game_phase = 0

    # 2. QUÉT 5 LOẠI QUÂN THÔNG THƯỜNG
    white_minors_on_back_rank = 0
    black_minors_on_back_rank = 0

    for piece_type in (chess.PAWN, chess.KNIGHT, chess.BISHOP, chess.ROOK, chess.QUEEN):
        val_mg = PIECE_VALUES_MG[piece_type]
        val_eg = PIECE_VALUES_EG[piece_type]
        tbl_mg = TABLES_MG[piece_type]
        tbl_eg = TABLES_EG[piece_type]

        if piece_type in PHASE_WEIGHTS:
            count = len(board.pieces(piece_type, chess.WHITE)) + len(board.pieces(piece_type, chess.BLACK))
            game_phase += count * PHASE_WEIGHTS[piece_type]

        # Quân Trắng
        for sq in board.pieces(piece_type, chess.WHITE):
            mg_white += val_mg + tbl_mg[sq]
            eg_white += val_eg + tbl_eg[sq]

            # Kiểm tra phát triển quân nhẹ ở khai cuộc (Mã, Tượng)
            if piece_type in (chess.KNIGHT, chess.BISHOP):
                if chess.square_rank(sq) == 0:  # Đang nằm ở hàng đáy (hàng 1)
                    white_minors_on_back_rank += 1
                else:
                    mg_white += MINOR_DEV_BONUS  # Thưởng rời hàng đáy tham chiến

        # Quân Đen (lật gương ô cờ qua trục ngang)
        for sq in board.pieces(piece_type, chess.BLACK):
            mirror_sq = chess.square_mirror(sq)
            mg_black += val_mg + tbl_mg[mirror_sq]
            eg_black += val_eg + tbl_eg[mirror_sq]

            # Kiểm tra phát triển quân nhẹ Đen
            if piece_type in (chess.KNIGHT, chess.BISHOP):
                if chess.square_rank(sq) == 7:  # Đang nằm ở hàng đáy (hàng 8)
                    black_minors_on_back_rank += 1
                else:
                    mg_black += MINOR_DEV_BONUS

    # 3. QUÂN VUA (PST)
    king_white = board.king(chess.WHITE)
    if king_white is not None:
        mg_white += KING_MG[king_white]
        eg_white += KING_EG[king_white]

    king_black = board.king(chess.BLACK)
    if king_black is not None:
        mirror_kb = chess.square_mirror(king_black)
        mg_black += KING_MG[mirror_kb]
        eg_black += KING_EG[mirror_kb]

    # 4. ĐẶC THÙ KHAI CUỘC CHESS960 (Chỉ áp dụng khi còn nhiều quân: game_phase >= 18)
    if game_phase >= 18:
        # A. Quyền nhập thành
        if board.has_kingside_castling_rights(chess.WHITE):
            mg_white += CASTLING_RIGHT_BONUS
        if board.has_queenside_castling_rights(chess.WHITE):
            mg_white += CASTLING_RIGHT_BONUS

        if board.has_kingside_castling_rights(chess.BLACK):
            mg_black += CASTLING_RIGHT_BONUS
        if board.has_queenside_castling_rights(chess.BLACK):
            mg_black += CASTLING_RIGHT_BONUS

        # B. Phạt xuất Hậu quá sớm nếu quân nhẹ còn ùn tắc ở hàng đáy
        for sq in board.pieces(chess.QUEEN, chess.WHITE):
            if chess.square_rank(sq) > 0 and white_minors_on_back_rank >= 3:
                mg_white -= EARLY_QUEEN_PENALTY

        for sq in board.pieces(chess.QUEEN, chess.BLACK):
            if chess.square_rank(sq) < 7 and black_minors_on_back_rank >= 3:
                mg_black -= EARLY_QUEEN_PENALTY

    # 5. CẤU TRÚC TỐT (BITBOARD MASKS & CACHE)
    pawn_mg_diff, pawn_eg_diff = evaluate_pawn_structure(board)
    mg_score = (mg_white - mg_black) + pawn_mg_diff
    eg_score = (eg_white - eg_black) + pawn_eg_diff

    # 6. MOP-UP TÀN CUỘC (Chỉ kích hoạt khi phase <= 4 và một bên có ưu thế vật chất >= 200cp)
    phase = min(game_phase, TOTAL_PHASE)
    if phase <= 4 and king_white is not None and king_black is not None:
        if eg_score >= 200:
            eg_score += _mop_up_eval(winning_king=king_white, losing_king=king_black)
        elif eg_score <= -200:
            eg_score -= _mop_up_eval(winning_king=king_black, losing_king=king_white)

    # 7. NỘI SUY TAPERED THEO GIAI ĐOẠN VÁN CỜ
    total_score = (mg_score * phase + eg_score * (TOTAL_PHASE - phase)) / TOTAL_PHASE

    # 8. CHUẨN NEGAMAX
    return total_score if board.turn == chess.WHITE else -total_score
