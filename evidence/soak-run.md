# Soak 80 VU, ngày 2026-11-22

Quyết định mức tải/tiêu chí trước run: `design/soak-decision.md`. Dùng Load JMX, `-Jvus=80 -Jramp=30 -Jduration=660`; think-time 1–3 giây trước mọi request. Backend PID 3420, Java JMeter PID 27756, cùng máy.

- JMeter Thread Group bắt đầu `17:21:03.921 +07:00`; cửa sổ **giữ tải sau ramp** từ `17:21:33.921` tới `17:32:03.921`, 630 giây = 10,5 phút.
- Raw `results/soak/soak.jtl`: 25.588 request toàn run, SHA-256 `e2f168445e62d8eef62931f078304abdfdfe6dcdaa77140f8445f6a528d72302`. `jmeter.log`, `html/index.html`, `resources.csv`, `manifest.json` cùng thư mục.
- Trong cửa sổ giữ tải: **25.018 request, 0 lỗi, 39,711 request/giây, p95 toàn request 10 ms**. Đây là request RPS, không phải workflow/s. Nhãn `06_category_delete` có 4.163 mẫu (~6,608 request/s), nhưng số DELETE cũng không tự chứng minh mọi iteration nghiệp vụ thành công nếu SUT trả 200 cho ID sai.

| Label | n trong hold | p95 (ms) | Lỗi |
|---|---:|---:|---:|
| `01_login` | 4.172 | 8 | 0 |
| `02_categories_list` | 4.174 | 7 | 0 |
| `03_products_list` | 4.175 | 7 | 0 |
| `04_category_create` | 4.166 | 13 | 0 |
| `05_category_update` | 4.168 | 12 | 0 |
| `06_category_delete` | 4.163 | 13 | 0 |

Nguồn phép tính: `results/soak/hold_metrics_v2.json` từ JTL và mốc log, **không** lấy p95 trung bình của các nhãn. Tất cả p95 dưới tiêu chí dự kiến (read 500 ms, auth/write 2.000 ms) trong lượt này. 80 VU và 39,711 RPS là mức **cao nhất đã thử và đạt** trong 10,5 phút trên laptop này; chưa tìm được trần RPS/tải tối đa, không thể khẳng định máy chủ riêng sẽ giống vậy.

Node private memory trong hold 95,82 → 95,65 MiB, min 95,03, max 96,45 MiB, chưa thấy tăng không giới hạn trong 10,5 phút. Node RSS 93,11 → 32,38 MiB vì khoảng `17:31:10` RSS của cả Node và JMeter đều bị cắt mạnh trong khi private memory gần như giữ nguyên. Đây **có thể là working-set trim của Windows**, chưa xác định nguyên nhân cụ thể; không gọi 32,38 MiB là “memory ceiling” hay bằng chứng ứng dụng giải phóng RAM. Java JMeter RSS tối đa 652,66 MiB, private tối đa 1.254,67 MiB; system CPU tối đa 17,32% theo CSV monitor.

Snapshot `results/soak/categories_after.csv` ghi 24 category HW05 còn lại do scheduler dừng giữa workflow; đã dọn đúng 24 ID/tên, baseline trở lại 3. Chưa có ảnh Task Manager/CLI cùng khung hoặc video người học; cần quay bổ sung.
