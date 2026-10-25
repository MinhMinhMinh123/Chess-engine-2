# Blueprint bản MVP #

### 1. `bot.py`

| Việc | Cách làm |
| --- | --- |
| Khởi tạo | Lưu `config`, tạo `random.Random(config.seed)` và một `Searcher` |
| Bảo vệ bàn cờ gốc | Search trên `board.copy()`, nên dù search bị cắt ngang bàn gốc vẫn đúng |
| Không bao giờ crash | Bọc toàn bộ trong `try/except`, lỗi thì trả nước hợp lệ đầu tiên |
| Kiểm tra cuối | Chỉ trả nước nếu nó thuộc `board.legal_moves` |

### 2. `search.py`

- **Negamax**: một hàm dùng cho cả hai bên, điểm của mình = −(điểm của đối thủ).
- **Alpha-beta**: `alpha` = điểm tốt nhất mình chắc chắn có, `beta` = mức đối thủ cho phép. Khi `alpha ≥ beta` thì bỏ các nước còn lại của node đó.
- **Điểm kết thúc ván**:
  - Chiếu hết → `-MATE + ply` (chiếu hết càng sớm càng được ưu tiên).
  - Hết nước / thiếu quân → `0`.
- **Dừng đúng giờ**: cứ 1024 node kiểm tra đồng hồ một lần, quá `hard` thì ném `SearchTimeout`.

### 3. `evaluation.py`

Chỉ đếm vật chất, dùng bitboard có sẵn của thư viện `chess`:

| Quân | Tốt | Mã | Tượng | Xe | Hậu |
| --- | --- | --- | --- | --- | --- |
| Điểm (centipawn) | 100 | 320 | 330 | 500 | 900 |

`điểm = Σ giá trị × (số quân Trắng − số quân Đen)`, sau đó đổi dấu nếu bên đang đi là Đen (yêu cầu của negamax).

### 4. `time_manager.py`

Trả về hai mốc cho mỗi nước:

- **soft**: thời gian *nên* dùng. Search xong một độ sâu mà đã dùng quá nửa soft thì dừng, vì độ sâu tiếp theo thường tốn gấp nhiều lần.
- **hard**: giới hạn *tuyệt đối*. Vượt là cắt search ngay.

Cách tính, theo 3 bước:

| Bước | Công thức | Lý do |
| --- | --- | --- |
| 1. Chia đều | `soft = (còn lại − 30 × 500) / 30` | Giả định còn ~30 nước; để dành trước 500 ms/nước mà hệ thống chắc chắn sẽ trừ |
| 2. Mức sàn | `soft ≥ 400 ms` nếu còn > 10 s, ngược lại `soft ≥ 50 ms` | Nghĩ dưới 500 ms gần như miễn phí vì đằng nào cũng bị trừ 500 ms |
| 3. Giới hạn cứng | `hard = min(3 × soft, 10% còn lại)`, và `hard ≥ soft` | Cho phép nghĩ lâu hơn khi cần, nhưng không bao giờ đốt quá 10% quỹ giờ trong một nước |

Ví dụ với thời gian còn lại khác nhau:

| Còn lại | soft | hard |
| --- | --- | --- |
| 360 s | 11,5 s | 34,5 s |
| 240 s | 7,5 s | 22,5 s |
| 180 s | 5,5 s | 16,5 s |
| 60 s | 1,5 s | 4,5 s |
| 20 s | 0,4 s (mức sàn) | 1,2 s |
| 5 s | 0,05 s (khẩn cấp) | 0,15 s |

Vì `soft` được tính lại mỗi nước theo thời gian *còn lại*, quỹ giờ giảm dần chứ không cạn đột ngột.
