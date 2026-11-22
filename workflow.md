# Workflow Admin đã chọn

MSSV: `23120127`. Ngày chuẩn bị: `2026-11-22` (Asia/Saigon).

## Phạm vi

1. `POST /api/login` bằng tài khoản có `role=admin` → trích `token`.
2. `GET /api/categories` → kiểm tra danh sách danh mục.
3. `GET /api/products` → kiểm tra danh sách sản phẩm.
4. `POST /api/categories` với tên duy nhất cho mỗi VU/lượt lặp → trích `id` từ JSON response làm `categoryId`.
5. `PUT /api/categories/${categoryId}` → cập nhật đúng danh mục vừa tạo.
6. `DELETE /api/categories/${categoryId}` → xóa đúng danh mục vừa tạo.

## Ba nhóm endpoint theo đề

| Nhóm | Endpoint |
|---|---|
| Auth-heavy | `POST /api/login` |
| Read-heavy | `GET /api/categories`, `GET /api/products` |
| Transactional/write-heavy | `POST`, `PUT`, `DELETE /api/categories` |

Đây là workflow người dùng đã chọn. Cần xác nhận với nhóm rằng không có thành viên khác kiểm thử cùng workflow. Nếu giảng viên yêu cầu “transactional” phải là giỏ hàng/checkout, cần trao đổi lại trước khi chạy ba scenario; đề nêu giỏ/checkout là **ví dụ**, không định nghĩa bắt buộc.

## Dữ liệu và tính độc lập

Tạo 100 admin account tổng hợp, mỗi VU dùng một account từ CSV riêng. CSV chứa `email,password,category_prefix`. Tên danh mục tạo mới phải ghép prefix với giá trị duy nhất theo từng iteration, ví dụ UUID; cập nhật/xóa dùng `categoryId` từ response tạo mới, không dùng ID cứng. Một iteration thất bại trước bước delete có thể để lại danh mục thử: ghi lại và dọn sau khi đã lưu bằng chứng, không xóa bừa danh mục seed.

## Quan sát từ code SUT

- `POST/PUT/DELETE /api/categories` yêu cầu JWT hợp lệ qua `authenticateToken`, nhưng **không kiểm tra `role=admin`**. Dùng account admin để giữ đúng workflow, và ghi sai lệch phân quyền này để kiểm chứng riêng khi làm issue.
- `POST /api/categories` trả JSON có `id`; `PUT/DELETE` trả thông báo, không xác nhận số bản ghi thay đổi. Assertion chỉ kiểm tra 200 là yếu; khi làm plan cần kiểm tra thêm trạng thái trước/sau bằng `GET /api/categories` hoặc kiểm chứng database trong smoke test.
- Login sai tăng `login_attempts` thêm 2 và khóa 180 giây; workload phải dùng mật khẩu đúng, xử lý login lỗi riêng.
- `backend/database.js` xóa và seed lại bảng khi server khởi động. Sau restart phải chuẩn bị lại admin account và CSV trước khi chạy.

## Kiểm chứng nhóm

Trạng thái: **chưa có bằng chứng xác nhận từ các thành viên khác**. Gửi đúng chuỗi workflow và 6 endpoint trên cho nhóm, ghi ngày/giờ xác nhận vào đây hoặc báo cáo trước khi nộp.
