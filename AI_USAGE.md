# Khai báo sử dụng AI

- **Các công cụ đã dùng trong nhóm:** 
  - Claude Code (mô hình Claude Opus 5.5 của Anthropic)
  - Google Antigravity (Gemini 3.8 / Pro)
  - GitHub Copilot / ChatGPT
- **Mục đích sử dụng:** Hỗ trợ đọc hiểu mã nguồn và tài liệu thư viện, gợi ý cấu trúc giải thuật toán học và tìm kiếm kinh điển, hỗ trợ viết mã và gỡ lỗi (debugging), sinh các kịch bản kiểm thử, định dạng báo cáo và thao tác Git.

---

## Chi tiết theo từng thành viên

### 1. Nguyễn Anh Minh (Trưởng nhóm - Điều phối chính & Quản lý dự án)

- **Vai trò:** Trưởng nhóm, điều phối tổng thể, phân chia nhiệm vụ, theo dõi tiến độ các giai đoạn (Milestones) và nghiệm thu chất lượng hệ thống.
- **Công cụ chính:** Google Antigravity (Gemini), ChatGPT.

| Việc | AI đã làm | Phần tự làm / kiểm tra |
| --- | --- | --- |
| **Cập nhật mã nguồn** | Hỗ trợ phân tích cấu trúc tổng thể của template và phát hiện các xung đột nhánh tiềm ẩn | Định hướng kiến trúc chung của bot; điều phối việc merge các nhánh tính năng (`feat/search`, `feat/eval`, `feat/time`) vào nhánh chính `main` |
| **Rà soát** | Hỗ trợ tổng hợp checklist các yêu cầu giảng viên trong `README.md` (giới hạn thư viện, dung lượng, luật thi đấu Chess960, cơ chế trừ giờ 500 ms) | Nghiên cứu kỹ thể thức thi đấu và quy chế môn học; rà soát chéo mã nguồn để đảm bảo không có vi phạm; quản lý tiến độ hoàn thành của các thành viên |
| **Viết mã** | Hỗ trợ kiểm tra các trường hợp biên trong luồng tích hợp tổng thể giữa Search - Evaluation - Time Manager | Phối hợp cùng các thành viên rà soát logic tích hợp tại `student/bot.py`; kiểm tra độ ổn định của bot trong các tình huống cờ phức tạp |
| **Kiểm thử** | Gợi ý các tiêu chí đánh giá độ ổn định và sức mạnh của bot qua các thế cờ chuẩn | Trực tiếp tổ chức các phiên đấu thử nghiệm nghiệm thu bot trên giao diện web local ở nhiều thế Chess960 ngẫu nhiên; kiểm tra tỷ lệ thắng/hòa và kiểm soát việc không bao giờ bị quá giờ |
| **Tài liệu** | Hỗ trợ định dạng và rà soát tính nhất quán của tài liệu kỹ thuật | Phân công công việc viết tài liệu; kiểm duyệt toàn bộ báo cáo nộp bài và hoàn thiện tệp khai báo sử dụng AI của cả nhóm |
| **Git** | Gợi ý cấu trúc quản lý nhánh và quy trình làm việc nhóm trên GitHub | Kiểm soát tiến độ commit/pull request của các thành viên; quản lý kho mã nguồn và thực hiện gắn thẻ nộp bài chính thức `submission-final` |

*Cam kết:* Nắm vững toàn bộ tiến độ, phân công nhiệm vụ và kiến trúc hệ thống của nhóm; cam kết toàn bộ mã nguồn của nhóm tuân thủ 100% quy chế môn học, không sử dụng mô hình học máy hay dữ liệu bên ngoài, sẵn sàng cùng các thành viên bảo vệ đồ án trước giảng viên.

---

### 2. Nguyễn Tiến Minh (Phần Evaluation & Bot Core)

- **Vai trò:** Phụ trách chính Module Lượng giá (Evaluation) và khung điều khiển Bot.
- **Công cụ chính:** Google Antigravity (Gemini), GitHub Copilot / ChatGPT.

