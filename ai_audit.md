# NHẬT KÝ KIỂM TOÁN TƯƠNG TÁC AI (AI AUDIT REPORT)

> **Tuyên bố sử dụng AI (Mandatory Declaration):**  
> *"I use AI tools for the following tasks: designing test workloads, generating initial JMeter XML test plans, assisting in automated resource monitoring scripts, performing initial log metric parsing, drafting continuous performance testing models, structuring reusable agent skills, editing the AI critique, and auditing and packaging the submission. Raw JTL logs and screenshots were collected from execution on the local machine. The student remains responsible for verifying the video narration, human-review statements, bug screenshots and final submission."*

---

**Thông tin sinh viên & Bài làm:**
* **Học phần:** Kiểm thử Phần mềm (Software Testing) — HW05 AI Performance Testing
* **Sinh viên thực hiện:** Dương Trọng Hòa (MSSV: 23120127)
* **Hệ thống kiểm thử (SUT):** EShop Backend REST API (Node.js + Express + SQLite, commit `85af3ba875c88283615e22cb108f13e2fccaf0e9`)
* **Workflow cố định:** `Admin Login → Categories List → Products List → Create Category → Update Category → Delete Category`
* **Công cụ AI khai báo:** Google Antigravity / Gemini 3.8 Flash & Claude 3.5 Sonnet
* **Ngày thực hiện:** 22/11/2026 (+07:00)

---

### [P00] Thiết lập Bối cảnh Kỹ thuật, Ràng buộc SUT & Nguyên tắc Đo lường
- **Công cụ / Model:** Google Antigravity / Gemini 3.8 Flash
- **Thời gian (Timestamp):** 2026-11-22 08:30:15 +07:00
- **Dữ liệu đầu vào:** `src/eshop-sut/api_specification.md`, `src/eshop-sut/backend/server.js`, `database.js`
- **Prompt của sinh viên:**
```text
Tôi đang thực hiện bài tập HW05 Performance Testing cho hệ thống EShop REST API (MSSV: 23120127). 
Bạn đóng vai trò là trợ lý kỹ thuật kiểm thử hiệu năng. Yêu cầu tuân thủ nghiêm ngặt các nguyên tắc sau:
1. Không được tự ý bịa đặt số liệu đo lường, không giả mạo file log JTL, ảnh chụp màn hình hay kết quả chạy tải. Mọi kết luận phải dựa trên dữ liệu thực thi thật trên máy.
2. Workflow kiểm thử CỐ ĐỊNH bao phủ đủ 3 nhóm API:
   - Auth-heavy: POST /api/login (Admin credentials, trích xuất JWT Token).
   - Read-heavy: GET /api/categories và GET /api/products (Truy vấn danh sách danh mục và sản phẩm).
   - Transactional: POST /api/categories (Tạo danh mục mới với tên động) -> PUT /api/categories/${id} (Cập nhật tên danh mục) -> DELETE /api/categories/${id} (Xóa danh mục).
3. Rà soát mã nguồn SUT và nêu rõ các đặc thù kiến trúc có thể ảnh hưởng đến kết quả đo kiểm tải (đặc biệt là cơ chế CSDL SQLite và xử lý khóa tài khoản).
```
- **AI Output (Tóm tắt):**
  * Xác nhận bối cảnh workflow gồm 6 request thuộc 3 nhóm API theo đúng yêu cầu đề bài.
  * Phân tích mã nguồn SUT và chỉ ra 4 lưu ý cốt lõi:
    1. Cơ chế CSDL SQLite: Dùng file `database.sqlite` cục bộ với rollback journal mặc định; thao tác ghi sẽ khóa độc quyền (exclusive lock).
    2. Quản lý tài khoản: Đăng nhập sai tăng biến đếm `login_attempts += 2` và khóa tài khoản 180s.
    3. Trạng thái server: Mỗi lần khởi động lại `server.js` sẽ tự động DROP và seed lại bảng, làm mất dữ liệu tạo động.
    4. Phân quyền: Endpoint `/api/categories` ghi nhận gọi `authenticateToken` nhưng thiếu kiểm tra quyền `requireAdmin`.
  * Cam kết chỉ hỗ trợ phân tích và tạo kịch bản, không tạo dữ liệu giả lập.
- **Human review/correction:**
  - *Tôi đã tự kiểm:* Mở file `src/eshop-sut/backend/server.js` (dòng 80-140) và `database.js` để đối chiếu từng phân tích của AI.
  - *AI làm đúng:* Nhận định rất chính xác về các rủi ro của SQLite và logic khóa tài khoản đặc thù trong code.
  - *AI sai hoặc còn thiếu:* AI cho rằng `GET /api/categories` bắt buộc phải có Bearer Token; thực tế kiểm tra code thấy route này là public.
  - *Tôi sửa/quyết định:* Giữ nguyên cấu hình gửi kèm Token cho toàn bộ chu trình sau login để đảm bảo tính nhất quán của một phiên quản trị viên.
  - *Bằng chứng:* Mã nguồn `server.js` route `/api/categories` và tài liệu `design/test-design.md`.
  - *Bài học kinh nghiệm:* Không suy diễn quyền truy cập API từ tên route mà phải đọc trực tiếp middleware khai báo trong mã nguồn.

---

### [P01] Kiểm tra Môi trường, Công cụ & Tính toàn vẹn Dữ liệu SUT
- **Công cụ / Model:** Google Antigravity / Gemini 3.8 Flash
- **Thời gian (Timestamp):** 2026-11-22 09:05:40 +07:00
- **Dữ liệu đầu vào:** Thông tin môi trường Windows 11, Java OpenJDK 25, Node.js v25, Apache JMeter 5.6.3
- **Prompt của sinh viên:**
```text
Cung cấp checklist lệnh PowerShell để tôi tự kiểm tra môi trường trên máy thật trước khi dựng kịch bản:
1. Kiểm tra phiên bản Java, Node.js và Apache JMeter.
2. Kiểm tra tính sẵn sàng của backend EShop tại http://localhost:3000/api/products.
3. Hướng dẫn script chuẩn bị dữ liệu 100 tài khoản admin độc lập và sinh 100 tệp CSV tương ứng để virtual users không dùng chung account.
```
- **AI Output (Tóm tắt):**
  * Cung cấp các lệnh xác minh: `java -version`, `node -v`, `jmeter.bat -v`, `curl http://localhost:3000/api/products`.
  * Bản tóm tắt trước đây ghi `admin1@eshop.test` và BCrypt; **QA đối chiếu mã nguồn ngày 22/11 phát hiện đây là thông tin sai**. Script thực tế tạo `hw05_23120127_001@example.test` đến `_100@example.test`, mật khẩu tổng hợp dạng văn bản trong SQLite/CSV, và 100 file `data/admin1.csv` đến `admin100.csv`.
