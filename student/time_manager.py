# """TODO: implement dynamic allocation of the remaining game clock here."""

# from chesslab_sdk import SearchContext


# def allocate_time(context: SearchContext) -> int:
#     ...
"""Quản lý thời gian: chia quỹ giờ còn lại thành hai mốc cho mỗi nước đi.

- soft: thời gian *nên* dùng. Search xong một độ sâu mà đã dùng quá nửa soft
  thì dừng, vì độ sâu tiếp theo thường tốn gấp nhiều lần.
- hard: giới hạn *tuyệt đối*. Vượt là cắt search ngay (ném SearchTimeout).

Mọi đơn vị trong file này là mili-giây (ms).
"""

from __future__ import annotations

import warnings

from chesslab_sdk import SearchContext

# ---------------------------------------------------------------------------
# Tham số
# ---------------------------------------------------------------------------
ASSUMED_MOVES_LEFT = 30      # giả định ván còn ~30 nước của mình
MOVE_OVERHEAD_MS = 500       # hệ thống chắc chắn trừ 500 ms mỗi nước

NORMAL_FLOOR_MS = 400        # mức sàn khi quỹ giờ còn rộng
URGENT_FLOOR_MS = 50         # mức sàn khi sắp hết giờ
URGENT_THRESHOLD_MS = 10_000  # còn > 10 s là "rộng", ngược lại là "khẩn cấp"

HARD_MULTIPLIER = 3          # hard tối đa = 3 × soft ...
HARD_FRACTION_DIVISOR = 10   # ... và không quá 1/10 (10%) quỹ giờ còn lại

# Dùng khi không đọc được thời gian còn lại từ context (xem _remaining_ms).
FALLBACK_REMAINING_MS = 60_000

# Các tên trường có thể có trên SearchContext: (tên, hệ số đổi sang ms).
# Sửa/bổ sung cho đúng với chesslab_sdk của bạn.
_REMAINING_FIELDS: tuple[tuple[str, int], ...] = (
    ("time_left_ms", 1),
    ("remaining_ms", 1),
    ("remaining_time_ms", 1),
    ("time_remaining_ms", 1),
    ("clock_ms", 1),
    ("time_left_s", 1000),
    ("remaining_s", 1000),
    ("remaining_seconds", 1000),
    ("time_left_seconds", 1000),
)

_warned_missing_clock = False


# ---------------------------------------------------------------------------
# Lõi tính toán (hàm thuần, dễ test)
# ---------------------------------------------------------------------------
def compute_budget(remaining_ms: int) -> tuple[int, int]:
    """Trả về (soft_ms, hard_ms) cho một nước đi, theo thời gian còn lại."""
    remaining_ms = int(remaining_ms)

    # Bước 1: chia đều, để dành trước phần overhead hệ thống sẽ trừ.
    soft = (remaining_ms - ASSUMED_MOVES_LEFT * MOVE_OVERHEAD_MS) // ASSUMED_MOVES_LEFT

    # Bước 2: mức sàn (nghĩ dưới 500 ms gần như miễn phí vì đằng nào cũng bị trừ).
    floor = NORMAL_FLOOR_MS if remaining_ms > URGENT_THRESHOLD_MS else URGENT_FLOOR_MS
    soft = max(soft, floor)

    # Bước 3: giới hạn cứng, nhưng không bao giờ nhỏ hơn soft.
    hard = min(HARD_MULTIPLIER * soft, remaining_ms // HARD_FRACTION_DIVISOR)
    hard = max(hard, soft)

    return soft, hard


# ---------------------------------------------------------------------------
# Giao diện với SDK
# ---------------------------------------------------------------------------
def _remaining_ms(context: SearchContext) -> int:
    """Đọc thời gian còn lại (ms) của bên đang đi từ context."""
    global _warned_missing_clock

    for name, scale in _REMAINING_FIELDS:
        value = getattr(context, name, None)
        if value is not None:
            return int(value * scale)

    if not _warned_missing_clock:
        _warned_missing_clock = True
        warnings.warn(
            "time_manager: không tìm thấy trường thời gian còn lại trên "
            "SearchContext; đang dùng giá trị dự phòng. Hãy sửa _REMAINING_FIELDS.",
            RuntimeWarning,
            stacklevel=2,
        )
    return FALLBACK_REMAINING_MS


def allocate_time_window(context: SearchContext) -> tuple[int, int]:
    """Trả về (soft_ms, hard_ms) cho nước đi hiện tại. search.py dùng hàm này."""
    return compute_budget(_remaining_ms(context))


def allocate_time(context: SearchContext) -> int:
    """Giữ nguyên chữ ký gốc (-> int): trả về mốc soft của nước đi, đơn vị ms.

    Nếu SDK mong đợi mốc hard thay vì soft, đổi `[0]` thành `[1]`.
    """
    return allocate_time_window(context)[0]