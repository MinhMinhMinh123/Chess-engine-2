# Khai báo sử dụng AI

- Công cụ đã dùng: Claude Code (mô hình Claude Opus 5.5 của Anthropic), chạy trong ứng dụng Claude trên máy tính.
- Mục đích sử dụng: hỗ trợ đọc hiểu mã nguồn, đề xuất và viết mã cho phần search, kiểm thử, viết báo cáo và thao tác Git.

## Chi tiết theo thành viên

### Nguyễn Ngọc Phúc (phần search)

| Việc | AI đã làm | Phần tự làm / kiểm tra |
| --- | --- | --- |
| Cập nhật mã nguồn | Tải bản mới nhất từ GitHub, merge `main` vào `feat/search-level2` | Quyết định nhánh làm việc |
| Rà soát | Đọc luật trong README, `blueprint-MVP.md`, `app/game_controller.py`; đối chiếu search với time manager và eval; chỉ ra các chỗ chưa khớp | Chọn các việc cần làm |
| Viết mã | Sửa `student/bot.py`, `student/search.py`, `student/strategies/search/search_level2.py` (quản lý thời gian soft/hard, giữ kết quả khi hết giờ giữa chừng, luật hòa 300 ply và 50 nước, contempt, ưu tiên nhập thành Chess960); đổi phép chia thành số nguyên trong `eval_v2.py` | Đọc hiểu và chấp nhận từng thay đổi |
| Kiểm thử | Chạy `pytest`, đo tốc độ và độ sâu, đo thời gian mỗi nước so với soft/hard, cho bot tự đấu trên các thế 960 ngẫu nhiên | Xem lại kết quả |
| Tài liệu | Viết báo cáo `docs/bao-cao-search-level2.pdf` | Duyệt nội dung |
| Git | Commit, push nhánh, soạn mô tả cập nhật cho PR #11 | Commit đứng tên thành viên |

Không dùng học máy, mô hình đã huấn luyện, chương trình cờ vua bên ngoài, sách khai cuộc hay dữ liệu nước đi có sẵn trong mã nguồn bot. AI chỉ hỗ trợ viết mã dùng các kỹ thuật search đã học; thành viên hiểu và giải thích được toàn bộ phần mã đã nộp.

### Nguyễn Tiến Minh (phần: ...)

| Việc | AI đã làm | Phần tự làm / kiểm tra |
| --- | --- | --- |
| Cập nhật mã nguồn |  |  |
| Rà soát |  |  |
| Viết mã |  |  |
| Kiểm thử |  |  |
| Tài liệu |  |  |
| Git |  |  |

_(Ghi rõ công cụ AI đã dùng nếu khác Claude Code. Nếu không dùng AI, ghi "Không sử dụng AI".)_

### Họ và tên (NguyenDucQuan) (phần: ...)

| Việc | AI đã làm | Phần tự làm / kiểm tra |
| --- | --- | --- |
| Cập nhật mã nguồn |  |  |
| Rà soát |  |  |
| Viết mã |  |  |
| Kiểm thử |  |  |
| Tài liệu |  |  |
| Git |  |  |

_(Ghi rõ công cụ AI đã dùng nếu khác Claude Code. Nếu không dùng AI, ghi "Không sử dụng AI".)_

### Họ và tên (MinhMinhMinh123) (phần: ...)

| Việc | AI đã làm | Phần tự làm / kiểm tra |
| --- | --- | --- |
| Cập nhật mã nguồn |  |  |
| Rà soát |  |  |
| Viết mã |  |  |
| Kiểm thử |  |  |
| Tài liệu |  |  |
| Git |  |  |

_(Ghi rõ công cụ AI đã dùng nếu khác Claude Code. Nếu không dùng AI, ghi "Không sử dụng AI".)_