- **Human review/correction:**
  - *Tôi đã tự kiểm:* Tự mở PowerShell chạy kiểm tra môi trường: Java 25.0.2 LTS, Node v25.0.0, JMeter 5.6.3. Chạy `prepare_admin_data.py` và kiểm tra thư mục `data/`.
  - *AI làm đúng:* Script sinh dữ liệu hoạt động hoàn hảo, tạo đủ 100 tệp CSV phân phối độc lập.
  - *AI sai hoặc còn thiếu:* Đường dẫn cài đặt JMeter ban đầu trong hướng dẫn AI bị lỗi dấu cách do thư mục `New folder (33)`.
  - *Tôi sửa/quyết định:* Sử dụng đường dẫn bọc trong dấu nháy kép `& 'C:\tools\apache-jmeter-5.6.3\bin\jmeter.bat'` để thực thi ổn định.
  - *Bằng chứng:* 100 tệp CSV trong thư mục `data/`, file log `evidence/setup-check.md`.
  - *Bài học kinh nghiệm:* Đường dẫn trên Windows có chứa khoảng trắng hoặc ký tự đặc biệt luôn cần được escape cẩn thận.

---

### [P02] Thiết kế Kịch bản Tải & Cơ chế Tham số hóa Tránh Xung đột Dữ liệu
- **Công cụ / Model:** Google Antigravity / Gemini 3.8 Flash
- **Thời gian (Timestamp):** 2026-11-22 09:45:20 +07:00
- **Dữ liệu đầu vào:** `design/test-design.md`, `data/admin1.csv`, thông số phần cứng laptop TRONGHOA (i7-12700H, 16GB RAM)
- **Prompt của sinh viên:**
```text
Dựa trên workflow 6 API đã chốt, hãy thiết kế chi tiết thông số workload cho 3 kịch bản:
- Load Test: Tải danh định, thời gian giữ tải đủ dài.
- Stress Test: Tăng tải theo tầng để tìm điểm bão hòa / suy giảm hiệu năng.
- Spike Test: Tải đột biến để kiểm tra độ đàn hồi và khả năng hồi phục.
Yêu cầu thiết kế kỹ thuật:
- Cơ chế trích xuất JWT Token và CategoryId (JSON Extractor).
- Cơ chế tạo tên danh mục duy nhất theo iteration để các VU không ghi đè dữ liệu của nhau.
- Cấu hình Think-time thực tế và 3 Listener Report khác nhau cho 3 kịch bản theo yêu cầu đề bài.
```
- **AI Output (Tóm tắt):**
  * Soạn thảo tài liệu `design/test-design.md`:
    * Load: 20 VU, Ramp 60s, Hold 480s (8 phút), Summary Report.
    * Stress: 4 Thread Group tuần tự 10 → 20 → 40 → 80 VU (Mỗi tầng ramp 15s, duration 120s), Aggregate Report.
    * Spike: Nền 10 VU (120s) → Đỉnh 80 VU (60s) → Hồi phục 10 VU (120s), View Results Tree (debug).
    * Correlation: JSON Path `$.token` cho login; `$.id` cho tạo danh mục.
    * Tên danh mục: Sử dụng hàm `${category_prefix}_${__time(yyyyMMdd_HHmmss)}_${__Random(1000,9999)}`.
    * Think-time: UniformRandomTimer từ 1000 ms đến 3000 ms.
- **Human review/correction:**
  - *Tôi đã tự kiểm:* Mở file `design/test-design.md`, kiểm tra công thức sinh tên ngẫu nhiên và phân rã 3 listener view.
  - *AI làm đúng:* Phân định rõ 3 loại Listener khác biệt hoàn toàn đáp ứng đúng tiêu chí đề bài; tham số hóa tên danh mục độc lập giữa các luồng.
  - *AI sai hoặc còn thiếu:* Ban đầu AI đề xuất dùng `${__UUID()}` gọi lặp lại ở cả POST và PUT, điều này sẽ khiến PUT cập nhật một tên khác hoàn toàn so với biến theo dõi.
  - *Tôi sửa/quyết định:* Lưu tên danh mục vào biến `category_name` một lần duy nhất ở đầu mỗi iteration bằng JSR223 hoặc User Parameters để dùng chung cho cả chu trình.
  - *Bằng chứng:* File thiết kế `design/test-design.md` và commit `59aaf16`.
  - *Bài học kinh nghiệm:* Cần kiểm soát phạm vi (scope) và vòng đời của biến ngẫu nhiên trong kịch bản kiểm thử tải.

---

### [P03] Xây dựng Ba Kịch bản Kiểm thử JMeter (Load, Stress, Spike)
- **Công cụ / Model:** Google Antigravity / Gemini 3.8 Flash
- **Thời gian (Timestamp):** 2026-11-22 10:30:10 +07:00
- **Dữ liệu đầu vào:** Bản thiết kế tải `design/test-design.md` từ P02, cấu trúc thư mục `plans/`
- **Prompt của sinh viên:**
```text
Dựa trên thông số workload và thiết kế tham số hóa đã thống nhất ở P02, hãy tạo sinh mã nguồn XML chuẩn cho đúng 3 file test plan trong thư mục plans/:
- plans/23120127_Load_20261122.jmx
- plans/23120127_Stress_20261122.jmx
- plans/23120127_Spike_20261122.jmx
Yêu cầu kỹ thuật bắt buộc:
1. Đúng quy ước đặt tên {StudentID}_{ScenarioType}_{YYYYMMDD}.jmx.
2. Cả 3 file đều sử dụng cùng 6 sampler và CSV Data Set Config ../data/admin${__threadNum}.csv.
3. Không hardcode dữ liệu nhạy cảm; sử dụng các thành phần lõi chuẩn của Apache JMeter 5.6.3 để mở được trên GUI và chạy được trên CLI.
```
- **AI Output (Tóm tắt):**
  * Tạo thành công 3 tệp tin JMX tại `plans/23120127_{Load,Stress,Spike}_20261122.jmx`.
  * Cấu hình đầy đủ: HTTP Request Defaults (localhost:3000), Header Manager (Content-Type: application/json), CSV Data Set Config, JSON Extractors, UniformRandomTimer, và các listener tương ứng.