| Việc | AI đã làm | Phần tự làm / kiểm tra |
| --- | --- | --- |
| **Cập nhật mã nguồn** | Đồng bộ cập nhật từ GitHub, đối chiếu giao diện giữa module evaluation, bot core và hệ thống chấm điểm | Quyết định lộ trình nâng cấp các phiên bản lượng giá từ MVP lên v2 và v3 |
| **Rà soát** | Tra cứu cú pháp Bitboard trong `python-chess`; tra cứu nguyên lý toán học của Tapered Evaluation (nội suy MG/EG theo `game_phase`), cấu trúc tốt và các thế hòa lý thuyết | Quyết định bảng trọng số điểm quân, hệ số thưởng/phạt và phân loại giai đoạn ván cờ |
| **Viết mã** | Hỗ trợ tra cứu các hàm bitwise (`pieces_mask`, `square_mirror`, `is_insufficient_material`); gợi ý công thức tính trước mảng mặt nạ Bitboard (`FILE_MASKS`, `PASSED_MASKS`, `ADJACENT_FILES_MASK`) và bảng băm cache cấu trúc Tốt; hỗ trợ viết hàm xuất PGN | Tự thiết kế toàn bộ bảng vị trí quân PST (Piece-Square Tables) thủ công cho trung cuộc và tàn cuộc; xây dựng các luật đánh giá đặc thù cho Chess960 (giữ quyền nhập thành, phát triển quân nhẹ rời hàng đáy, phạt xuất Hậu sớm, lá chắn Tốt bảo vệ Vua sau nhập thành); lập trình hàm dồn ép Vua (mop-up) ở cờ tàn; chuẩn hóa phép chia số nguyên `//` và ép kiểu `int` cho chuẩn Negamax/PVS |
| **Kiểm thử** | Gợi ý kịch bản test bàn cờ thế, kiểm tra tính toán Bitboard $O(1)$ và đo đạc thời gian chạy của hàm eval | Trực tiếp chạy `pytest`, thử nghiệm bot trên giao diện web local qua nhiều thế Chess960 ngẫu nhiên, xác minh hàm lượng giá phản ánh đúng ưu thế bàn cờ |
| **Tài liệu** | Hỗ trợ định dạng và rà soát tài liệu `blueprint-MVP.md`, chú thích chi tiết trong mã nguồn | Viết mô tả ý nghĩa chiến thuật cờ vua cho từng hàm lượng giá và hoàn thiện khai báo AI |
| **Git** | Gợi ý soạn thảo commit message và mô tả pull request rõ ràng theo chuẩn Conventional Commits | Trực tiếp tạo và merge các PR cốt lõi (#1, #2, #3, #4, #5, #7, #10, #14, #15) |

*Cam kết:* Tuyệt đối không sử dụng mạng nơ-ron (NNUE), mô hình học sâu hay bộ dữ liệu cờ tàn/sách khai cuộc có sẵn. Toàn bộ hàm lượng giá hoàn toàn là các công thức giải tích toán học tĩnh dựa trên tri thức cờ vua; thành viên hoàn toàn làm chủ và sẵn sàng bảo vệ từng thành phần trong mã nguồn.

---

### 3. Nguyễn Ngọc Phúc (Phần Search)

- **Vai trò:** Phụ trách chính Module Tìm kiếm nâng cao (Search Engine).
- **Công cụ chính:** Claude Code (Claude Opus 5.5).

| Việc | AI đã làm | Phần tự làm / kiểm tra |
| --- | --- | --- |
| **Cập nhật mã nguồn** | Tải bản mới nhất từ GitHub, merge `main` vào `feat/search-level2` | Quyết định nhánh làm việc và chiến lược giải quyết conflict |
| **Rà soát** | Đọc luật trong README, `blueprint-MVP.md`, `app/game_controller.py`; đối chiếu search với time manager và eval; chỉ ra các chỗ chưa khớp | Lựa chọn các kỹ thuật cần cải tiến và kiến trúc tìm kiếm |
| **Viết mã** | Hỗ trợ hiện thực PVS (Principal Variation Search), LMR (Late Move Reduction), Reverse Futility Pruning, SEE (Static Exchange Evaluation), Delta Pruning trong quiescence; quản lý soft/hard budget, luật hòa 300 ply / 50 nước / 3 lần lặp, contempt factor | Đọc hiểu, kiểm soát chặt chẽ từng dòng mã và chấp nhận thay đổi |
| **Kiểm thử** | Chạy `pytest`, đo tốc độ duyệt (nps) và độ sâu đạt được, đo thời gian mỗi nước so với soft/hard, cho bot tự đấu trên các thế 960 ngẫu nhiên | Phân tích nhật ký thi đấu và tinh chỉnh tham số |
| **Tài liệu** | Hỗ trợ soạn thảo báo cáo kỹ thuật `docs/bao-cao-search-level2.pdf` | Duyệt nội dung và kiểm chứng tính chuẩn xác |
| **Git** | Soạn mô tả chi tiết cho commit và pull request | Trực tiếp commit và quản lý nhánh |

*Cam kết:* Không dùng học máy, mô hình đã huấn luyện, chương trình cờ vua bên ngoài, sách khai cuộc hay cơ sở dữ liệu nước đi có sẵn. AI chỉ hỗ trợ hiện thực các thuật toán tìm kiếm kinh điển; thành viên hiểu và giải thích được toàn bộ phần mã đã nộp.

---

### 4. Nguyễn Đức Quân (Phần Time Management)

- **Vai trò:** Phụ trách Module Quản lý đồng hồ thời gian (Time Allocation).
- **Công cụ chính:** Google Antigravity / ChatGPT.

| Việc | AI đã làm | Phần tự làm / kiểm tra |
| --- | --- | --- |
| **Cập nhật mã nguồn** | Hỗ trợ tích hợp module đồng hồ thời gian vào luồng tìm kiếm của bot | Phân tích yêu cầu quỹ thời gian trong tài liệu đặc tả |
| **Rà soát** | Tra cứu các mô hình phân bổ thời gian cờ vua (Time Allocation), kiểm tra các trường hợp biên khi đồng hồ sắp cạn | Lựa chọn công thức chia thời gian động soft/hard và mức trễ 500 ms/nước |
| **Viết mã** | Gợi ý khung mã nguồn hàm `compute_budget`, tính toán `soft_limit` và `hard_limit` dựa trên thời gian còn lại | Hoàn thiện `student/time_manager.py`, thiết lập ngưỡng khẩn cấp (urgent threshold), mức sàn tối thiểu và trần an toàn không vượt quá 10% quỹ giờ |
| **Kiểm thử** | Sinh kịch bản kiểm thử mô phỏng đồng hồ đếm ngược với các mức thời gian ban đầu khác nhau | Kiểm tra thực tế trên giao diện để đảm bảo bot không bao giờ bị xử thua vì hết giờ |
| **Tài liệu** | Hỗ trợ định dạng bảng ví dụ phân bổ thời gian theo số giây còn lại | Rà soát và hoàn thiện phần thuyết minh quản lý thời gian |
| **Git** | Hỗ trợ soạn thảo mô tả commit | Thực hiện commit và tạo PR #12, #13 nhánh `feat/time-manager` |

*Cam kết:* Thuật toán phân bổ thời gian hoàn toàn dựa trên phép tính số học động, không sử dụng tài nguyên bên ngoài.

---

## Cam kết chung của toàn nhóm

1. **Tuyệt đối không dùng mô hình học máy:** Không dùng NNUE, mạng nơ-ron hay trọng số huấn luyện trước. Toàn bộ mã nguồn bot vận hành dựa trên các giải thuật tìm kiếm kinh điển và hàm lượng giá toán học tĩnh.
2. **Không dùng dữ liệu bên ngoài:** Không tích hợp Opening Book hay Endgame Tablebase.
3. **Làm chủ mã nguồn:** Mọi đoạn mã AI gợi ý đều được các thành viên trực tiếp rà soát, kiểm thử kỹ lưỡng và nắm vững nguyên lý hoạt động để bảo vệ trong buổi vấn đáp.
