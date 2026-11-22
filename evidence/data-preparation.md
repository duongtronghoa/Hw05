# Mục 3 — Chuẩn bị dữ liệu thử

Ngày 2026-11-22 (Asia/Saigon). Backend được giữ chạy ở PID `13352`; không restart trong lúc chuẩn bị. Dữ liệu này phục vụ workflow Admin, **không phải** kết quả benchmark.

Lệnh: `python .\scripts\prepare_admin_data.py` từ `hw05-work/`.

| Kiểm tra | Kết quả |
|---|---:|
| Tài khoản admin tổng hợp mới tạo | 100 |
| Tổng tài khoản admin tổng hợp kiểm chứng trong SQLite | 100 |
| File CSV `data/admin1.csv` đến `data/admin100.csv` | 100 |
| Chạy lại script để kiểm tra idempotency | 0 tài khoản mới, vẫn 100 CSV |
| Tổng user trong DB sau chuẩn bị | 102 |
| Category/product/order sau chuẩn bị | 3 / 5 / 0 |
| Admin account bị khóa | 0 |
| API login bằng account `001` và `100` | Thành công, `role=admin`, có token |

Mỗi CSV có header `email,password,category_prefix` và một dòng. Tên category tạo trong lượt test sau này phải dùng `category_prefix` cộng với UUID/iteration key để tránh trùng giữa VU và các lượt lặp. `categoryId` sẽ lấy từ response `POST /api/categories`, không lấy từ CSV hay ID seed.

Vì `POST /api/register` chỉ tạo user có role `user` và không có API cấp quyền admin, script tạo các account admin **trực tiếp trong SQLite** trước khi đo; đây là thao tác dựng dữ liệu thử, không tính vào tải. Script kiểm tra account trùng và role/password trước khi dùng lại. Mật khẩu là giả, chỉ dùng cho SUT cục bộ.

Nếu backend khởi động lại, module `database.js` xóa/seed lại bảng: chạy script chuẩn bị này lần nữa và kiểm tra số lượng trước khi đo. Không đưa file `database.sqlite` đã sửa vào repo bài làm hoặc zip nộp trừ khi giảng viên yêu cầu rõ.