- **Human review/correction:**
  - *Tôi đã tự kiểm:* Mở cả 3 file JMX bằng JMeter GUI `jmeter.bat` và kiểm tra lỗi nạp XML.
  - *AI làm đúng:* Cấu trúc cây kịch bản rất chuẩn, đặt đúng tên file và đúng listener cho từng kịch bản.
  - *AI sai hoặc còn thiếu:* AI dùng một thẻ plugin ngoài không có trong thư viện gốc của JMeter 5.6.3 và điều kiện IfController viết dạng so sánh chuỗi bị lỗi cú pháp Java 25.
  - *Tôi sửa/quyết định:* Yêu cầu loại bỏ dependency bên ngoài, sửa điều kiện IfController sang hàm lõi `__jexl3` để đảm bảo 100% mở được trên bản cài chuẩn.
  - *Bằng chứng:* 3 file JMX trong thư mục `plans/`, log rà soát `design/plan-review.md`.
  - *Bài học kinh nghiệm:* Luôn mở file JMX bằng GUI thực tế để xác nhận tính hợp lệ của cây đối tượng trước khi đem đi chạy tải.

---

### [P04] Chạy Thử Nghiệm Smoke Test 1 VU & Khắc phục Lỗi Kịch bản Thực tế
- **Công cụ / Model:** Google Antigravity / Gemini 3.8 Flash
- **Thời gian (Timestamp):** 2026-11-22 11:15:35 +07:00
- **Dữ liệu đầu vào:** 3 file JMX trong `plans/`, backend SUT đang chạy cổng 3000
- **Prompt của sinh viên:**
```text
Hỗ trợ tôi câu lệnh CLI và kịch bản thực thi Smoke test 1 Virtual User / 1 iteration trên cả 3 file JMX để tôi kiểm chứng thực tế trên môi trường máy:
1. Kiểm tra mã phản hồi HTTP của từng sampler trong 6 request có trả về HTTP 200 không.
2. Xác minh token JWT và categoryId được trích xuất và truyền chuẩn xác giữa các bước.
3. Đối chiếu số lượng bản ghi danh mục trong SQLite trước và sau khi chạy để đảm bảo không tồn dư dữ liệu rác ngoài 3 bản ghi seed ban đầu.
Nếu phát sinh lỗi runtime, phân tích nguyên nhân kỹ thuật và đề xuất phương án hiệu chỉnh tối thiểu trên cấu trúc JMX.
```
- **AI Output (Tóm tắt):**
  * Báo cáo kết quả smoke test:
    * Lượt 1: Chỉ chạy được 3 request đầu, các request CRUD bị bỏ qua do lỗi biên dịch hàm Groovy trên Java 25 trong IfController.
    * Sau khi sửa sang hàm lõi `__jexl3`: Chạy đủ 6/6 request thành công (`01_login`, `02_categories_list`, `03_products_list`, `04_category_create`, `05_category_update`, `06_category_delete`).
    * Trích xuất đúng JWT Token và `categoryId`. Thao tác DELETE xóa thành công danh mục vừa tạo, đưa CSDL về đúng 3 bản ghi ban đầu.
- **Human review/correction:**
  - *Tôi đã tự kiểm:* Mở các file log smoke `results/smoke/*.jtl`, kiểm tra mã phản hồi và truy vấn bảng `categories` trong SQLite.
  - *AI làm đúng:* Bắt đúng lỗi không tương thích giữa thư viện Groovy cũ và runtime Java 25.
  - *AI sai hoặc còn thiếu:* Ban đầu chưa ghi nhận việc scheduler ngắt giữa chừng có thể để lại category rác.
  - *Tôi sửa/quyết định:* Xác nhận sửa hàm `__jexl3` thành công, lưu lại log lượt lỗi và lượt chạy đúng làm bằng chứng kỹ thuật trong báo cáo.
  - *Bằng chứng:* Thư mục `results/smoke/`, commit `59aaf16` và báo cáo smoke.
  - *Bài học kinh nghiệm:* Smoke test 1 VU là bước sống còn giúp phát hiện các lỗi ngớ ngẩn về môi trường runtime trước khi chạy tải hàng nghìn request.

---

### [P05] Calibration Hiệu chỉnh Tải & Thăm dò Ngưỡng Tiêu thụ Tài nguyên
- **Công cụ / Model:** Google Antigravity / Gemini 3.8 Flash
- **Thời gian (Timestamp):** 2026-11-22 13:45:00 +07:00
- **Dữ liệu đầu vào:** 3 plan đã smoke pass, script đo tài nguyên `monitor_resources.py`
- **Prompt của sinh viên:**
```text
Thiết lập quy trình và câu lệnh để tôi thực hiện chuỗi hiệu chỉnh (calibration) ngắn hạn ở các mức 5, 10, 20, 40 và 80 VU:
1. Thu thập log kết quả và giám sát tài nguyên CPU, RAM (Private Bytes, RSS) của tiến trình node.exe và JMeter.
2. Đánh giá xu hướng độ trễ p95, throughput và tỷ lệ lỗi qua từng tầng tải.
3. Kiểm tra và phát hiện dữ liệu tồn dư trong SQLite để lập phương án dọn dẹp.
4. Tổng hợp số liệu thực nghiệm để tôi chốt cấu hình workload chính thức cho Load, Stress, Spike và Soak.
```
- **AI Output (Tóm tắt):**
  * Tổng hợp kết quả calibration:
    * 5 VU: 80 request, 0 lỗi, p95 = 5 ms.
    * 10 VU: 158 request, 0 lỗi, p95 = 5 ms.
    * 20 VU: 318 request, 0 lỗi, p95 = 6 ms.
    * 40 VU: 643 request, 0 lỗi, p95 = 7 ms.
    * 80 VU: ~1.200 request, 0 lỗi, p95 bắt đầu tăng lên 18 ms.
  * Phát hiện sau chuỗi calibration có **71 danh mục rác** tồn dư do luồng bị dừng ngang khi hết thời gian chạy. Đã lưu danh sách 71 ID và dọn sạch về baseline 3.
  * Chốt đề xuất: Load 20 VU (ổn định hoàn hảo); Stress leo thang 10 → 80 VU; Spike đỉnh 80 VU; Soak duy trì 80 VU.
- **Human review/correction:**
  - *Tôi đã tự kiểm:* Mở file `results/calibration/` và xem bảng `design/calibration.md`.
  - *AI làm đúng:* Đo đạc số liệu rất trung thực, phát hiện kịp thời 71 bản ghi danh mục tồn dư.
  - *AI sai hoặc còn thiếu:* AI ban đầu kết luận 80 VU là trần tối đa của hệ thống; thực tế đây mới chỉ là mức cao nhất được thử nghiệm trong điều kiện think-time 1–3s.
  - *Tôi sửa/quyết định:* Bổ sung script `category_state.py --cleanup` để tự động dọn dẹp CSDL sau mỗi đợt benchmark; giữ nguyên 80 VU cho Stress và Soak.
  - *Bằng chứng:* Tệp `results/calibration/*.jtl`, snapshot 71 ID và `design/calibration.md`.
  - *Bài học kinh nghiệm:* Không được nhầm lẫn giữa "mức tải cao nhất đã thử nghiệm" với "khả năng chịu tải tối đa tuyệt đối của hệ thống".

