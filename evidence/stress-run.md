# Stress run 2026-11-22

- Backend PID 3420; JMeter 5.6.3 CLI, bốn Thread Group tuần tự 10/20/40/80 VU, mỗi mức ramp 15 s và duration 120 s, think-time 1–3 s trước mọi request. Tổng 8.364 mẫu, 0 `success=false`; JTL SHA-256 `5f5ebffc713fc84474ef1aa1d8dbc3f6e9862952af6eb745a710a59d8e5ef15a`.
- JTL/log/HTML/resources và manifest: `results/stress/stress.jtl`, `jmeter.log`, `html/index.html`, `resources.csv`, `manifest.json`; số theo tầng ở `phase_metrics.json`.

| Tầng VU | Request | Lỗi | RPS theo khoảng request | p95 tất cả (ms) | p95 đọc cao nhất (ms) | p95 auth/ghi cao nhất (ms) |
|---:|---:|---:|---:|---:|---:|---:|
| 10 | 569 | 0 | 4,879 | 8 | 2 | 9 |
| 20 | 1.103 | 0 | 9,310 | 8 | 2 | 13 |
| 40 | 2.201 | 0 | 18,521 | 9 | 6 | 11 |
| 80 | 4.491 | 0 | 37,796 | 23 | 15 | 32 |

Các p95 tính từ toàn bộ mẫu của từng Thread Group, bao gồm ramp; không phải p95 của riêng đoạn hold. RPS = số request / khoảng từ request đầu tới response cuối của tầng; không phải workflow/s. Node RSS tối đa 92,98 MiB, Java JMeter RSS tối đa 480,33 MiB theo 99 mẫu monitor; CPU% được chia trên tổng logical CPU của máy.

Sau run có 49 category HW05 tồn dư. Snapshot ID/tên ở `results/stress/categories_after.csv`, sau đó dọn đúng 49 ID/tên và baseline còn 3. Chưa có ảnh/video trực tiếp do người học chưa thể quay; phải bổ sung lượt quay cùng khung trước khi nộp.
