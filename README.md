# HW05 Performance Testing — 23120127

## Trạng thái

- Đã chuẩn bị repo bài làm cục bộ và chọn workflow Admin.
- Đã xác nhận backend EShop chạy ở `http://localhost:3000` và smoke test đủ 6 endpoint trong workflow.
- Đã tạo 100 admin account tổng hợp và 100 CSV riêng cho virtual users; xem `evidence/data-preparation.md`.
- Các test plan Load/Stress/Spike và kết quả đo chưa được tạo; đó là phần sau mục 1–3 của kế hoạch.
- Chưa tạo GitHub repository công khai hoặc xác nhận workflow không trùng với thành viên khác.

## Workflow đã chọn

`Admin Login → Categories List → Products List → Create Category → Update Category → Delete Category`

Chi tiết endpoint, dữ liệu và các lưu ý kiểm thử: [workflow.md](workflow.md).

## SUT

- Source tham chiếu: `../src/eshop-sut`
- Commit upstream: `85af3ba875c88283615e22cb108f13e2fccaf0e9`
- Backend: Node.js + Express + SQLite, port `3000`
- Dữ liệu thử: `data/admin1.csv` … `data/admin100.csv`, tạo bằng `scripts/prepare_admin_data.py`.

## Các mục cần điền sau khi chạy hiệu năng

| Tiêu chí | Điểm tối đa | Tự chấm |
|---|---:|---:|
| Load | 30 | Chưa chấm |
| Stress | 20 | Chưa chấm |
| Spike | 20 | Chưa chấm |
| AI analysis + misinterpretation hunt | 10 | Chưa chấm |
| Continuous Performance Testing proposal | 10 | Chưa chấm |
| Agent Skill | 10 | Chưa chấm |
| **Tổng** | **100** | **Chưa chấm** |

Các số đo, issue, ngưỡng endurance và link video chỉ được bổ sung sau khi có bằng chứng thật.