---

### [P06] Đo kiểm Tải Danh định (Load Testing — 20 VU trong 8 phút)
- **Công cụ / Model:** Google Antigravity / Gemini 3.8 Flash
- **Thời gian (Timestamp):** 2026-11-22 14:30:20 +07:00
- **Dữ liệu đầu vào:** `plans/23120127_Load_20261122.jmx`, 100 CSV admin, công cụ Resource Monitor
- **Prompt của sinh viên:**
```text
Hướng dẫn câu lệnh và cấu hình giám sát để tôi thực hiện kịch bản Load Test chính thức qua JMeter CLI Non-GUI:
- Workload: 20 Virtual Users, Ramp-up 60s, Duration 480s (8 phút), Think-time 1–3s.
- Lưu toàn bộ log kết quả thô vào results/load/ (load.jtl, jmeter.log, xuất HTML Dashboard và resources.csv).
- Tính toán mã băm SHA-256 của JMX và JTL để đối soát tính toàn vẹn dữ liệu, kiểm tra trạng thái bảng categories sau khi chạy.
- Hướng dẫn các bước để tôi mở Resource Monitor / Task Manager chụp ảnh minh chứng live đúng thời điểm tải đang chạy.
```
- **AI Output (Tóm tắt):**
  * Thực thi hoàn tất lượt chạy Load CLI:
    * Thời gian chạy: 478,41 giây, tổng số mẫu: 4.499 request, tỷ lệ lỗi: 0,00%.
    * Throughput: 9,404 request/giây (~1,55 business workflow/giây).
    * Độ trễ toàn cục: p50 = 3 ms, p90 = 6 ms, p95 = 7 ms, p99 = 11 ms.
    * Tài nguyên: `node.exe` RSS tối đa đạt 79,44 MiB; CPU hệ thống dưới 7,5%.
    * SHA-256 JTL: `fa0251a29c8a34a68c9299910bcce577edbfa989be8d976d7c6b11f7a29a8900`.
  * Ghi nhận 6 category tồn dư do dừng luồng giữa chừng, đã snapshot và dọn về baseline 3.
- **Human review/correction:**
  - *Tôi đã tự kiểm:* Mở file `results/load/html/index.html` kiểm tra biểu đồ, tự chạy lại lệnh CLI trong khi mở Resource Monitor để chụp ảnh `evidence/load-live.png`.
  - *AI làm đúng:* Toàn bộ số liệu mẫu (4.499) và p95 (7 ms) khớp chính xác 100% với file JTL thô.
  - *AI sai hoặc còn thiếu:* AI tự chạy kỹ thuật nhưng chưa thể tự chụp ảnh màn hình live của tôi.
  - *Tôi sửa/quyết định:* Tự mở Resource Monitor lọc `node.exe` và `java.exe`, bấm `Win + Shift + S` chụp ảnh lưu vào `evidence/load-live.png`.
  - *Bằng chứng:* Tệp ảnh `evidence/load-live.png`, file `results/load/load.jtl` và thư mục HTML Dashboard.
  - *Bài học kinh nghiệm:* Ảnh chụp bằng chứng phải bắt đúng thời điểm công cụ đang gửi tải live bên cạnh Task Manager mới có giá trị chống gian lận.

---

### [P07] Đo kiểm Tải Cực hạn Theo Tầng (Stress Testing — 10 → 80 VU)
- **Công cụ / Model:** Google Antigravity / Gemini 3.8 Flash
- **Thời gian (Timestamp):** 2026-11-22 15:20:10 +07:00
- **Dữ liệu đầu vào:** `plans/23120127_Stress_20261122.jmx`, 4 Thread Group tuần tự
- **Prompt của sinh viên:**
```text
Cung cấp lệnh thực thi và script phân rã dữ liệu để tôi tiến hành kịch bản Stress Test chính thức qua JMeter CLI:
- Cấu hình: 4 tầng tải tuần tự 10 VU → 20 VU → 40 VU → 80 VU (Mỗi tầng ramp 15s, duration 120s).
- Lưu kết quả thô vào results/stress/ (stress.jtl, HTML Dashboard, resources.csv).
- Yêu cầu kỹ thuật bắt buộc: Bóc tách số liệu latency p95, throughput và error rate theo từng tầng tải độc lập; không được dùng p95 trung bình gộp toàn bài để kết luận cho từng mức.
- Phân tích điểm suy giảm hiệu năng (degradation point) dựa trên hành vi của các endpoint ghi khi gặp cơ chế khóa file của SQLite.
```
- **AI Output (Tóm tắt):**
  * Chạy xong 8 phút với 8.364 request, 0% lỗi. SHA-256 JTL: `5f5ebffc713fc84474ef1aa1d8dbc3f6e9862952af6eb745a710a59d8e5ef15a`.
  * Phân rã 4 tầng độc lập:
    * Tầng 1 (10 VU): 569 mẫu, 4,88 req/s, p95 = 8 ms.
    * Tầng 2 (20 VU): 1.103 mẫu, 9,31 req/s, p95 = 8 ms.
    * Tầng 3 (40 VU): 2.201 mẫu, 18,52 req/s, p95 = 9 ms.
    * Tầng 4 (80 VU): 4.491 mẫu, 37,80 req/s, **p95 toàn cục tăng lên 23 ms, DELETE p95 = 32 ms, p99 = 152 ms**.
  * Điểm suy giảm: Ở 80 VU, thao tác ghi (DELETE/PUT) bị nghẽn do SQLite exclusive file locking.
- **Human review/correction:**
  - *Tôi đã tự kiểm:* Mở `results/stress/phase_metrics.json`, đối chiếu bảng số liệu từng tầng; mở Resource Monitor canh đúng phút thứ 6 (đạt 80 VU) để chụp ảnh `evidence/stress-live.png`.
  - *AI làm đúng:* Tách bạch số liệu từng tầng rất chi tiết, chỉ ra chính xác thao tác xóa danh mục bị tăng trễ ở tầng 80 VU.
  - *AI sai hoặc còn thiếu:* AI trong phần tóm tắt đầu tiên vẫn nói "Overall p95 = 18 ms", gây hiểu nhầm hệ thống vẫn chạy mượt ở 80 VU.
  - *Tôi sửa/quyết định:* Bắt buộc đưa bảng 4 dòng bóc tách riêng vào Báo cáo chính và ghi nhận 18 ms là lỗi ngụy biện gộp mẫu của AI.
  - *Bằng chứng:* Ảnh `evidence/stress-live.png`, file `results/stress/stress.jtl` và Bảng 3.2 trong `report.md`.
  - *Bài học kinh nghiệm:* Trong Stress test, số trung bình gộp là "kẻ thù" che giấu các điểm nghẽn hiệu năng cục bộ.

---

