# Hướng Dẫn Git & Quy Trình Làm Việc Nhóm

Tài liệu tóm tắt kiến thức Git cơ bản từ đầu và quy trình phối hợp làm việc nhóm chuẩn chỉ để hạn chế tối đa xung đột mã nguồn (merge conflict).

---

## 1. Các Khái Niệm Cốt Lõi (Git Là Gì?)

* **Repository (Repo):** Kho lưu trữ toàn bộ mã nguồn cùng lịch sử chỉnh sửa của dự án. Gồm có:
  * *Local Repo:* Bản sao hoàn chỉnh nằm trên máy tính cá nhân của bạn.
  * *Remote Repo:* Kho lưu trữ đặt trên máy chủ đám mây (GitHub, GitLab, Bitbucket).
* **Commit:** Một "ảnh chụp" (snapshot) lưu lại trạng thái các tệp tin tại một thời điểm cụ thể kèm theo mã hash nhận diện, tên tác giả và thông điệp (message) mô tả thay đổi.
* **Working Directory:** Thư mục làm việc thực tế trên ổ cứng máy bạn, nơi bạn trực tiếp chỉnh sửa code.
* **Staging Area (Index):** Khu vực chờ trung gian. Nơi bạn chọn lọc chính xác các file đã thay đổi (`git add`) trước khi đóng gói thành một commit.
* **Branch (Nhánh):** Một luồng phát triển tách biệt. Nhánh cho phép bạn viết tính năng mới hoặc sửa lỗi mà hoàn toàn không ảnh hưởng đến code đang chạy ổn định của người khác.
* **`main` / `master` Branch:** Nhánh chính chứa phiên bản mã nguồn đã hoàn thiện và ổn định nhất. **Nguyên tắc bất di bất dịch: Không bao giờ commit hay push trực tiếp lên nhánh này.**
* **Clone:** Thao tác tải toàn bộ repository từ máy chủ về máy tính lần đầu tiên (`git clone <url>`).
* **Fetch:** Lấy thông tin về các commit và nhánh mới nhất trên Remote về máy tính nhưng chưa gộp vào code bạn đang viết.
* **Pull (`git pull`):** Tải và tự động gộp (merge) code mới nhất từ Remote vào nhánh bạn đang đứng (tương đương `git fetch` + `git merge`).
* **Push (`git push`):** Tải các commit từ máy cá nhân lên kho lưu trữ Remote để chia sẻ với cả nhóm.
* **Merge:** Trộn lịch sử commit và nội dung của một nhánh khác vào nhánh hiện tại.
* **Merge Conflict (Xung đột mã nguồn):** Xảy ra khi hai thành viên cùng sửa đổi các dòng code giống nhau trên cùng một file. Git sẽ tạm dừng và yêu cầu lập trình viên tự chọn đoạn code nào cần giữ lại.
* **Pull Request (PR) / Merge Request (MR):** Yêu cầu xem xét trước khi gộp nhánh tính năng vào `main`. Đây là nơi các thành viên review code, góp ý và chạy kiểm thử tự động.

---

## 2. Quy Trình Phối Hợp Làm Việc Chuẩn (Team Workflow)

Mỗi khi bắt đầu một tính năng mới hoặc sửa một lỗi, hãy làm tuần tự theo 7 bước sau:

```
[Remote main]  <---------------------------- (Merge PR) <----+
      |                                                      |
  (git pull)                                            (git push)
      v                                                      |
[Local main] ---> (checkout -b) ---> [feat/branch] ---> (git commit)
```

### Bước 1: Cập nhật nhánh `main` ở máy cá nhân
Trước khi viết bất kỳ dòng code nào, luôn đảm bảo nhánh `main` của bạn đang chứa bản code mới nhất của cả nhóm:
```bash
git checkout main
git pull origin main
```

### Bước 2: Tạo nhánh mới cho tính năng
Tạo một nhánh mới tách ra từ `main` và đặt tên theo quy chuẩn rõ ràng:
* Cú pháp: `git checkout -b <loại-nhánh>/<tên-ngắn-gọn>`
* Ví dụ:
  * Tính năng mới: `git checkout -b feat/board-evaluation`
  * Sửa lỗi: `git checkout -b fix/pawn-move-bug`
  * Giao diện: `git checkout -b ui/timer-component`

