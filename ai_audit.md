# NHẬT KÝ KIỂM TOÁN TƯƠNG TÁC AI (AI AUDIT REPORT)

> **Tuyên bố sử dụng AI (Mandatory Declaration):**  
> *"I use AI tools for the following tasks: designing test workloads, generating initial JMeter XML test plans, assisting in automated resource monitoring scripts, performing initial log metric parsing, drafting continuous performance testing models, and structuring reusable agent skills. All test execution, raw log generation, ground-truth metric recalculation, AI misinterpretation hunting, live evidence capture, Vietnamese video demonstration, and final evaluations were independently verified and executed by the student."*

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
  - *Bằng chứng:* Mã nguồn `server.js` route `/api/categories` và tài liệu `workflow.md`.
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
  * Soạn thảo script `scripts/prepare_admin_data.py`: chèn trực tiếp 100 tài khoản admin tổng hợp (`admin1@eshop.test` đến `admin100@eshop.test`) vào bảng `users` trong SQLite với mật khẩu mã hóa BCrypt (`admin123`), đồng thời xuất ra 100 file `data/admin1.csv` đến `data/admin100.csv` chứa `email,password,category_prefix`.
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
- **Dữ liệu đầu vào:** `workflow.md`, `data/admin1.csv`, thông số phần cứng laptop TRONGHOA (i7-12700H, 16GB RAM)
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
    * Stress: 4 Thread Group tuần tự 10 $\rightarrow$ 20 $\rightarrow$ 40 $\rightarrow$ 80 VU (Mỗi tầng ramp 15s, duration 120s), Aggregate Report.
    * Spike: Nền 10 VU (120s) $\rightarrow$ Đỉnh 80 VU (60s) $\rightarrow$ Hồi phục 10 VU (120s), View Results Tree (debug).
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
- **Dữ liệu đầu vào:** `design/test-design.md`, cấu trúc thư mục `plans/`
- **Prompt của sinh viên:**
```text
Hãy tạo sinh mã nguồn XML chuẩn cho đúng 3 file test plan trong thư mục plans/:
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
Thực thi lệnh Smoke test 1 Virtual User / 1 iteration trên cả 3 file JMX để kiểm chứng thực tế:
1. Xác minh từng sampler trong 6 request có trả về HTTP 200 không.
2. Kiểm tra xem Token JWT và categoryId có được truyền chính xác giữa các sampler không.
3. Kiểm tra số lượng bản ghi danh mục trong CSDL trước và sau khi chạy: có đảm bảo được xóa sạch để giữ nguyên baseline 3 danh mục seed không?
Nếu có lỗi, phân tích nguyên nhân và sửa đổi tối thiểu trên JMX.
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
Tiến hành chạy hiệu chỉnh (calibration) ngắn hạn ở các mức 5, 10, 20, 40 và 80 VU:
1. Lưu log kết quả và đo CPU, RAM (Private Bytes, RSS) của backend node.exe và Java JMeter.
2. Đánh giá tính ổn định, độ trễ p95 và tỷ lệ lỗi ở từng mức.
3. Kiểm tra tình trạng dữ liệu tồn dư trong SQLite sau mỗi mức.
4. Chốt cấu hình chính thức cho Load, Stress, Spike và kịch bản đo độ bền (Soak).
```
- **AI Output (Tóm tắt):**
  * Tổng hợp kết quả calibration:
    * 5 VU: 80 request, 0 lỗi, p95 = 5 ms.
    * 10 VU: 158 request, 0 lỗi, p95 = 5 ms.
    * 20 VU: 318 request, 0 lỗi, p95 = 6 ms.
    * 40 VU: 643 request, 0 lỗi, p95 = 7 ms.
    * 80 VU: ~1.200 request, 0 lỗi, p95 bắt đầu tăng lên 18 ms.
  * Phát hiện sau chuỗi calibration có **71 danh mục rác** tồn dư do luồng bị dừng ngang khi hết thời gian chạy. Đã lưu danh sách 71 ID và dọn sạch về baseline 3.
  * Chốt đề xuất: Load 20 VU (ổn định hoàn hảo); Stress leo thang 10 $\rightarrow$ 80 VU; Spike đỉnh 80 VU; Soak duy trì 80 VU.
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
Thực thi đo kiểm kịch bản Load Test chính thức bằng lệnh JMeter CLI Non-GUI:
- Thông số: 20 Virtual Users, Ramp-up 60s, Duration 480s (8 phút), Think-time 1-3s.
- Lưu toàn bộ kết quả thô vào results/load/ (file load.jtl, jmeter.log, HTML Dashboard, resources.csv).
- Ghi nhận đầy đủ mã băm SHA-256 của file JMX và JTL, kiểm tra số lượng category tồn dư sau khi chạy để dọn dẹp.
- Hướng dẫn tôi thao tác mở Task Manager / Resource Monitor để chụp ảnh live cùng khung hình.
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

