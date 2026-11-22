# Calibration ngắn (P05)

Mỗi mức dùng Load plan, ramp 5 giây, tổng 35 giây. Đây là phép đo ngắn, chưa chứng minh độ ổn định dài hạn.

| VU | Requests | Lỗi | RPS toàn run | p95 tất cả (ms) | p95 đọc max (ms) | p95 ghi/xác thực max (ms) | Node RSS max (MiB) | System CPU max (%) |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 5 | 80 | 0 | 2.41 | 7 | 3 | 18 | 61.2 | 16.9 |
| 10 | 158 | 0 | 4.74 | 7 | 3 | 7 | 61.6 | 16.5 |
| 20 | 318 | 0 | 9.61 | 5 | 2 | 8 | 63.8 | 9.0 |
| 40 | 643 | 0 | 19.55 | 5 | 2 | 7 | 67.2 | 8.3 |
| 80 | 1261 | 0 | 37.32 | 5 | 2 | 6 | 78.8 | 10.3 |

Nguồn: `results/calibration/vu*.jtl` và `vu*_resources.csv`. RPS = số request / thời gian từ request đầu đến response cuối; mỗi p95 tính từ mẫu gốc của nhóm tương ứng. Khi scheduler hết hạn, VU có thể dừng giữa CREATE và DELETE: snapshot sau cả 5 lượt có 71 category thử còn lại (xem `results/calibration/post_all_categories.csv`), đã dọn đúng 71 ID/tên để đưa baseline về 3. Việc dọn không sửa JTL.

Tiêu chí dự kiến đã ghi trước đo trong `design/test-design.md`: error ≤1%, read p95 ≤500 ms, auth/write p95 ≤2000 ms, không HTTP 500, không rác category sau khi dọn và kiểm chứng. Mức soak tạm chọn 20 VU để đại diện tải thường; 80 VU chỉ được chứng minh qua 35 giây, cần run dài để đánh giá. Không gọi 80 VU là tối đa tuyệt đối.
