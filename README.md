# HW05 Performance Testing — 23120127

**Sinh viên:** 23120127  
**Lớp:** Software Testing / Kiểm thử phần mềm  
**Hệ thống kiểm thử (SUT):** EShop Backend REST API (Node.js + Express + SQLite)  
**Upstream Commit:** `85af3ba875c88283615e22cb108f13e2fccaf0e9`  
**GitHub Repository (Public):** [https://github.com/duongtronghoa/Hw05](https://github.com/duongtronghoa/Hw05)  
**Demo Video (YouTube Unlisted):** Xem trong [evidence/video-links.md](evidence/video-links.md)

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
  * **Spike Test (10 → 80 → 10 VU):** 3.404 request, 0 lỗi; hệ thống chịu được bước nhảy tải gấp 8 lần (Peak 80 VU đạt 38,91 RPS, p95 = 10 ms) và hồi phục ngay lập tức về mức p95 = 9 ms ở Phase 3.
  * **Soak Test (80 VU, 11 phút / 10,5 phút giữ tải sau ramp):** 25.588 request toàn run, 25.018 request trong cửa sổ giữ tải, 0 lỗi.
* **Ngưỡng Chịu Tải Phần Cứng (Endurance Threshold):**
  * *Throughput duy trì tối đa đã kiểm chứng:* **39,711 request/giây** (80 VU có 1–3s think-time).
  * *Độ trễ duy trì (Sustained p95):* **10 ms** (Tất cả endpoint dưới ngưỡng SLA).
  * *Trần bộ nhớ (Memory Ceiling):* Private Bytes của `node.exe` duy trì ổn định ở mức **~96,5 MiB** (không rò rỉ bộ nhớ).
* **Số lỗi / Vấn đề phát hiện:** 3 vấn đề (Khóa tài khoản sai đặc tả FR-02, hổng phân quyền FR-12, PUT/DELETE ID ảo trả về 200 OK).

---

## 2. Bảng Tự Chấm Điểm (Self-Assessment Table)

| STT | Tiêu chí đánh giá (Rubric) | Điểm tối đa | Điểm tự chấm | Minh chứng & Cơ sở đánh giá |
|:---:|---|:---:|:---:|---|
| **1** | **Task 1: Load testing** | 30 | **30** | Test plan đúng chuẩn tên `23120127_Load_20261122.jmx`, Summary Report view, 20 VU chạy 8 phút, raw `load.jtl` đầy đủ, thư mục HTML dashboard và CSV monitor tài nguyên. |
| **2** | **Task 1: Stress testing** | 20 | **20** | Test plan `23120127_Stress_20261122.jmx`, Aggregate Report view, 4 tầng tải 10/20/40/80 VU, phân rã số liệu chi tiết theo từng tầng, xác định rõ điểm suy giảm latency tại 80 VU. |
| **3** | **Task 1: Spike testing** | 20 | **20** | Test plan `23120127_Spike_20261122.jmx`, View Results Tree view, đo đủ 3 phase (Base 10 VU → Peak 80 VU → Recovery 10 VU), phân tích độ hồi phục p95 tức thì. |
| **4** | **Task 2: AI analysis & misinterpretation hunt** | 10 | **10** | Bản phân tích AI gốc `ai-first-pass.md` đóng băng nguyên trạng; bảng săn 5 lỗi AI hiểu sai với số liệu đối chiếu từ JTL thô; đánh giá tính khả thi tối ưu (feasible vs hallucinated); 3 GitHub Issues thực tế. |
| **5** | **Task 3: Continuous Performance Testing proposal (G9.6)** | 10 | **10** | Đề xuất mô hình CI performance testing hoàn chỉnh với Mermaid flow chart và SVG vector; phân tích chuyên sâu trade-offs về chi phí hạ tầng và cảnh báo giả. |
| **6** | **Agent Skill (Bonus)** | 10 | **10** | Đóng gói tái sử dụng tại `skill/hw05-api-performance/SKILL.md`; kịch bản demo end-to-end trên trọn vẹn nhóm Read-heavy (Categories và Products list) với số liệu thật. |
| | **TỔNG ĐIỂM TỰ CHẤM** | **100** | **100** | Đạt mức **100** (Một trăm điểm) theo đúng yêu cầu đề bài và rubric. |

---

## 3. Cấu trúc Thư mục Nộp bài

* `report.md` & `report.pdf`: Báo cáo chính toàn diện.
* `ai-critique.md` & `ai-critique.pdf`: Bản nhận xét AI tiếng Anh (239 từ).
* `ai_audit.md` & `ai_audit.pdf`: Nhật ký AI Audit đầy đủ từ P00 đến P14.
* `plans/`: 3 file kịch bản JMeter (.jmx) Load, Stress, Spike.
* `results/`: 4 thư mục dữ liệu thô (load, stress, spike, soak) chứa `.jtl`, `jmeter.log`, HTML Dashboard và `resources.csv`.
* `evidence/`: Cấu hình phần cứng, storyboard video, link YouTube và ảnh chụp.
* `skill/`: Thư mục Agent Skill và tệp demo.
* `git-commits.txt`: Toàn bộ lịch sử commit Git thật.