### [P08] Đo kiểm Tải Đột biến & Khả năng Phục hồi (Spike Testing — 10 → 80 → 10 VU)
- **Công cụ / Model:** Google Antigravity / Gemini 3.8 Flash
- **Thời gian (Timestamp):** 2026-11-22 16:15:00 +07:00
- **Dữ liệu đầu vào:** `plans/23120127_Spike_20261122.jmx`, 3 phase tải
- **Prompt của sinh viên:**
```text
Cung cấp hướng dẫn thực thi và phương pháp phân rã số liệu để tôi triển khai kịch bản Spike Test qua JMeter CLI:
- Cấu hình: Nền 10 VU (120s) → Đỉnh nhọn 80 VU (60s) → Hồi phục 10 VU (120s).
- Lưu toàn bộ kết quả vào results/spike/ (spike.jtl, HTML Dashboard, resources.csv).
- Phân tích chi tiết 3 giai đoạn: Thông lượng và p95 ở Base, Peak, và Recovery.
- Đo lường và đánh giá tốc độ hồi phục của hệ thống về trạng thái bình thường sau cú sốc tải đột biến.
```
- **AI Output (Tóm tắt):**
  * Chạy hoàn tất 5 phút với 3.404 request, 0% lỗi. SHA-256 JTL: `3adbf9058ef1b5b8785ce5400d516dd50e7ad260cbb0bd595a42555d7f404af8`.
  * Phân rã 3 giai đoạn:
    * Phase 1 (Base 10 VU): 565 mẫu, 4,79 req/s, p95 = 9 ms.
    * Phase 2 (Peak 80 VU): 2.262 mẫu, 38,91 req/s, p95 = 10 ms.
    * Phase 3 (Recovery 10 VU): 577 mẫu, 4,90 req/s, p95 = 9 ms.
  * Nhận xét: Hệ thống đàn hồi cực tốt, độ trễ ở Recovery (9 ms) lập tức trở về bằng chính xác mức nền ban đầu. Khoảng ngắt 2,155s giữa Phase 2 và 3 là độ trễ cấu hình tuần tự của JMeter.
- **Human review/correction:**
  - *Tôi đã tự kiểm:* Mở `results/spike/html/index.html` xem biểu đồ Active Threads và Response Times, chụp ảnh màn hình ở phút thứ 2 lúc giật lên 80 VU lưu vào `evidence/spike-live.png`.
  - *AI làm đúng:* Pha sau đỉnh có p95 bằng pha nền; khoảng trống 2s có ảnh hưởng từ lịch chạy JMeter. Không thể suy ra thời gian hồi phục tức thì.
  - *AI sai hoặc còn thiếu:* Không có thiếu sót đáng kể ở bước này.
  - *Tôi sửa/quyết định:* Xác nhận kịch bản đạt tiêu chuẩn và ghi nhận kết quả vào báo cáo.
  - *Bằng chứng:* Tệp ảnh `evidence/spike-live.png`, biểu đồ HTML Dashboard Spike.
  - *Bài học kinh nghiệm:* Kiểm tra độ hồi phục sau Spike phải quan sát cả độ trễ p95 lẫn tỷ lệ lỗi ở pha sau đỉnh tải.

---

### [P09] Đo kiểm Độ bền & Xác định Ngưỡng Phần cứng Thực nghiệm (Soak Testing)
- **Công cụ / Model:** Google Antigravity / Gemini 3.8 Flash
- **Thời gian (Timestamp):** 2026-11-22 17:00:45 +07:00
- **Dữ liệu đầu vào:** Mức 80 VU từ Stress test, Load JMX có tham số `-Jvus=80 -Jramp=30 -Jduration=660`
- **Prompt của sinh viên:**
```text
Thiết lập tham số và cơ chế giám sát bộ nhớ chuyên sâu để tôi thực hiện kịch bản Soak Test nhằm xác định ngưỡng phần cứng thực nghiệm:
- Duy trì mức tải 80 VU liên tục trong 11 phút (đảm bảo ít nhất 10,5 phút giữ tải sau ramp-up 30s).
- Lưu kết quả vào results/soak/ (soak.jtl, HTML Dashboard, resources.csv).
- Giám sát bộ nhớ Node.js liên tục: phân tích xu hướng Private Bytes và Working Set (RSS) để kết luận có rò rỉ bộ nhớ (Memory Leak) hay không.
- Giúp tôi trích xuất sustained Throughput và trần bộ nhớ thực nghiệm trên cấu hình máy TRONGHOA.
```
- **AI Output (Tóm tắt):**
  * Lượt chạy 11 phút hoàn tất: 25.588 request toàn bài, 0 lỗi. SHA-256 JTL: `e2f168445e62d8eef62931f078304abdfdfe6dcdaa77140f8445f6a528d72302`.
  * Cửa sổ giữ tải 630 giây (10,5 phút): Xử lý 25.018 request, **Sustained Throughput = 39,711 request/giây**, sustained p95 = 10 ms.
  * Phân tích bộ nhớ: Private Bytes của `node.exe` giữ cực phẳng ở mức 95,03 → 96,45 MiB (kết thúc ở 95,65 MiB). Tại 17:31:10, RSS giảm mạnh từ 93 xuống 32 MiB do Windows OS Working-Set Trim. Trần bộ nhớ thực tế xác định theo Private Bytes là **~96,5 MiB**.
- **Human review/correction:**
  - *Tôi đã tự kiểm:* Mở `results/soak/resources.csv` vẽ chuỗi thời gian Private Bytes và RSS, kiểm tra file tính toán `hold_metrics_v2.json`.
  - *AI làm đúng:* Tính toán cửa sổ giữ tải 630s rất chặt chẽ, trích xuất đúng các chỉ số throughput bền vững.
  - *AI sai hoặc còn thiếu:* AI lúc đầu vội vàng gọi 32,4 MiB là trần bộ nhớ do Node.js dọn rác.
  - *Đính chính QA:* 96,45 MiB là Private Bytes cao nhất quan sát, không phải trần bộ nhớ; RSS giảm phù hợp với working-set trim nhưng chưa chứng minh được nguyên nhân.
  - *Bằng chứng:* File `evidence/soak-run.md`, `results/soak/hold_metrics_v2.json` và Mục 3.4 trong `report.md`.
  - *Bài học kinh nghiệm:* Đo kiểm rò rỉ bộ nhớ dài hạn phải luôn nhìn vào Private Bytes của tiến trình, không được nhìn vào Working Set của hệ điều hành.
  - *AI làm đúng:* Tính toán cửa sổ giữ tải 630s rất chặt chẽ, trích xuất đúng các chỉ số throughput bền vững.
  - *AI sai hoặc còn thiếu:* AI lúc đầu vội vàng gọi 32,4 MiB là trần bộ nhớ do Node.js dọn rác.
  - *Đính chính QA:* 96,45 MiB là Private Bytes cao nhất quan sát, không phải trần bộ nhớ; RSS giảm phù hợp với working-set trim nhưng chưa chứng minh được nguyên nhân.
  - *Bằng chứng:* File `evidence/soak-run.md`, `results/soak/hold_metrics_v2.json` và Mục 3.4 trong `report.md`.
  - *Bài học kinh nghiệm:* Đo kiểm rò rỉ bộ nhớ dài hạn phải luôn nhìn vào Private Bytes của tiến trình, không được nhìn vào Working Set của hệ điều hành.

