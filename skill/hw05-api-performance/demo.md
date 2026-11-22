# Demo áp dụng Agent Skill: nhóm Read-heavy

**Lệnh giao việc cho agent demo (do agent tự chọn để đáp ứng P13, không giả là tin nhắn riêng của người học):** “Dùng `skill/hw05-api-performance/SKILL.md` để kiểm tra một nhóm endpoint hoàn chỉnh từ JTL thật: `GET /api/categories` và `GET /api/products` ở tầng Stress 80 VU. Nêu nguồn, cửa sổ, số mẫu, p95, RPS, lỗi và giới hạn.”

## Input và phép tính

- SUT EShop commit `85af3ba875c88283615e22cb108f13e2fccaf0e9`, JMeter 5.6.3, plan `23120127_Stress_20261122.jmx`.
- Raw `results/stress/stress.jtl`, SHA-256 `5f5ebffc713fc84474ef1aa1d8dbc3f6e9862952af6eb745a710a59d8e5ef15a`.
- Lọc `threadName` thuộc `TG_Stress_Level_4_80VU`, cửa sổ request đầu đến response cuối của tầng dài **118,821 giây** (gồm ramp). RPS mỗi endpoint = số mẫu endpoint / 118,821. p95 nearest-rank tính từ từng label riêng, không trung bình p95 của hai endpoint.

| Endpoint/label | Số mẫu | `success=false` | p95 (ms) | RPS trong cùng cửa sổ |
|---|---:|---:|---:|---:|
| `GET /api/categories` / `02_categories_list` | 769 | 0 | 13 | 6,472 |
| `GET /api/products` / `03_products_list` | 754 | 0 | 15 | 6,346 |

Hai endpoint đều nằm dưới giả thuyết read p95 ≤500 ms của thiết kế, trong **lượt 80 VU 2 phút trên máy này**. Tổng read RPS là 12,818; tổng tất cả sáu endpoint trong tầng là 37,796 RPS. Chưa thể suy ra trần server hoặc SLA ngoài môi trường local; think-time, JMeter và Node cùng máy, dữ liệu demo nhỏ. Số request không phải số workflow hoàn tất.

**Demo video còn thiếu:** người học cần quay màn hình mở skill này, JTL/phase metrics thật, chạy kiểm lại con số và nói bằng tiếng Việt của mình; gắn URL Unlisted trong `evidence/video-links.md` và report. File văn bản này không thay thế video.
