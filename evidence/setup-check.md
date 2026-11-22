# Mục 2 — Kiểm tra SUT/backend

Ngày: 2026-11-22, múi giờ Asia/Saigon. Đây là log thiết lập, **không phải** kết quả Load/Stress/Spike.

| Mục | Kết quả quan sát |
|---|---|
| SUT commit | `85af3ba875c88283615e22cb108f13e2fccaf0e9` |
| Backend | Node process PID `13352`, `node server.js`, khởi động khoảng `07:55:08` |
| Port | `3000`, `GET /api/products` trả HTTP 200 |
| Node/npm | `v25.9.0` / `11.12.1` |
| Backend packages | `npm ls --depth=0` thành công: Express 5.2.1, sqlite3 6.0.1, jsonwebtoken 9.0.3, cors 2.8.6, body-parser 2.2.2 |
| DB trước smoke | `users=2`, `categories=3`, `products=5`, `orders=0` |
| Danh mục seed | ID 1 Điện thoại; ID 2 Laptop; ID 3 Phụ kiện |

Smoke API bằng `scripts/smoke_admin_api.ps1` lúc `08:03:31+07:00`: đăng nhập admin thành công; GET category có 3 dòng, GET product có 5 dòng; tạo category ID 5, cập nhật và xóa đều kiểm chứng bằng GET; sau smoke còn 3 category. Một lần chạy smoke trước đó đã tạo/xóa ID 4. Không có danh mục thử còn sót.

Đối chiếu code `backend/server.js`: POST category trả `id`; PUT/DELETE trả thông báo. Ba endpoint ghi category dùng `authenticateToken` nhưng không kiểm tra role admin. `backend/database.js` DROP/seed bảng khi server khởi động, nên không restart backend giữa lúc chuẩn bị dữ liệu và chạy test nếu không muốn mất dữ liệu thử.

Không ghi token JWT hoặc mật khẩu vào log này. Không có ảnh tài nguyên trong bước này; ảnh khi chạy hiệu năng sẽ được thu ở bước sau.