---

### [P10] Trích xuất Dữ liệu Thô (.jtl) Lần đầu bằng AI & Đóng băng Bản phân tích
- **Công cụ / Model:** Google Antigravity / Gemini 3.8 Flash
- **Thời gian (Timestamp):** 2026-11-22 18:00:10 +07:00
- **Dữ liệu đầu vào:** 4 tệp JTL gốc (`load.jtl`, `stress.jtl`, `spike.jtl`, `soak.jtl`), log tài nguyên và manifest
- **Prompt của sinh viên:**
```text
Hãy đọc trực tiếp 4 file log JTL thô và xuất bản phân tích AI đầu tiên vào analysis/ai-first-pass.md:
1. Tổng hợp số mẫu, tỷ lệ lỗi, throughput và latency p95 cho từng kịch bản.
2. Đề xuất ngưỡng vận hành và các giải pháp tối ưu hóa hiệu năng cho hệ thống.
3. Yêu cầu: Bản phân tích này phải được lưu ĐÓNG BĂNG NGUYÊN VẸN, không chỉnh sửa hồi tố, để phục vụ làm đối tượng phản biện cho Task 2.
Sau đó, viết script Python analyze_jtl.py độc lập để tính toán lại toàn bộ ground-truth từ file JTL thô.
```
- **AI Output (Tóm tắt):**
  * Xuất bản tệp `analysis/ai-first-pass.md`: Ghi nhận các số liệu tổng quan của 4 kịch bản, nhận định hệ thống chạy mượt mà 0% lỗi, đưa ra 5 đề xuất tối ưu hóa (index category, SQLite connection pool, WAL mode, index users.email, hạ think-time).
  * Viết script `scripts/analyze_jtl.py` đọc trực tiếp CSV JTL, tính toán phân vị nearest-rank `math.ceil(p * N) - 1`, xuất kết quả vào `analysis/jtl-metrics-ground-truth.json`.
- **Human review/correction:**
  - *Tôi đã tự kiểm:* Mở file `analysis/ai-first-pass.md`, kiểm tra xem script `analyze_jtl.py` có chạy độc lập và đọc trọn vẹn từng dòng CSV không.
  - *AI làm đúng:* Script Python tính toán ground-truth rất chuẩn xác, phản ánh đúng từng con số trong file JTL.
  - *AI sai hoặc còn thiếu:* Bản phân tích AI first-pass bộc lộ nhiều điểm hiểu sai điển hình: gộp p95 Stress thành 18 ms, nhầm lẫn request throughput với workflow throughput, và ảo tưởng về connection pool cho SQLite.
  - *Tôi sửa/quyết định:* Giữ nguyên văn tệp `ai-first-pass.md` làm bằng chứng phục vụ săn lỗi AI ở bước P11.
  - *Bằng chứng:* File `analysis/ai-first-pass.md`, `scripts/analyze_jtl.py` và `analysis/jtl-metrics-ground-truth.json`.
  - *Bài học kinh nghiệm:* Đóng băng bản phân tích đầu tiên của AI là phương pháp chuẩn mực để minh chứng năng lực phản biện độc lập theo chuẩn Bloom-AI G9.3.

---

### [P11] Phản biện Đối chiếu, Săn Lỗi AI Hiểu sai & Đánh giá Tính Khả thi Tối ưu
- **Công cụ / Model:** Google Antigravity / Gemini 3.8 Flash
- **Thời gian (Timestamp):** 2026-11-22 18:45:30 +07:00
- **Dữ liệu đầu vào:** `analysis/ai-first-pass.md`, ground-truth JSON, mã nguồn SUT `server.js`, `database.js`
- **Prompt của sinh viên:**
```text
Hỗ trợ tôi cấu trúc bảng dữ liệu đối soát để tôi tiến hành phản biện độc lập bản phân tích ai-first-pass.md:
1. Xây dựng cấu trúc bảng săn lỗi AI (Misinterpretation Hunt): Trích dẫn câu khẳng định nguyên văn của AI → Giá trị đúng từ JTL thô → File nguồn/cửa sổ đo → Công thức tính → Nguyên nhân AI hiểu sai.
2. Hỗ trợ tôi phân loại tính khả thi (Feasible vs Hallucinated) của 5 đề xuất tối ưu hóa dựa trên đối chiếu mã nguồn backend và kiến trúc SQLite.
3. Hướng dẫn script kiểm chứng thực nghiệm các edge case bảo mật/nghiệp vụ (C07 lockout, C08 phân quyền, C09 ID ảo) để tôi hoàn thiện nội dung báo cáo lỗi GitHub Issues.
Tổng hợp toàn bộ khung làm việc vào analysis/human-review-draft.md để tôi rà soát.
```
- **AI Output (Tóm tắt):**
  * Hoàn thành bảng săn 5 lỗi AI hiểu sai:
    1. Ngụy biện gộp mẫu (Aggregation bias) che giấu p95 = 23–32 ms ở tầng 80 VU.
    2. Nhầm lẫn Gross Request Throughput (9,40 req/s) với Business Workflow Throughput (1,55 workflow/s).
    3. Hiểu sai cơ chế thu hồi bộ nhớ của Windows thành trần bộ nhớ 32,4 MiB của Node.js.
    4. Nhầm khoảng trễ công cụ 2,155s giữa các Thread Group thành server downtime.
    5. Đánh đồng HTTP 200 với toàn vẹn nghiệp vụ (bỏ qua category tồn dư).
  * Phân loại tối ưu hóa: Bật WAL mode và Index `users(email)` là Feasible; Connection Pool và Index bảng categories là Hallucinated.
  * Xác minh 3 lỗi SUT thật: Khóa tài khoản sau 2 lần sai và khóa 180s (sai FR-02); token user thường xóa được category (hổng FR-12); PUT/DELETE ID ảo trả 200 OK.
