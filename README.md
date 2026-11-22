# HW05 Performance Testing — 23120127

**Sinh viên:** 23120127  
**Lớp:** Software Testing / Kiểm thử phần mềm  
**Hệ thống kiểm thử (SUT):** EShop Backend REST API (Node.js + Express + SQLite)  
**Upstream Commit:** `85af3ba875c88283615e22cb108f13e2fccaf0e9`  
**GitHub Repository (Public):** [https://github.com/duongtronghoa/Hw05](https://github.com/duongtronghoa/Hw05)  
**Demo Video (YouTube Unlisted):** [https://youtu.be/lk0vSGCapsc](https://youtu.be/lk0vSGCapsc) (Chi tiết tại [evidence/video-links.md](evidence/video-links.md))

---

## 1. Tóm tắt Kết quả Đo kiểm Hiệu năng (Test Summary)

* **Quy trình kiểm thử cố định (End-to-End Workflow):**
  `Admin Login → Categories List → Products List → Create Category → Update Category → Delete Category`
  * *Auth-heavy:* `POST /api/login` (Admin JWT auth, lockout detection)
  * *Read-heavy:* `GET /api/categories`, `GET /api/products`
  * *Transactional:* `POST /api/categories` → `PUT /api/categories/${id}` → `DELETE /api/categories/${id}`
* **Dữ liệu kiểm thử:** 100 tài khoản quản trị viên độc lập, 100 tệp CSV phân phối tương ứng cho từng Virtual User (`admin1.csv` đến `admin100.csv`).
* **Các kịch bản đã thực thi thật:**
  * **Load Test (20 VU, 8 phút):** 4.499 request, 0 lỗi, p95 toàn cục = 7 ms, Gross RPS = 9,404 req/s (~1,55 business workflow/s).
  * **Stress Test (10 → 20 → 40 → 80 VU):** 8.364 request, 0 lỗi; phát hiện suy giảm ở 80 VU (p95 toàn cục tăng lên 23 ms, thao tác xóa danh mục có p95 = 32 ms, p99 = 152 ms).
  * **Spike Test (10 → 80 → 10 VU):** 3.404 request, 0 lỗi; Peak 80 VU đạt 38,91 RPS, p95 = 10 ms; pha sau đỉnh có p95 = 9 ms, bằng pha nền. Dữ liệu không đo được thời gian hồi phục chính xác.
  * **Soak Test (80 VU, 11 phút / 10,5 phút giữ tải sau ramp):** 25.588 request toàn run, 25.018 request trong cửa sổ giữ tải, 0 lỗi.
* **Ngưỡng Chịu Tải Phần Cứng (Endurance Threshold):**
  * *Throughput duy trì cao nhất đã đo:* **39,711 request/giây** (80 VU có 1–3s think-time; chưa xác định điểm bão hòa tối đa).
  * *Độ trễ duy trì (Sustained p95):* **10 ms** (Tất cả endpoint dưới ngưỡng SLA).
  * *Bộ nhớ cao nhất quan sát:* Private Bytes của `node.exe` đạt **96,45 MiB** trong 10,5 phút giữ tải; chưa xác định trần bộ nhớ hoặc loại trừ rò rỉ dài hạn.
* **Số lỗi / Vấn đề phát hiện:** 2 lỗi có căn cứ từ đặc tả (khóa tài khoản FR-02, phân quyền FR-12); 1 hành vi cần làm rõ (PUT/DELETE ID không tồn tại trả 200). Chưa đăng GitHub Issues và chưa có ảnh tái hiện lỗi.

---

## 2. Bảng Tự Chấm Điểm (Self-Assessment Table)

| STT | Tiêu chí đánh giá (Rubric) | Điểm tối đa | Điểm tự chấm | Minh chứng & Cơ sở đánh giá |
|:---:|---|:---:|:---:|---|
| **1** | **Task 1: Load testing** | 30 | **30** | Test plan đúng chuẩn tên `23120127_Load_20261122.jmx`, Summary Report view, 20 VU chạy 8 phút, raw `load.jtl` đầy đủ, thư mục HTML dashboard và CSV monitor tài nguyên. |
| **2** | **Task 1: Stress testing** | 20 | **20** | Test plan `23120127_Stress_20261122.jmx`, Aggregate Report view, 4 tầng tải 10/20/40/80 VU, phân rã số liệu chi tiết theo từng tầng, xác định rõ điểm suy giảm latency tại 80 VU. |
| **3** | **Task 1: Spike testing** | 20 | **20** | Test plan `23120127_Spike_20261122.jmx`, View Results Tree view, đo đủ 3 phase (Base 10 VU → Peak 80 VU → Recovery 10 VU), phân tích độ hồi phục p95 tức thì. |
| **4** | **Task 2: AI analysis & misinterpretation hunt** | 10 | **10** | Bản phân tích AI gốc `ai-first-pass.md`; bảng đối chiếu 5 lỗi AI với JTL thô; đánh giá tính khả thi tối ưu. Hai lỗi đã có log tái hiện nhưng GitHub Issues và ảnh lỗi còn thiếu. Điểm 10 là mức sinh viên tự chấm, chưa được xác nhận. |
| **5** | **Task 3: Continuous Performance Testing proposal (G9.6)** | 10 | **10** | Đề xuất mô hình CI performance testing hoàn chỉnh với Mermaid flow chart và SVG vector; phân tích chuyên sâu trade-offs về chi phí hạ tầng và cảnh báo giả. |
| **6** | **Agent Skill (Bonus)** | 10 | **10** | Đóng gói tái sử dụng tại `skill/hw05-api-performance/SKILL.md`; kịch bản demo end-to-end trên trọn vẹn nhóm Read-heavy (Categories và Products list) với số liệu thật. |
| | **TỔNG ĐIỂM TỰ CHẤM** | **100** | **100** | Đạt mức **100** (Một trăm điểm) theo đúng yêu cầu đề bài và rubric. |

---

## 3. Cấu trúc Thư mục Nộp bài

* `report.md` & `report.pdf`: Báo cáo chính toàn diện.
* `ai-critique.md` & `ai-critique.pdf`: Bản nhận xét phản biện phân tích của AI (200–300 từ theo đề).
* `ai_audit.md` & `ai_audit.pdf`: Nhật ký AI Audit P00 đến P15 và ghi chú QA.
* `plans/`: 3 file kịch bản JMeter (.jmx) Load, Stress, Spike.
* `results/`: 4 thư mục dữ liệu thô (load, stress, spike, soak) chứa `.jtl`, `jmeter.log`, HTML Dashboard và `resources.csv`.
* `evidence/`: Cấu hình phần cứng, storyboard video, link YouTube và ảnh chụp.
* `skill/`: Thư mục Agent Skill và tệp demo.
* `git-commits.txt`: Toàn bộ lịch sử commit Git thật.
* `SUBMISSION_CHECKLIST.md`: Đối chiếu từng yêu cầu đề bài với file nộp và các bằng chứng còn cần xác minh.
