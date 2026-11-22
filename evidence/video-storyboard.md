# Khung quay video HW05 (người học tự quay và thuyết minh)

**Bằng chứng hiện tại:** chưa có video/ảnh trong lúc chạy. Những JTL hiện có là lượt đo kỹ thuật không ghi hình. Không dựng hình ảnh tài nguyên từ CSV để gọi là ảnh Task Manager.

## Chuẩn bị trước khi bấm Record

1. Cắm nguồn máy, tắt các tác vụ nặng khác; xác nhận hostname `TRONGHOA` có khớp bài trước. Mở Task Manager > Details/Performance, nhận diện `node.exe` backend và `java.exe` JMeter bằng PID. Có thể dùng Process Explorer nếu Task Manager không hiện PID, nhưng ảnh nộp cần rõ CPU/RAM backend.
2. Mở JMeter GUI để cho thấy tên plan/ba listener; khi chạy tải chính dùng CLI để tránh GUI tiêu tốn RAM. Đặt cửa sổ CLI/JMeter và Task Manager cạnh nhau, cả hai **cùng một khung**. Điều chỉnh tỷ lệ chữ đủ đọc. Che email/mật khẩu và JWT nếu hiện.
3. Mở OBS Studio hoặc Windows Snipping Tool/Screen Recorder, kiểm tra mic thật bằng clip thử 15 giây. Chọn vùng màn hình chứa cả hai cửa sổ. Ghi giờ và tên run trong file riêng. Chuẩn bị dung lượng trống cho video, JTL và HTML.
4. Xác nhận backend PID 3000, 100 admin CSV, baseline 3 categories. Nếu restart Node, chạy lại `scripts/prepare_admin_data.py` rồi đếm lại; không chạy hai JMeter cùng lúc.

## Nội dung video tối thiểu 6 phút

| Thời điểm gợi ý | Cảnh cần thấy | Ý để tự nói bằng tiếng Việt của mình |
|---|---|---|
| 0:00–0:45 | Hostname, cấu hình máy, workflow sáu API | Mục tiêu, ba nhóm endpoint, dữ liệu CSV. |
| 0:45–1:45 | Load CLI/JMeter + Task Manager trong cùng khung | 20 VU, ramp/hold/think-time, tài nguyên Node, JTL/HTML sau chạy. |
| 1:45–2:45 | Stress; có ít nhất một đoạn tầng cao | 10/20/40/80 VU, khi nào p95/lỗi thay đổi, phân biệt Node và JMeter. |
| 2:45–3:45 | Spike từ nền lên 80 rồi hồi phục | Mốc phase, p95/error/RPS từng phase, thời gian hồi phục. |
| 3:45–4:45 | Soak/resource CSV + Task Manager lúc đang chạy | 10–15 phút giữ tải sau ramp, ngưỡng cao nhất đã thử, giới hạn kết luận. |
| 4:45–5:45 | JTL gốc, AI first pass, human correction | Chỉ đúng một lỗi/thiếu sót AI thật và phép kiểm từ JTL; không bịa lỗi. |
| 5:45–6:45+ | `skill/hw05-api-performance/SKILL.md` và demo nhóm read-heavy | Cho thấy skill được gọi, hai endpoint `02_categories_list`/`03_products_list`, output từ run thật. |

Có thể ghi dài từng run rồi cắt đoạn, hoặc chia clip theo scenario; tổng clip unlisted ≥6 phút. Giữ mốc thời gian và số đo thật. Với mỗi Load/Stress/Spike, chụp ít nhất một ảnh trong lúc lệnh đang chạy có tool + Task Manager cùng khung. Sau khi upload YouTube dạng Unlisted, mở link bằng cửa sổ ẩn danh để chắc người chấm xem được. Điền URL và tổng thời lượng vào report/README; không để placeholder trong bản nộp.