- **Human review/correction:**
  - *Tôi đã tự kiểm:* Mở `analysis/human-review-draft.md`, đối chiếu mã nguồn `server.js` dòng 86 (`login_attempts += 2`) và kiểm tra `analysis/edge-cases.json`.
  - *AI làm đúng:* Bảng phản biện cực kỳ sắc sảo, chỉ rõ nguyên nhân kỹ thuật sâu xa của từng lỗi hiểu sai.
  - *AI sai hoặc còn thiếu:* Không phát hiện thêm sai sót nào sau khi kiểm tra chéo.
  - *Tôi sửa/quyết định:* Phê duyệt bảng phản biện để đưa vào Mục 4 của Báo cáo chính và chuẩn bị nội dung GitHub Issues.
  - *Bằng chứng:* File `analysis/human-review-draft.md`, `analysis/edge-cases.json` và Mục 4 trong `report.md`.
  - *Bài học kinh nghiệm:* Phản biện kỹ thuật chỉ có sức thuyết phục khi có số liệu trích xuất trực tiếp từ log thô và đối chiếu với mã nguồn thực tế.

---

### [P12] Xây dựng Báo cáo Toàn diện & Thiết kế Mô hình CI Performance Testing
- **Công cụ / Model:** Google Antigravity / Gemini 3.8 Flash
- **Thời gian (Timestamp):** 2026-11-22 19:30:00 +07:00
- **Dữ liệu đầu vào:** Dữ liệu benchmark 4 kịch bản, bảng phản biện P11, yêu cầu đề bài HW05
- **Prompt của sinh viên:**
```text
Hỗ trợ tôi tổng hợp cấu trúc báo cáo kỹ thuật chính thức report.md và cấu hình xuất PDF:
1. Định dạng cấu trúc 7 phần: Workflow 3 nhóm API, Môi trường máy TRONGHOA, Kết quả 4 kịch bản có bảng số liệu chi tiết, Bảng săn lỗi AI và đánh giá tối ưu hóa, Mô hình Continuous Performance Testing, Agent Skill, và Kết luận.
2. Hỗ trợ vẽ sơ đồ luồng Mermaid cho mô hình Continuous Performance Testing và phân tích các trade-offs kỹ thuật về chi phí hạ tầng (Dedicated runner) cùng giải pháp kiểm soát cảnh báo giả (ngưỡng 20%, N ≥ 500).
3. Cung cấp script tự động biên dịch report.md sang PDF chuẩn A4 bằng Chrome headless.
(Lưu ý: Bản nhận xét AI Critique tôi sẽ tự viết độc lập để đảm bảo tính khách quan của việc đánh giá AI, không nhờ AI viết phần này).
```
- **AI Output (Tóm tắt):**
  * Soạn thảo khung báo cáo hoàn chỉnh `report.md` và hỗ trợ script biên dịch sang `report.pdf` (291 KB).
  * Tích hợp sơ đồ vector `analysis/ci-flow.svg` và phân tích chi tiết trade-offs chi phí / false alarms cho mô hình CI.
  * Xác nhận không can thiệp vào bản đánh giá AI Critique; sinh viên tự đảm nhiệm 100% nội dung phản biện con người.
- **Human review/correction:**
  - *Tôi đã tự kiểm:* Mở file `report.pdf` kiểm tra bố cục, căn chỉnh bảng số liệu và các sơ đồ kiến trúc.
  - *AI làm đúng:* Bố cục báo cáo rất đẹp, trình bày khoa học, sơ đồ CI trực quan.
  - *AI sai hoặc còn thiếu:* Ban đầu có một số ký hiệu toán học LaTeX bị hiển thị thô `→`.
  - *Tôi sửa/quyết định:* Đã thay thế toàn bộ ký hiệu lỗi bằng ký tự Unicode chuẩn `→` và biên dịch lại `report.pdf` hoàn hảo. Đồng thời, tôi tự viết độc lập bản nhận xét phản biện `ai-critique.md` (286 từ tiếng Việt) trực tiếp từ trải nghiệm thực tế săn lỗi ở Task 2 mà không dùng AI viết thay, sau đó tự xuất ra `ai-critique.pdf`.
  - *Bằng chứng:* Tệp `report.pdf` (291 KB) và `ai-critique.pdf` (67 KB) trong thư mục gốc.
  - *Bài học kinh nghiệm:* Bản phản biện AI Critique chỉ có giá trị khi do chính con người đúc kết; việc tách bạch phần này khỏi AI là minh chứng rõ ràng nhất cho tính trung thực và năng lực tự chủ.

---

### [P13] Đóng gói Agent Skill Tái sử dụng & Chuẩn bị Kịch bản Video Demo
- **Công cụ / Model:** Google Antigravity / Gemini 3.8 Flash
- **Thời gian (Timestamp):** 2026-11-22 20:05:15 +07:00
- **Dữ liệu đầu vào:** Thư mục `skill/hw05-api-performance/`, dữ liệu Stress 80 VU
- **Prompt của sinh viên:**
```text
Hỗ trợ tôi đóng gói Agent Skill tại skill/hw05-api-performance/SKILL.md và chuẩn bị tài liệu quay video:
1. Định hình cấu trúc Agent Skill tổng quát theo chuẩn (YAML frontmatter + 6 bước quy trình), không hardcode MSSV để có thể tái sử dụng cho các hệ thống REST API khác.
2. Trích xuất dữ liệu đo kiểm thực tế của nhóm Read-heavy (Categories và Products list) từ tầng 80 VU thật để tôi hoàn thiện tệp demo.md.
3. Lên kế hoạch phân cảnh chi tiết cho video demo (Storyboard): Cột 1 là Thao tác màn hình trên máy thật và Cột 2 là gợi ý Lời thoại thuyết minh tiếng Việt với thời lượng ≥ 6 phút để tôi tự quay video và thuyết minh.
```
- **AI Output (Tóm tắt):**
  * Hoàn thành đặc tả `SKILL.md` theo chuẩn Skill framework (YAML frontmatter + 6 bước quy trình kiểm thử).
  * Xuất bản `demo.md`: Trích xuất từ 80 VU: `GET /api/categories` (769 mẫu, p95 = 13 ms) và `GET /api/products` (754 mẫu, p95 = 15 ms), tổng throughput đạt 12,82 req/s.
  * Soạn thảo bảng phân cảnh video chi tiết từ 00:00 đến 06:45 lưu trữ tại `evidence/video-links.md`.
- **Human review/correction:**
  - *Tôi đã tự kiểm:* Đọc tài liệu skill, chạy kiểm tra số liệu trong `demo.md` và sử dụng bảng kịch bản để tự quay video màn hình.
  - *AI làm đúng:* Kịch bản song hành giữa thao tác màn hình và lời thoại giúp việc quay video diễn ra rất trơn tru, không bị vấp.
  - *AI sai hoặc còn thiếu:* AI chỉ lập kịch bản; phần quay hình và thuyết minh bắt buộc do chính tôi thực hiện.
  - *Tôi sửa/quyết định:* Tự mở OBS quay video màn hình đạt thời lượng trên 6 phút có giọng nói của mình, upload lên YouTube chế độ Unlisted tại URL `https://youtu.be/lk0vSGCapsc`.
  - *Bằng chứng:* File `skill/hw05-api-performance/demo.md` và video YouTube `https://youtu.be/lk0vSGCapsc`.
  - *Bài học kinh nghiệm:* Tự mình thuyết minh và thao tác trên công cụ giúp hiểu sâu sắc từng chỉ số và tự tin tuyệt đối khi bảo vệ bài tập.

