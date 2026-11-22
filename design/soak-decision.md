# Quyết định cấu hình soak trước khi chạy

**Thời điểm quyết định:** 2026-11-22, sau Stress và trước Soak.  
**Mức thử:** 80 VU dùng Load JMX, `-Jvus=80 -Jramp=30 -Jduration=660`, think-time 1–3 giây trước mọi request. Duration 660 giây gồm ramp 30 giây và dự kiến ~630 giây (10,5 phút) ở đủ 80 VU.

Stress vừa đo mức 80 VU trong 120 giây: 4.491 request, 0 lỗi; p95 đọc cao nhất 15 ms, p95 auth/ghi cao nhất 32 ms; Node RSS tối đa trên cả Stress 92,98 MiB, JMeter Java 480,33 MiB. Các số này đáp ứng tiêu chí thiết kế cho lượt ngắn, nên 80 VU là mức cao nhất **đã thử và còn ổn trong 2 phút**. Calibration chỉ đo 35 giây/mức. Soak sẽ kiểm tra liệu điều đó giữ được 10,5 phút hay không.

Tiêu chí đánh giá đã chốt ở `test-design.md`: lỗi ≤1%, read p95 ≤500 ms, auth/write p95 ≤2000 ms, không HTTP 500, RAM Node không tăng liên tục không giới hạn. Chỉ tính số ở cửa sổ giữ tải sau ramp; báo cả số toàn run để đối chiếu. Nếu 80 VU đạt, kết luận là **ít nhất** mức 80 VU/RPS đo được ổn định trong khoảng thử trên máy này, chưa tìm được trần tuyệt đối. Nếu không đạt, báo mức thất bại và hạn chế chưa có soak thấp hơn; không tự tuyên bố mức khác ổn định dài hạn.