### Bước 3: Viết code và commit cục bộ
Chia nhỏ công việc thành các commit có ý nghĩa logic thay vì gom một lượng lớn code vào một commit duy nhất:
```bash
# Kiểm tra các file đã chỉnh sửa hoặc tạo mới
git status

# Đưa file vào Staging Area (chọn tất cả hoặc từng file cụ thể)
git add .
# hoặc: git add student/evaluation.py

# Tạo commit kèm thông điệp rõ ràng theo chuẩn
git commit -m "feat: implement knight move generation"
```

### Bước 4: Đồng bộ code mới nhất từ `main` về nhánh của mình
Trong quá trình bạn code, các thành viên khác có thể đã merge code mới vào `main`. Hãy kéo cập nhật về nhánh của bạn để giải quyết xung đột sớm ngay tại máy mình:
```bash
git fetch origin
git merge origin/main
```

*Nếu xảy ra Conflict:*
1. Mở các file bị báo xung đột trong VS Code.
2. Chọn giữ code của bạn (*Accept Current Change*), code của nhóm (*Accept Incoming Change*) hoặc kết hợp cả hai.
3. Lưu file, sau đó chạy:
   ```bash
   git add .
   git commit -m "fix: resolve merge conflicts with main"
   ```

### Bước 5: Đẩy nhánh lên Remote Repository
Đẩy nhánh làm việc của bạn lên GitHub/GitLab:
```bash
# Lần đầu tiên đẩy nhánh này lên server:
git push -u origin feat/board-evaluation

# Những lần push tiếp theo trên cùng nhánh:
git push
```

### Bước 6: Mở Pull Request (PR)
1. Truy cập vào giao diện repository trên GitHub hoặc GitLab.
2. Nhấn nút **Compare & pull request** xuất hiện trên banner.
3. Điền tiêu đề và phần mô tả tóm tắt:
   * Bạn đã làm gì?
   * Cách kiểm tra / chạy thử code này thế nào?
4. Chỉ định ít nhất 1 thành viên trong nhóm làm **Reviewer**.
5. Sau khi nhận được xác nhận (Approve) và không có lỗi kiểm thử tự động, tiến hành merge vào `main`.

### Bước 7: Dọn dẹp nhánh sau khi hoàn tất
Khi PR đã được merge thành công lên `main`:
```bash
# Chuyển về main và kéo code mới vừa merge về
git checkout main
git pull origin main

# Xóa nhánh tính năng ở máy cá nhân cho gọn gàng
git branch -d feat/board-evaluation
```

---

## 3. Bảng Tra Cứu Lệnh Thường Dùng

| Lệnh | Mô tả chi tiết |
| :--- | :--- |
| `git status` | Kiểm tra tình trạng các file (đã sửa, đang chờ commit hay chưa quản lý) |
| `git diff` | Xem chi tiết từng dòng code thêm/xóa trước khi đưa vào staging |
| `git log --oneline -n 5` | Hiển thị 5 commit gần nhất dưới dạng 1 dòng rút gọn |
| `git branch -a` | Liệt kê tất cả các nhánh hiện có (cả local và remote) |
| `git checkout <tên-nhánh>` | Chuyển sang làm việc tại một nhánh đã tồn tại |
| `git checkout -b <tên-nhánh>` | Tạo một nhánh mới và tự động chuyển sang nhánh đó ngay |
| `git stash` | Tạm cất các thay đổi chưa commit vào bộ nhớ tạm để chuyển nhánh an toàn |
| `git stash pop` | Lấy lại các thay đổi vừa cất trong bộ nhớ tạm ra lại thư mục làm việc |

---

## 4. Bốn Nguyên Tắc Vàng Khi Làm Việc Nhóm

1. **Tuyệt đối không commit trực tiếp lên `main`:** Tất cả code mới chỉ được đưa vào nhánh chính thông qua quy trình tạo và duyệt Pull Request.
2. **Không commit file rác hoặc cấu hình môi trường cá nhân:**
   * Luôn khai báo các thư mục ảo (`.venv/`, `venv/`), file tạm (`__pycache__/`, `.DS_Store`), và các file chứa thông tin nhạy cảm (`.env`) vào tệp `.gitignore`.
   * Không commit các file sinh ra trong quá trình chạy tự động nếu chúng không phục vụ mục đích cấu hình chung.
3. **Commit thường xuyên, pull sớm:** Viết các commit nhỏ, rõ ràng. Kéo code mới từ `main` về nhánh thường xuyên để tránh xung đột lớn khi làm việc lâu ngày.
4. **Tuyệt đối không dùng cờ cưỡng ép (`git push -f`) lên các nhánh chung:** Lệnh này ghi đè toàn bộ lịch sử trên server và có thể làm mất toàn bộ công sức code của đồng đội.