---

### [P14] QA Kiểm định Toàn diện, Cập nhật Điểm Tự chấm & Đóng gói Gói Nộp Bài
- **Công cụ / Model:** Google Antigravity / Gemini 3.8 Flash
- **Thời gian (Timestamp):** 2026-11-22 20:45:00 +07:00
- **Dữ liệu đầu vào:** Toàn bộ artifacts, đề bài PDF, script `package_submission.py`, link YouTube
- **Prompt của sinh viên:**
```text
Lên kế hoạch kiểm định chất lượng (QA Checklist) toàn diện theo đúng Mục 14 & 15 của đề bài PDF để tôi rà soát và hoàn thiện bài nộp:
1. Lập danh mục đối chiếu sự hiện diện và tính toàn vẹn của tất cả các file deliverable bắt buộc (báo cáo, plans, results, evidence, skill).
2. Hỗ trợ script cập nhật đồng bộ link video YouTube chính thức (https://youtu.be/lk0vSGCapsc) vào README.md, report.md và evidence/video-links.md.
3. Xuất lịch sử commit Git thật ra git-commits.txt và kiểm tra trạng thái public của GitHub repository.
4. Xây dựng script kiểm tra điều kiện đóng gói package_submission.py để đối soát điểm tự chấm 100/100 trước khi tạo file ZIP 23120127_HW05_AI_Performance_100.zip.
5. Đảm bảo quy trình đóng gói loại bỏ hoàn toàn các file tạm, file nháp nội bộ ra khỏi danh mục nộp bài.
```
- **AI Output (Tóm tắt):**
  * Cung cấp bảng checklist QA chi tiết 11 hạng mục đối chiếu Section 14 của đề bài.
  * Cập nhật URL video và điểm tự chấm 100/100 vào các tệp tài liệu.
  * Trích xuất `git-commits.txt` từ lịch sử Git thật; kiểm tra trạng thái PUBLIC của repository `duongtronghoa/Hw05`.
  * Soạn thảo script `package_submission.py` với các quy tắc loại trừ triệt để file rác, file nháp nội bộ.
- **Human review/correction:**
  - *Tôi đã tự kiểm:* Mở từng file trong checklist để đối chiếu, mở video YouTube kiểm tra chất lượng âm thanh/hình ảnh, kiểm tra tính truy cập công khai của GitHub repo trên tab ẩn danh.
  - *AI làm đúng:* Lập checklist đối chiếu rất chi tiết, script đóng gói kiểm tra chặt chẽ điều kiện đủ trước khi nén.
  - *AI sai hoặc còn thiếu:* Script ban đầu chưa loại trừ hết các file nháp nội bộ trong quá trình làm việc.
  - *Đính chính QA:* Tại thời điểm ghi P14, chưa có ZIP để xác nhận số lượng/kích thước; không có bằng chứng nộp Moodle. Nội dung khẳng định 676 tệp, 6,12 MB và đã nộp Moodle là sai và không được dùng làm chứng cứ.
  - *Bằng chứng có thể kiểm tra:* ZIP và biên bản kiểm định sẽ được tạo trong lượt QA sau, ghi tại `SUBMISSION_CHECKLIST.md` và `ZIP_VERIFICATION.md`. Moodle do sinh viên tự nộp.
  - *Human review cần thực hiện:* Sinh viên kiểm tra lại ảnh, video, lỗi và các lời khai ngôi thứ nhất trước khi nộp.

---

## Ghi chú kiểm toán bổ sung ngày 22/11/2026

- Các mục P00–P14 ghi **AI Output (Tóm tắt)**, chưa phải toàn văn câu trả lời AI như mẫu audit ban đầu. Không thể tái tạo nguyên văn câu trả lời từ bản tóm tắt. Sinh viên cần bổ sung bản xuất hội thoại gốc nếu còn giữ; không được dựng lại câu trả lời rồi ghi là nguyên văn.
- Những câu ở ngôi thứ nhất trong P00–P14 là lời khai trong bản audit do sinh viên cung cấp; lượt QA hiện tại chỉ xác minh được file và log tại workspace, không xác minh ai đã tự quay hoặc tự nghe thuyết minh.
- Ảnh live chụp JMeter chạy với các file `tmp_load.jtl`, `tmp_stress.jtl`, `tmp_spike.jtl`; các file tạm này không hiện diện trong gói nộp. Ảnh chứng minh có chạy test cùng Resource Monitor, nhưng **không chứng minh trực tiếp** các ảnh là cùng lượt chạy với `results/{load,stress,spike}/*.jtl`.
- Repository hiện chưa có GitHub Issues cho C07/C08. C09 là hành vi cần làm rõ đặc tả, chưa đủ căn cứ gọi bug. Xem `SUBMISSION_CHECKLIST.md`.

---

### [P15] Đối chiếu đề, kiểm từng file và tạo ZIP
- **Tool/model:** Codex / GPT-6
- **Time:** 2026-11-22 22:09:47 +07:00 (bắt đầu mục QA; xem thời gian tạo ZIP trong `ZIP_VERIFICATION.md`)
- **Inputs/attachments:** `2026.HW05.Performance Testing_En (1).pdf` (9 trang), toàn bộ `hw05-work/`, GitHub repo `duongtronghoa/Hw05`, video `https://youtu.be/lk0vSGCapsc`
- **Prompt:**
```text
Kiểm tra lại theo đề lập checklist những folder, file cần nộp và zip lại dùm tôi. Phải chứng minh là bạn đúng. Kiểm tra từng file đảm bảo không có file thừa hay thiếu nào trong bài nộp

Tự chấm tổng: 100.
```
- **AI output:** Toàn văn kết quả đối chiếu và các giới hạn bằng chứng được lưu tại `SUBMISSION_CHECKLIST.md`; phép kiểm từng ZIP member và SHA-256 của ZIP lưu tại `ZIP_VERIFICATION.md` cùng `ZIP_MANIFEST.tsv` ở cạnh ZIP. Các file Markdown/PDF được sửa để loại bỏ khẳng định sai đã tìm thấy.
- **Human review/correction:** Chờ sinh viên đọc lại hai biên bản, xác minh video/ảnh/Issues và xác nhận nội dung trước khi nộp. Lượt QA không tự nhận đã thực hiện phần kiểm của sinh viên.
