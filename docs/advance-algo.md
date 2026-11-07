# Blueprint bản Advance-MVP

### 1. `search_v2.py`

Mở rộng Negamax + Alpha-Beta của MVP:

- **PVS**: nước đầu tìm cửa sổ đầy đủ, các nước sau thử cửa sổ hẹp rồi tìm lại nếu cần.
- **Transposition table**: lưu điểm, độ sâu, loại bound và nước tốt nhất để tái sử dụng.
- **Quiescence**: tiếp tục xét bắt quân, phong Hậu và nước thoát chiếu để giảm hiệu ứng chân trời.
- **Pruning / extension**: null-move pruning và kéo dài độ sâu khi đang bị chiếu.
- **Move ordering**: TT move, bắt quân MVV-LVA, phong cấp, killer và history heuristic.
- **Iterative deepening + timeout**: chỉ giữ kết quả từ độ sâu đã hoàn tất; search trên bản sao bàn cờ.

### 2. `eval_v2.py`

Điểm theo centipawn, trả về góc nhìn bên đang đi:

- **Tapered evaluation**: nội suy riêng điểm trung cuộc và tàn cuộc theo game phase.
- **Material + PST**: giá trị quân và bảng điểm vị trí khác nhau theo giai đoạn.
- **Cấu trúc Tốt**: tốt thông, tốt chồng, tốt cô lập và tốt liên kết; dùng bitboard và cache.

### 3. `eval_v3.py`

Giữ nền `eval_v2`, bổ sung yếu tố chiến lược:

- **Cặp Tượng, Xe** trên cột mở / nửa mở và lá chắn Tốt quanh Vua.
- **Khai cuộc Chess960**: quyền nhập thành, phát triển quân nhẹ và hạn chế xuất Hậu sớm.
- **Tàn cuộc**: mop-up khi hơn quân; trả hòa khi thiếu lực chiếu hết.
