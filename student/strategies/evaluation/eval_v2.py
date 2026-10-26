# V2 sử dụng Piece-Square Tables (PST) và Tapered Evaluation

import chess



# 1. GIÁ TRỊ VẬT CHẤT CHO 2 GIAI ĐOẠN (MG: Trung cuộc, EG: Tàn cuộc)

PIECE_VALUES_MG: dict[chess.PieceType, int] = {
    chess.PAWN: 100,
    chess.KNIGHT: 320,
    chess.BISHOP: 330,
    chess.ROOK: 500,
    chess.QUEEN: 900,
}

PIECE_VALUES_EG: dict[chess.PieceType, int] = {
    chess.PAWN: 130,   # Tốt mạnh hơn ở tàn cuộc vì có thể phong cấp
    chess.KNIGHT: 280, # Mã giảm sức mạnh khi thế cờ mở
    chess.BISHOP: 340, # Tượng mạnh hơn khi các đường chéo thông thoáng
    chess.ROOK: 550,
    chess.QUEEN: 950,
}

# Trọng số tính Phase ván cờ 
PHASE_WEIGHTS: dict[chess.PieceType, int] = {  # Cái này để xác định thời điểm chuyển từ trung cuộc sang tàn cuộc
    chess.KNIGHT: 1,
    chess.BISHOP: 1,
    chess.ROOK: 2,
    chess.QUEEN: 4,
}
TOTAL_PHASE = 24


# 2. BẢNG ĐIỂM VỊ TRÍ (PST) CHO TỪNG LOẠI QUÂN


def _flip(table: list[int]) -> list[int]:
    #Chuyển đổi bảng nhìn trực quan từ hàng 8->1 sang chỉ số 0..63 của python-chess để tránh nhầm lẫn index khi gọi table() (a1->h8)
    res: list[int] = []
    for rank in range(7, -1, -1):
        res.extend(table[rank * 8 : (rank + 1) * 8])
    return res

# --- TỐT (Pawn) ---
PAWN_MG = _flip([
     0,  0,  0,  0,  0,  0,  0,  0,
    50, 50, 50, 50, 50, 50, 50, 50,
    10, 10, 20, 30, 30, 20, 10, 10,
     5,  5, 10, 25, 25, 10,  5,  5,
     0,  0,  0, 20, 20,  0,  0,  0,
     5, -5,-10,  0,  0,-10, -5,  5,
     5, 10, 10,-20,-20, 10, 10,  5,
     0,  0,  0,  0,  0,  0,  0,  0,
])
PAWN_EG = _flip([
     0,  0,  0,  0,  0,  0,  0,  0,
    90, 90, 90, 90, 90, 90, 90, 90,
    50, 50, 50, 50, 50, 50, 50, 50,
    30, 30, 30, 30, 30, 30, 30, 30,
    20, 20, 20, 20, 20, 20, 20, 20,
    10, 10, 10, 10, 10, 10, 10, 10,
     0,  0,  0,  0,  0,  0,  0,  0,
     0,  0,  0,  0,  0,  0,  0,  0,
])

# --- MÃ (Knight) ---
KNIGHT_MG = _flip([
    -50,-40,-30,-30,-30,-30,-40,-50,
    -40,-20,  0,  0,  0,  0,-20,-40,
    -30,  0, 10, 15, 15, 10,  0,-30,
    -30,  5, 15, 20, 20, 15,  5,-30,
    -30,  0, 15, 20, 20, 15,  0,-30,
    -30,  5, 10, 15, 15, 10,  5,-30,
    -40,-20,  0,  5,  5,  0,-20,-40,
    -50,-40,-30,-30,-30,-30,-40,-50,
])
KNIGHT_EG = KNIGHT_MG

# --- TƯỢNG (Bishop) ---
BISHOP_MG = _flip([
    -20,-10,-10,-10,-10,-10,-10,-20,
    -10,  0,  0,  0,  0,  0,  0,-10,
    -10,  0,  5, 10, 10,  5,  0,-10,
    -10,  5,  5, 10, 10,  5,  5,-10,
    -10,  0, 10, 10, 10, 10,  0,-10,
    -10, 10, 10, 10, 10, 10, 10,-10,
    -10,  5,  0,  0,  0,  0,  5,-10,
    -20,-10,-10,-10,-10,-10,-10,-20,
])
BISHOP_EG = BISHOP_MG

# --- XE (Rook) ---
ROOK_MG = _flip([
      0,  0,  0,  0,  0,  0,  0,  0,
      5, 10, 10, 10, 10, 10, 10,  5,
     -5,  0,  0,  0,  0,  0,  0, -5,
     -5,  0,  0,  0,  0,  0,  0, -5,
     -5,  0,  0,  0,  0,  0,  0, -5,
     -5,  0,  0,  0,  0,  0,  0, -5,
     -5,  0,  0,  0,  0,  0,  0, -5,
      0,  0,  0,  5,  5,  0,  0,  0,
])
ROOK_EG = ROOK_MG