### [P07] Đo kiểm Tải Cực hạn Theo Tầng (Stress Testing — 10 $\rightarrow$ 80 VU)
- **Công cụ / Model:** Google Antigravity / Gemini 3.8 Flash
- **Thời gian (Timestamp):** 2026-11-22 15:20:10 +07:00
- **Dữ liệu đầu vào:** `plans/23120127_Stress_20261122.jmx`, 4 Thread Group tuần tự
- **Prompt của sinh viên:**
```text
Thực thi kịch bản Stress Test chính thức bằng JMeter CLI Non-GUI:
- Cấu hình: 4 tầng tuần tự 10 VU -> 20 VU -> 40 VU -> 80 VU (Mỗi tầng ramp 15s, duration 120s).
- Xuất dữ liệu vào results/stress/ (stress.jtl, HTML Dashboard, resources.csv).
- Yêu cầu đặc biệt: Bóc tách số liệu latency p95, throughput và lỗi theo TỪNG TẦNG TẢI ĐỘC LẬP; không được dùng p95 trung bình của toàn bài để kết luận cho từng mức.
- Xác định rõ điểm suy giảm hiệu năng (degradation point) xuất hiện ở đâu.
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

### [P08] Đo kiểm Tải Đột biến & Khả năng Phục hồi (Spike Testing — 10 $\rightarrow$ 80 $\rightarrow$ 10 VU)
- **Công cụ / Model:** Google Antigravity / Gemini 3.8 Flash
- **Thời gian (Timestamp):** 2026-11-22 16:15:00 +07:00
- **Dữ liệu đầu vào:** `plans/23120127_Spike_20261122.jmx`, 3 phase tải
- **Prompt của sinh viên:**
```text
Thực thi kịch bản Spike Test chính thức bằng JMeter CLI Non-GUI:
- Cấu hình: Nền 10 VU (120s) -> Đỉnh nhọn 80 VU (60s) -> Hồi phục 10 VU (120s).
- Lưu kết quả vào results/spike/ (spike.jtl, HTML Dashboard, resources.csv).
- Phân tích chi tiết 3 giai đoạn: Thông lượng và p95 ở Base, Peak, và Recovery.
- Đo thời gian hệ thống hồi phục về trạng thái bình thường sau cú sốc tải.
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
  - *AI làm đúng:* Nhận định đúng về khả năng hồi phục tức thì của backend và làm rõ bản chất khoảng trễ 2s là do công cụ JMeter.
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
Thực thi kịch bản Soak Test để tìm ngưỡng chịu tải phần cứng thực nghiệm theo yêu cầu đề bài:
- Duy trì mức tải 80 VU liên tục trong 11 phút (đảm bảo ít nhất 10,5 phút sau khoảng ramp-up 30s).
- Lưu trữ toàn bộ kết quả vào results/soak/ (soak.jtl, HTML Dashboard, resources.csv).
- Giám sát bộ nhớ Node.js liên tục: phân tích xu hướng Private Bytes và Working Set (RSS) để kết luận có rò rỉ bộ nhớ (Memory Leak) hay không.
- Xác định sustained RPS và trần bộ nhớ thực nghiệm trên laptop TRONGHOA.
```
- **AI Output (Tóm tắt):**
  * Lượt chạy 11 phút hoàn tất: 25.588 request toàn bài, 0 lỗi. SHA-256 JTL: `e2f168445e62d8eef62931f078304abdfdfe6dcdaa77140f8445f6a528d72302`.
  * Cửa sổ giữ tải 630 giây (10,5 phút): Xử lý 25.018 request, **Sustained Throughput = 39,711 request/giây**, sustained p95 = 10 ms.
  * Phân tích bộ nhớ: Private Bytes của `node.exe` giữ cực phẳng ở mức 95,03 $\rightarrow$ 96,45 MiB (kết thúc ở 95,65 MiB). Tại 17:31:10, RSS giảm mạnh từ 93 xuống 32 MiB do Windows OS Working-Set Trim. Trần bộ nhớ thực tế xác định theo Private Bytes là **~96,5 MiB**.
- **Human review/correction:**
  - *Tôi đã tự kiểm:* Mở `results/soak/resources.csv` vẽ chuỗi thời gian Private Bytes và RSS, kiểm tra file tính toán `hold_metrics_v2.json`.
  - *AI làm đúng:* Tính toán cửa sổ giữ tải 630s rất chặt chẽ, trích xuất đúng các chỉ số throughput bền vững.
  - *AI sai hoặc còn thiếu:* AI lúc đầu vội vàng gọi 32,4 MiB là trần bộ nhớ do Node.js dọn rác.
  - *Tôi sửa/quyết định:* Đính chính trong báo cáo: trần bộ nhớ phải là 96,5 MiB dựa trên Private Bytes, hiện tượng giảm RSS là do hệ điều hành Windows thu hồi trang nhớ vật lý.
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
Thực hiện phản biện độc lập đối với bản phân tích ai-first-pass.md:
1. Lập bảng săn lỗi AI (Misinterpretation Hunt): Trích dẫn câu khẳng định nguyên văn của AI -> Giá trị đúng từ JTL thô -> File nguồn/cửa sổ đo -> Công thức tính -> Nguyên nhân AI hiểu sai.
2. Đánh giá tính khả thi (Feasible vs Hallucinated) của 5 đề xuất tối ưu hóa đối chiếu với mã nguồn và kiến trúc SQLite.
3. Chạy kiểm chứng thực nghiệm các edge case (C07 lockout, C08 phân quyền, C09 ID ảo) và soạn thảo dự thảo GitHub Issues.
Ghi toàn bộ vào analysis/human-review-draft.md.
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

### [P12] Xây dựng Báo cáo Toàn diện, Đề xuất Mô hình CI & Viết AI Critique
- **Công cụ / Model:** Google Antigravity / Gemini 3.8 Flash
- **Thời gian (Timestamp):** 2026-11-22 19:30:00 +07:00
- **Dữ liệu đầu vào:** Dữ liệu benchmark 4 kịch bản, bảng phản biện P11, yêu cầu đề bài HW05
- **Prompt của sinh viên:**
```text
Tổng hợp toàn bộ quá trình kiểm thử thành báo cáo chính thức report.md và xuất bản PDF:
1. Cấu trúc đầy đủ 7 phần: Workflow 3 nhóm API, Môi trường máy TRONGHOA, Kết quả 4 kịch bản có bảng số liệu chi tiết, Bảng săn lỗi AI và đánh giá tối ưu hóa, Mô hình Continuous Performance Testing, Agent Skill, và Kết luận.
2. Mô hình CI (G9.6 Disrupt): Vẽ sơ đồ luồng Mermaid và phân tích sâu sắc trade-offs về chi phí hạ tầng (Dedicated runner) và giải pháp kiểm soát cảnh báo giả (ngưỡng 20%, N >= 500).
3. Soạn thảo ai-critique.md thuần tiếng Việt đúng 200-300 từ trả lời đủ 3 câu hỏi của đề bài.
4. Biên dịch toàn bộ ra PDF chuẩn A4 bằng Chrome headless.
```
- **AI Output (Tóm tắt):**
  * Soạn thảo hoàn chỉnh `report.md` và xuất ra `report.pdf` (291 KB).
  * Soạn thảo `ai-critique.md` (286 từ tiếng Việt) và xuất ra `ai-critique.pdf` (67 KB).
  * Tích hợp sơ đồ vector `analysis/ci-flow.svg` và phân tích trade-offs chi phí / false alarms.
- **Human review/correction:**
  - *Tôi đã tự kiểm:* Mở file `report.pdf` và `ai-critique.pdf` kiểm tra số trang, đếm số từ bản Critique (286 từ) và kiểm tra lỗi chính tả/ký tự.
  - *AI làm đúng:* Bố cục báo cáo rất đẹp, trình bày khoa học, sơ đồ CI trực quan.
  - *AI sai hoặc còn thiếu:* Ban đầu có một số ký hiệu toán học LaTeX bị hiển thị thô `$\rightarrow$`.
  - *Tôi sửa/quyết định:* Đã thay thế toàn bộ ký hiệu lỗi bằng ký tự Unicode chuẩn `→` và biên dịch lại PDF hoàn hảo.
  - *Bằng chứng:* Hai file PDF `report.pdf` và `ai-critique.pdf` trong thư mục gốc.
  - *Bài học kinh nghiệm:* Báo cáo nộp bài cần được trau chuốt cả về tính chuẩn xác của số liệu lẫn tính chuyên nghiệp của định dạng văn bản.

---

### [P13] Đóng gói Agent Skill Tái sử dụng & Chuẩn bị Kịch bản Video Demo
- **Công cụ / Model:** Google Antigravity / Gemini 3.8 Flash
- **Thời gian (Timestamp):** 2026-11-22 20:05:15 +07:00
- **Dữ liệu đầu vào:** Thư mục `skill/hw05-api-performance/`, dữ liệu Stress 80 VU
- **Prompt của sinh viên:**
```text
Đóng gói Agent Skill hoàn chỉnh tại skill/hw05-api-performance/SKILL.md:
1. Đảm bảo tính tổng quát, không gắn cứng MSSV hay schema Category, có thể tái sử dụng cho bất kỳ REST API nào.
2. Thực hiện demo thực tế trên TRỌN VẸN nhóm Read-heavy (Categories và Products list) từ dữ liệu tầng 80 VU thật, ghi rõ kết quả vào demo.md.
3. Soạn bảng kịch bản quay video song hành chi tiết: Cột 1 là Thao tác màn hình (mở cửa sổ nào, click vào đâu) và Cột 2 là Lời thoại thuyết minh tiếng Việt chuẩn thời lượng >= 6 phút.
```
- **AI Output (Tóm tắt):**
  * Hoàn thành đặc tả `SKILL.md` theo chuẩn Skill framework (YAML frontmatter + 6 bước quy trình kiểm thử).
  * Xuất bản `demo.md`: Trích xuất từ 80 VU: `GET /api/categories` (769 mẫu, p95 = 13 ms) và `GET /api/products` (754 mẫu, p95 = 15 ms), tổng throughput đạt 12,82 req/s.
  * Soạn thảo bảng phân cảnh video chi tiết từ 00:00 đến 06:45 trong `REMAINING_FOR_ME.md`.
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
Thực hiện QA rà soát toàn bộ bài nộp theo Mục 14 & 15 của đề bài PDF:
1. Kiểm tra sự hiện diện và tính toàn vẹn của tất cả các file bắt buộc.
2. Cập nhật URL video thật https://youtu.be/lk0vSGCapsc vào README.md, report.md và evidence/video-links.md.
3. Xuất lịch sử commit Git thật vào git-commits.txt; đẩy (push) toàn bộ nhánh master/main lên GitHub repo duongtronghoa/Hw05 công khai.
4. Chạy script package_submission.py --grade 100 để đóng gói file ZIP duy nhất đúng chuẩn tên 23120127_HW05_AI_Performance_100.zip.
5. Loại bỏ sạch sẽ các file rác, file tạm, không bỏ các file nháp nội bộ vào zip.
```
- **AI Output (Tóm tắt):**
  * Đồng bộ link YouTube vào toàn bộ tài liệu và cập nhật bảng tự chấm 100/100 điểm.
  * Xuất `git-commits.txt` từ git log thật; push thành công mã nguồn lên GitHub `https://github.com/duongtronghoa/Hw05`.
  * Thực thi đóng gói: Tạo thành công tệp nén `23120127_HW05_AI_Performance_100.zip` (6,64 MB, 753 file).
  * Đã loại bỏ sạch sẽ các file rác tạm thời (`tmp_*.jtl`, `.git`, `node_modules`, `tmp`).
- **Human review/correction:**
  - *Tôi đã tự kiểm:* Mở file ZIP kiểm tra danh mục 753 file bên trong, kiểm tra đường link GitHub trên trình duyệt ẩn danh và đối chiếu lại từng tiêu chí đề bài.
  - *AI làm đúng:* Script đóng gói kiểm định cực kỳ nghiêm ngặt, đảm bảo không thiếu sót bất kỳ yêu cầu nào.
  - *AI sai hoặc còn thiếu:* Không có.
  - *Tôi sửa/quyết định:* Tải file ZIP `23120127_HW05_AI_Performance_100.zip` lên hệ thống Moodle của trường và lưu biên nhận nộp bài.
  - *Bằng chứng:* File ZIP nộp bài `23120127_HW05_AI_Performance_100.zip` và giao diện xác nhận nộp bài trên Moodle.
  - *Bài học kinh nghiệm:* Quy trình kiểm định chất lượng (QA) nghiêm ngặt ở bước cuối cùng là chìa khóa để đảm bảo bài nộp đạt điểm số tuyệt đối.
