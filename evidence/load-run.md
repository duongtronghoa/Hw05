# Load run 2026-11-22

- Backend PID: 3420; SUT commit `85af3ba875c88283615e22cb108f13e2fccaf0e9`.
- JMeter 5.6.3 CLI, 20 VU, ramp 60 s, duration 480 s, UniformRandomTimer 1–3 s trước mỗi request.
- JMX SHA-256: `d84f72b49e73404e83723136351c2fa242d85110848f078469e7f5f681f5a02d`.
- Raw JTL: `results/load/load.jtl`, SHA-256 `fa0251a29c8a34a68c9299910bcce577edbfa989be8d976d7c6b11f7a29a8900`; 4.499 mẫu, 0 lỗi JMeter. Log và HTML tại `results/load/jmeter.log`, `results/load/html/index.html`.
- Node RSS tối đa 79,44 MiB theo `results/load/resources.csv`; JMeter resource CSV chỉ có một mẫu đang chạy, chưa có chuỗi client đủ dài.
- 6 category HW05 tồn dư do scheduler dừng giữa iteration. Đã lưu `results/load/categories_after.csv` rồi dọn đúng 6 ID/tên, baseline 3.
- Thiếu ảnh Task Manager + JMeter cùng khung và video giọng Việt tại thời điểm chạy. Người học cần quay lượt bổ sung; không dùng file đo tài nguyên thay ảnh/video.