# --- HẬU (Queen) ---
QUEEN_MG = _flip([
    -20,-10,-10, -5, -5,-10,-10,-20,
    -10,  0,  0,  0,  0,  0,  0,-10,
    -10,  0,  5,  5,  5,  5,  0,-10,
     -5,  0,  5,  5,  5,  5,  0, -5,
      0,  0,  5,  5,  5,  5,  0, -5,
    -10,  5,  5,  5,  5,  5,  0,-10,
    -10,  0,  5,  0,  0,  0,  0,-10,
    -20,-10,-10, -5, -5,-10,-10,-20,
])
QUEEN_EG = QUEEN_MG

# --- VUA (King) ---
KING_MG = _flip([
    -30,-40,-40,-50,-50,-40,-40,-30,
    -30,-40,-40,-50,-50,-40,-40,-30,
    -30,-40,-40,-50,-50,-40,-40,-30,
    -30,-40,-40,-50,-50,-40,-40,-30,
    -20,-30,-30,-40,-40,-30,-30,-20,
    -10,-20,-20,-20,-20,-20,-20,-10,
     20, 20,  0,  0,  0,  0, 20, 20,
     20, 30, 10,  0,  0, 10, 30, 20,
])
KING_EG = _flip([
    -50,-40,-30,-20,-20,-30,-40,-50,
    -30,-20,-10,  0,  0,-10,-20,-30,
    -30,-10, 20, 30, 30, 20,-10,-30,
    -30,-10, 30, 40, 40, 30,-10,-30,
    -30,-10, 30, 40, 40, 30,-10,-30,
    -30,-10, 20, 30, 30, 20,-10,-30,
    -30,-30,  0,  0,  0,  0,-30,-30,
    -50,-30,-30,-30,-30,-30,-30,-50,
])
# Bộ bảng điểm này lấy từ  PeSTO’s Piece-Square Tables



TABLES_MG: dict[chess.PieceType, list[int]] = {
    chess.PAWN: PAWN_MG,
    chess.KNIGHT: KNIGHT_MG,
    chess.BISHOP: BISHOP_MG,
    chess.ROOK: ROOK_MG,
    chess.QUEEN: QUEEN_MG,
    chess.KING: KING_MG,
}

TABLES_EG: dict[chess.PieceType, list[int]] = {
    chess.PAWN: PAWN_EG,
    chess.KNIGHT: KNIGHT_EG,
    chess.BISHOP: BISHOP_EG,
    chess.ROOK: ROOK_EG,
    chess.QUEEN: QUEEN_EG,
    chess.KING: KING_EG,
}

# 3. HÀM ĐÁNH GIÁ CHÍNH (TAPERED EVALUATION + PST)

def evaluate_board(board: chess.Board) -> float:

    mg_white = 0      # Khởi tạo tổng điểm trung cuộc / tản cuộc cho trắng / đen
    mg_black = 0
    eg_white = 0
    eg_black = 0
    game_phase = 0

    # 1. Duyệt các quân cờ thông thường
    for piece_type in (chess.PAWN, chess.KNIGHT, chess.BISHOP, chess.ROOK, chess.QUEEN):
        val_mg = PIECE_VALUES_MG[piece_type]
        val_eg = PIECE_VALUES_EG[piece_type]
        tbl_mg = TABLES_MG[piece_type]
        tbl_eg = TABLES_EG[piece_type]

        # Đếm phase (chỉ tính quân nhẹ và quân nặng)
        if piece_type in PHASE_WEIGHTS:
            count = len(board.pieces(piece_type, chess.WHITE)) + len(board.pieces(piece_type, chess.BLACK))
            game_phase += count * PHASE_WEIGHTS[piece_type]

        # Quân trắng
        for sq in board.pieces(piece_type, chess.WHITE):
            mg_white += val_mg + tbl_mg[sq]
            eg_white += val_eg + tbl_eg[sq]

        # Quân đen sử dụng chung bảng điểm với quân trắng rồi dùng phép lật gương
        for sq in board.pieces(piece_type, chess.BLACK):
            mirror_sq = chess.square_mirror(sq)
            mg_black += val_mg + tbl_mg[mirror_sq]
            eg_black += val_eg + tbl_eg[mirror_sq]

    # 2. Vua (chỉ tính điểm vị trí PST)
    king_white = board.king(chess.WHITE)
    if king_white is not None:
        mg_white += KING_MG[king_white]
        eg_white += KING_EG[king_white]

    king_black = board.king(chess.BLACK)
    if king_black is not None:
        mirror_king_black = chess.square_mirror(king_black)
        mg_black += KING_MG[mirror_king_black]
        eg_black += KING_EG[mirror_king_black]

    # 3. Tính điểm chênh lệch cho 2 kịch bản
    mg_score = mg_white - mg_black
    eg_score = eg_white - eg_black

    # 4. Nội suy theo Phase thực tế 
    phase = min(game_phase,TOTAL_PHASE)
    total_score = (mg_score*phase+eg_score*(TOTAL_PHASE - phase))/TOTAL_PHASE

    return total_score if board.turn == chess.WHITE else -total_score
