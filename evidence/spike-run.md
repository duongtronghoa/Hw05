# Spike run 2026-11-22

- Backend PID 3420; JMeter 5.6.3 CLI; nền 10 VU/120 s/ramp 10 s, spike 80 VU/60 s/ramp 5 s, hồi phục 10 VU/120 s/ramp 5 s; think-time 1–3 s trước mọi request.
- JTL `results/spike/spike.jtl`, SHA-256 `3adbf9058ef1b5b8785ce5400d516dd50e7ad260cbb0bd595a42555d7f404af8`; 3.404 mẫu, 0 `success=false`. Log, HTML, monitor, manifest và phân tích phase ở cùng thư mục.

| Phase | Requests | Lỗi | RPS | p95 tất cả (ms) |
|---|---:|---:|---:|---:|
| Base 10 VU | 565 | 0 | 4,785 | 9 |
| Peak 80 VU | 2.262 | 0 | 38,907 | 10 |
| Recovery 10 VU | 577 | 0 | 4,902 | 9 |

RPS là request/s trong khoảng có request của từng Thread Group (gồm ramp); không phải workflow/s. Khoảng từ response cuối Peak đến request đầu Recovery là 2,155 s, tương thích với chuyển nhóm tuần tự và think-time; **không coi là downtime**. Recovery p95 bằng Base p95 trong lượt này, nên không đo được thời gian phục hồi sau suy giảm vì không có suy giảm rõ. Node RSS tối đa 93,19 MiB; JMeter Java RSS tối đa 324,36 MiB.

Snapshot `results/spike/categories_after.csv` ghi 43 category HW05 tồn dư; sau khi dọn đúng 43 ID/tên baseline là 3. View Results Tree trong JMX được tắt khi CLI; người học có thể mở JTL trong GUI để debug/xem listener trước khi tuyên bố đã dùng view này. Chưa có ảnh/video trực tiếp.
