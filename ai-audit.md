# Nhật ký kiểm toán AI (AI Audit Log)

**Học phần:** Kiểm thử phần mềm nâng cao (HW05 - Performance Testing)  
**MSSV:** 23120127  
**SUT:** E-Shop Backend API (commit `85af3ba875c88283615e22cb108f13e2fccaf0e9`)  

---

### [P00] Nạp bối cảnh chuẩn (Workflow, cấu hình SUT và cam kết)
- **Tool/model:** Google Antigravity / Gemini 3.8 Flash
- **Time:** 2026-11-22 08:19:37 +07:00
- **Inputs/attachments:** `HW05_PLAN.md`, `hw05-work/workflow.md`, `src/eshop-sut/api_specification.md`, SUT commit `85af3ba875c88283615e22cb108f13e2fccaf0e9`
- **Prompt:**
```text
Tôi đang làm HW05 Performance Testing, MSSV 23120127. Hãy chỉ hỗ trợ từng bước tôi yêu cầu; không tự tuyên bố đã chạy test và không tạo số liệu, ảnh, video, JTL hoặc bằng chứng giả.

Workflow CỐ ĐỊNH cho cả Load/Stress/Spike:
1 POST /api/login (admin) -> JSON token và user.role=admin
2 GET /api/categories
3 GET /api/products
4 POST /api/categories, body {"name":"<tên duy nhất>"} -> JSON id
5 PUT /api/categories/${categoryId}, body {"name":"<tên mới>"}
6 DELETE /api/categories/${categoryId}
Base URL http://localhost:3000. Các bước ghi cần Bearer JWT. CSV đã có data/admin1.csv ... data/admin100.csv, mỗi file gồm email,password,category_prefix; 100 account admin tổng hợp đã được tạo trực tiếp trong SQLite trước khi đo. JMX sẽ nằm trong plans/ nên đường dẫn CSV tương đối là ../data/admin${__threadNum}.csv.

Code hiện thực có các đặc điểm cần lưu ý: POST category trả id; PUT/DELETE trả 200 + thông báo ngay cả khi không kiểm tra số bản ghi; ba route category chỉ gọi authenticateToken, chưa check role; đăng nhập sai tăng bộ đếm 2 và khóa 180 giây; server restart sẽ DROP/seed database và mất 100 admin account. Không đưa đăng ký user hoặc dựng dữ liệu vào workload đo.

Hãy trả lời bằng tiếng Việt, nêu giả định chưa được xác minh. Mọi thông số tải hoặc ngưỡng đề xuất chỉ là giả thuyết cho đến khi tôi đo và kiểm chứng. Nếu cần dữ liệu, hãy chỉ rõ dữ liệu nào.
```
- **AI output:**
```text
Chào bạn (MSSV: 23120127). Tôi đã tiếp nhận đầy đủ bối cảnh, quy định làm việc và workflow cố định cho bài tập HW05 Performance Testing.

Tôi cam kết tuân thủ nghiêm ngặt các nguyên tắc:
1. **Chỉ hỗ trợ từng bước theo đúng yêu cầu** của bạn; không làm tắt, không đi trước yêu cầu.
2. **Tuyệt đối không tự tuyên bố đã chạy test**, không tạo số liệu giả, không bịa đặt log, ảnh chụp, video hoặc file JTL giả.
3. **Mọi thông số tải (VU, ramp-up, duration, think-time) và ngưỡng hiệu năng chỉ là giả thuyết/đề xuất kỹ thuật** phục vụ thiết kế thử nghiệm; kết quả thực tế hoàn toàn phụ thuộc vào việc bạn đo và kiểm chứng trên máy thật.

---

### 1. Tóm lược bối cảnh và workflow đã đồng bộ

- **Mục tiêu đo:** 3 kịch bản (Load, Stress, Spike) dùng chung 1 workflow cố định.
- **Workflow (6 bước):**
  1. `POST /api/login` (admin) -> Trích xuất JWT `token` và xác minh `user.role === 'admin'`.
  2. `GET /api/categories` -> Đọc danh sách danh mục (cần Bearer token).
  3. `GET /api/products` -> Đọc danh sách sản phẩm.
  4. `POST /api/categories` với body `{"name":"<tên duy nhất>"}` -> Trích xuất `id` từ JSON response (`categoryId`).
  5. `PUT /api/categories/${categoryId}` với body `{"name":"<tên mới>"}` -> Cập nhật tên danh mục.
  6. `DELETE /api/categories/${categoryId}` -> Dọn dẹp danh mục vừa tạo.
- **Cấu hình dữ liệu & môi trường:**
  - Base URL: `http://localhost:3000`.
  - 100 tài khoản admin tổng hợp đã được nạp trực tiếp vào SQLite (không đưa bước tạo admin/register vào kịch bản đo).
  - File dữ liệu CSV: `data/admin1.csv` ... `data/admin100.csv` (gồm `email,password,category_prefix`).
  - Đường dẫn tương đối từ file `.jmx` (trong `plans/`) tới CSV: `../data/admin${__threadNum}.csv`.
  - Giữ server chạy liên tục vì server restart sẽ chạy lại seed data và làm mất 100 admin account.
  - Sai mật khẩu sẽ tăng bộ đếm 2 lần và khóa tài khoản 180 giây -> script JMeter cần dừng iteration khi login lỗi, tránh gửi request rác gây khóa hàng loạt tài khoản.

---

### 2. Các giả định kỹ thuật chưa được xác minh

Các điểm dưới đây là giả định kỹ thuật cần được bạn kiểm chứng trên môi trường thực tế:

1. **Khả năng xử lý ghi đồng thời của SQLite (Concurrency lock):** SQLite là cơ sở dữ liệu dạng file đơn với cơ chế khóa ghi toàn bảng. Khi chạy Stress/Spike với nhiều VU thực hiện đồng thời các bước 4, 5, 6, giả định SUT có thể nảy sinh lỗi `SQLITE_BUSY` hoặc timeout ghi nếu backend chưa bật chế độ WAL (`PRAGMA journal_mode=WAL;`) hoặc thiết lập `busy_timeout`.
2. **Chiến lược tạo tên danh mục không trùng lặp:** Giả định việc kết hợp `${category_prefix}` từ CSV với hàm thời gian và số thứ tự luồng (ví dụ: `${category_prefix}_${__time()}_${__threadNum}_${__counter(TRUE,)}`) là đủ để đảm bảo tính duy nhất tuyệt đối giữa các VU và các lần lặp, tránh lỗi 400 do trùng tên danh mục.
3. **Trạng thái rác dữ liệu khi có lỗi giữa chừng:** Giả định nếu một iteration gặp lỗi mạng hoặc crash ở bước 4 hoặc 5 (trước khi đến bước 6 DELETE), danh mục thử nghiệm sẽ tồn đọng trong DB. Cần có kế hoạch kiểm tra số lượng bản ghi category trước và sau mỗi đợt đo.
4. **Cơ chế xử lý lỗi của sampler:** Giả định cấu hình *Action to be taken after a Sampler error* nên được đặt là `Start Next Thread Loop` (hoặc kiểm soát qua Flow Control Action) đối với bước `01_login`, nhằm ngăn chặn các bước sau gửi Bearer token rỗng/hỏng gây lỗi 401 giả tạo.
5. **Môi trường JMeter & Java trên máy:** Giả định máy bạn đã có sẵn Apache JMeter (khuyên dùng 5.6.3) và Java (JDK) tương thích, có thể thực thi lệnh CLI không bị thiếu bộ nhớ (heap size mặc định của JMeter).

---

### 3. Dữ liệu cần thiết khi chuyển sang các bước tiếp theo

Khi bạn yêu cầu thực hiện từng bước cụ thể, vui lòng cung cấp các thông tin tương ứng:
- **Nếu làm bước kiểm tra công cụ (P01):** Cần phiên bản Java (`java -version`), đường dẫn cài đặt JMeter, và phiên bản Node.js hiện tại.
- **Nếu làm bước rà soát kịch bản/JMX (P02, P03):** Cần cấu trúc chính xác các header yêu cầu và định dạng response thực tế từ một lượt chạy smoke test 1 VU.
- **Nếu phân tích lỗi hoặc điều chỉnh thông số:** Cần log thật từ terminal/JMeter (`jmeter.log`) và file kết quả `.jtl` hoặc bảng tóm tắt trích xuất thật từ máy bạn.

Tôi đã sẵn sàng. Bạn muốn tiến hành bước nào tiếp theo?
```
- **Human review/correction:**
  - *Tự kiểm tra:* Xác nhận AI hiểu đúng 6 bước workflow, không tự ý chọn kịch bản đăng ký user hoặc checkout ngoài kế hoạch.
  - *Sửa đổi/Ghi chú:* AI đã xác định đúng các bẫy kỹ thuật đặc thù của SUT (SQLite concurrency, lockout 180s, DB reset khi server khởi động lại). Các giả định kỹ thuật được phân tách rõ ràng; không có số liệu đo lường giả nào được tạo.


---

### [P01] Kiểm tra công cụ trước khi dựng plan
- **Tool/model:** Google Antigravity / Gemini 3.8 Flash
- **Time:** 2026-11-22 08:24:04 +07:00
- **Inputs/attachments:** `tools/apache-jmeter-5.6.3.zip`, `tools/apache-jmeter-5.6.3.zip.sha512`, Java version `25.0.2 LTS`, Node.js version `v25.9.0`
- **Prompt:**
```text
Dựa trên Windows 11, Java [phiên bản từ java -version], Node [phiên bản], và Apache JMeter [phiên bản/đường dẫn thực tế], hãy cho tôi checklist ngắn để xác minh JMeter mở được, đọc được CSV UTF-8, kết nối được localhost:3000, và xuất được JTL dạng CSV cùng HTML Dashboard. Đưa lệnh kiểm tra cụ thể trong PowerShell. Nếu chỉ có ZIP JMeter thì hướng dẫn xác minh SHA-512 từ nguồn chính thức trước khi giải nén. Chưa tạo hay chạy test plan. Phân biệt điều đã xác nhận từ input với điều cần tôi thử trên máy.
```
- **AI output:**
```text
### [P01] Checklist xác minh môi trường và công cụ trước khi dựng test plan

---

### 1. Phân định thông tin đã xác nhận và điều cần kiểm chứng

- **Đã xác nhận từ máy/hệ thống:**
  - Hệ điều hành: Windows 11 (hostname TRONGHOA).
  - Java: Java 25.0.2 LTS (đường dẫn Oracle Java 25).
  - Node.js: v25.9.0, npm 11.12.1.
  - Tệp nguồn JMeter: Hiện có file nén tools\apache-jmeter-5.6.3.zip (kèm file apache-jmeter-5.6.3.zip.sha512 trong thư mục tools\); chưa giải nén.
- **Điều cần bạn trực tiếp thực hiện/thử nghiệm trên máy:**
  - Kiểm tra tính toàn vẹn SHA-512 của file zip trước khi bung nén.
  - Kiểm tra tính tương thích giữa JMeter 5.6.3 và runtime Java 25.0.2 (JMeter khuyến nghị Java 8–17+, Java 25 có thể đưa ra cảnh báo GC/JVM).
  - Khởi động backend Node.js và xác minh kết nối http://localhost:3000.
  - Kiểm tra cấu hình encoding UTF-8 và cú pháp xuất HTML report.

---

### 2. Checklist và các lệnh PowerShell kiểm tra cụ thể

#### Bước 1: Xác minh mã băm SHA-512 của Apache JMeter 5.6.3 ZIP
Chạy lệnh so sánh hash SHA-512 từ file .sha512 đi kèm với file .zip:
```powershell
$expected = (Get-Content .\tools\apache-jmeter-5.6.3.zip.sha512).Split(' ')[0].Trim()
$actual = (Get-FileHash -Path .\tools\apache-jmeter-5.6.3.zip -Algorithm SHA512).Hash.ToLower()

Write-Host "Expected: $expected"
Write-Host "Actual:   $actual"
if ($expected -eq $actual) {
    Write-Host "[PASS] SHA-512 hoàn toàn trùng khớp!" -ForegroundColor Green
} else {
    Write-Host "[FAIL] SHA-512 không khớp, cần tải lại file ZIP!" -ForegroundColor Red
}
```

#### Bước 2: Giải nén và kiểm tra JMeter khởi động với Java 25
Giải nén vào thư mục tools\ (hoặc C:\tools\ để đường dẫn ngắn hơn):
```powershell
Expand-Archive -Path .\tools\apache-jmeter-5.6.3.zip -DestinationPath .\tools\
```
Sau đó kiểm tra JMeter CLI và kiểm tra tương thích Java:
```powershell
& ".\tools\apache-jmeter-5.6.3\bin\jmeter.bat" -v
```

#### Bước 3: Xác minh file CSV đọc đúng định dạng UTF-8
Kiểm tra cấu trúc và encoding của file CSV tài khoản admin:
```powershell
Get-Content -Path .\hw05-work\data\admin1.csv -Encoding utf8
```

#### Bước 4: Xác minh kết nối tới backend SUT (http://localhost:3000)
```powershell
# 1. Kiểm tra mở cổng TCP 3000
Test-NetConnection -ComputerName localhost -Port 3000

# 2. Gọi thử endpoint công khai GET /api/products
Invoke-RestMethod -Uri "http://localhost:3000/api/products" -Method GET
```

#### Bước 5: Xác minh cơ chế xuất JTL (CSV) và HTML Dashboard
- Lệnh chạy kiểm thử CLI chuẩn:
  & ".\tools\apache-jmeter-5.6.3\bin\jmeter.bat" -n -t "<đường_dẫn_jmx>" -l "<đường_dẫn_jtl>" -e -o "<thư_mục_html_report>"
- Hoặc tạo dashboard từ JTL đã có:
  & ".\tools\apache-jmeter-5.6.3\bin\jmeter.bat" -g "<đường_dẫn_jtl>" -o "<thư_mục_html_report>"
```
- **Human review/correction:**
  - *Tự kiểm tra:* Kiểm tra đối chiếu mã hash SHA-512 thực tế trên máy, xác nhận phiên bản runtime Java 25 và Node 25.
  - *Sửa đổi/Ghi chú:* Ghi nhận cảnh báo tiềm ẩn về tính tương thích giữa Java 25 và JMeter 5.6.3 (nếu gặp lỗi JVM flag cần tinh chỉnh trong file cấu hình khởi động của JMeter).


---

### [P03] Tạo và rà ba JMX
- Tool/model: Google Antigravity / Gemini 3.8 Flash
- Time: 2026-11-22 09:15:32 +07:00
- Inputs/attachments: design/test-design.md; CSV; API spec; server.js
- Prompt:

```text
Dựa vào design/test-design.md đã duyệt, hãy TẠO và kiểm tĩnh đúng ba file plans/23120127_Load_<ngày thực tế YYYYMMDD>.jmx, ..._Stress_..., ..._Spike_... bằng JMeter thành phần lõi. Cả ba dùng cùng 6 sampler và nhãn; CSV ../data/admin${__threadNum}.csv; trích token từ login, id từ POST category; không hardcode token/password/category ID; tên category duy nhất theo iteration. Load có Summary Report, Stress có Aggregate Report, Spike có View Results Tree chỉ dùng debug và tắt khi CLI. Thiết kế Stress tuần tự 10/20/40/80 VU; Spike 10->80->10; Load mặc định 20 VU/60s ramp/8 phút, có tham số -Jvus/-Jramp/-Jduration cho soak. Rà XML, scope timer/assertion, logic dừng iteration khi thiếu JWT/categoryId, và kiểm khác biệt ba listener. Nếu JMeter đã có, dùng CLI/GUI khả dụng để xác nhận file nạp được; chưa chạy benchmark chính. Ghi lỗi AI tạo plan và tự sửa trong design/plan-review.md, nói vì sao lỗi xuất hiện. Commit từng plan riêng nếu có thể, hoặc commit nêu rõ từng file.
Cuối lượt: lưu nguyên văn P03 vào hw05-work/audit_inputs/P03.txt; viết câu trả lời cuối và đường dẫn/hash ba JMX vào hw05-work/audit_outputs/P03.md; chạy python hw05-work/scripts/append_ai_audit.py --id P03 --purpose "Tạo và rà ba JMX" --tool-model "<tool/model thực tế hoặc không hiển thị>" --prompt-file hw05-work/audit_inputs/P03.txt --output-file hw05-work/audit_outputs/P03.md --inputs "design/test-design.md; CSV; API spec; server.js". Gửi đúng nội dung P03.md. Không sửa P00/P01,
```
- AI output:

````text
### Báo cáo Thực hiện P03: Tạo và Kiểm tĩnh Ba Kế hoạch Kiểm thử JMeter

Đã hoàn thành việc tạo và kiểm tĩnh ba file kế hoạch kiểm thử theo thiết kế chuẩn hóa, sử dụng hoàn toàn các thành phần lõi của Apache JMeter 5.6.3 (không phụ thuộc plugin ngoài).

---

### 1. Đường dẫn và Mã băm (SHA-256) Ba File JMX

| Kịch bản | Đường dẫn file | Mã băm SHA-256 |
|---|---|---|
| **Load Test** | `plans/23120127_Load_20261122.jmx` | `6faed97682594949055c88e14ff382700e4bc1fd5c11570be6fa070bb20a8941` |
| **Stress Test** | `plans/23120127_Stress_20261122.jmx` | `aa25bee4a821c01b94e007e9f649649fe0860b6b9a65676c052b9a28599666fa` |
| **Spike Test** | `plans/23120127_Spike_20261122.jmx` | `6aeae320eb7f3e162ccfeaa931aeca38dce06672d3a90956d096d23e50a70fb5` |

---

### 2. Chi tiết Cấu hình Kỹ thuật Chung

1. **Chuỗi 6 Sampler và nhãn ổn định:**
   - `01_login`: POST `/api/login` kèm body `{"email":"${email}","password":"${password}"}`. Trích xuất JWT `token` qua `JSONPostProcessor` (`$.token`, mặc định `NOT_FOUND`). Kiểm tra assertion 200 và JSON Assertion `$.user.role == "admin"`.
   - `02_categories_list`: GET `/api/categories` kèm header `Authorization: Bearer ${token}`.
   - `03_products_list`: GET `/api/products` (public endpoint).
   - `04_category_create`: POST `/api/categories` kèm Bearer token và body `{"name":"${category_prefix}_${__time(yyyyMMddHHmmss,)}_${__UUID()}"}`. Trích xuất `categoryId` từ `$.id`.
   - `05_category_update`: PUT `/api/categories/${categoryId}` cập nhật tên danh mục kèm Bearer token.
   - `06_category_delete`: DELETE `/api/categories/${categoryId}` xóa danh mục vừa tạo.
2. **Cấu hình CSV Data Set:**
   - File path: `../data/admin${__threadNum}.csv` (đường dẫn tương đối từ thư mục `plans/`).
   - Đọc header tự động `email,password,category_prefix`, `shareMode.thread` (mỗi thread độc lập theo đúng account của mình).
3. **Phạm vi Timer & Xử lý phân nhánh lỗi:**
   - `UniformRandomTimer` trễ 1000–3000ms đặt ở cấp Thread Group để mô phỏng think-time tự nhiên.
   - `IfController` kiểm tra `"${token}" != "NOT_FOUND"` bao quanh các bước 2–6; kết hợp `on_sample_error="startnextloop"` để dừng ngay iteration khi login lỗi, ngăn chặn tạo lỗi 401 giả và không kích hoạt cơ chế khóa tài khoản 180s.
   - `IfController` kiểm tra `"${categoryId}" != "NOT_FOUND"` bao quanh bước 5 và 6 để tránh gửi request rác khi bước 4 không tạo được ID.
4. **Phân định 3 Listener khác nhau theo kịch bản:**
   - **Load:** Kích hoạt `Summary Report` (`SummaryReport`). Hỗ trợ tham số hóa qua dòng lệnh `-Jvus=${__P(vus,20)} -Jramp=${__P(ramp,60)} -Jduration=${__P(duration,480)}` sẵn sàng phục vụ bài đo Soak.
   - **Stress:** Kích hoạt `Aggregate Report` (`StatVisualizer`), chạy tuần tự 4 Thread Group tương ứng 10, 20, 40, 80 VU (`serialize_threadgroups = true`), mỗi tầng giữ tải 120s.
   - **Spike:** Sử dụng `View Results Tree` (`ViewResultsFullVisualizer`) và được đặt cờ tắt `enabled="false"` theo mặc định để chạy tải CLI không tốn tài nguyên, sẵn sàng kích hoạt phục vụ debug 1 VU. Kịch bản chạy tuần tự 3 giai đoạn: Base 10 VU (120s) -> Peak 80 VU (60s) -> Recovery 10 VU (120s).

---

### 3. Rà soát Lỗi AI và Tự sửa chữa

Toàn bộ chi tiết lỗi và giải trình đã được ghi tại [design/plan-review.md](file:///c:/Users/duong/Downloads/New%20folder%20(33)/hw05-work/design/plan-review.md):
- **Lỗi 1 (Dependency plugin bên thứ ba):** AI ban đầu đưa thẻ class `com.atlantbh.jmeter.plugins.jsonutils.jsonpathassertion.JSONPathAssertion` vào XML khiến bộ giải mã XStream của JMeter văng lỗi `CannotResolveClassException`. Đã tự sửa bằng cách thay thế 100% bằng class lõi `JSONPathAssertion` (`org.apache.jmeter.assertions.JSONPathAssertion`).
- **Lỗi 2 (Sự cố đường dẫn batch file):** Gọi `jmeter.bat` từ đường dẫn workspace chứa dấu ngoặc `New folder (33)` gây lỗi ngắt cú pháp lệnh CMD. Đã khắc phục bằng cách sao chép bộ cài JMeter vào đường dẫn ngắn `C:\tools\apache-jmeter-5.6.3` theo đúng hướng dẫn tại [HW05_PLAN.md](file:///c:/Users/duong/Downloads/New%20folder%20(33)/HW05_PLAN.md).

---

### 4. Kết quả Kiểm tĩnh và Nạp Thử nghiệm Thực tế

- **Kiểm tra cú pháp XML:** Cả 3 file phân tích cú pháp thành công với Python `xml.etree.ElementTree`.
- **Kiểm tra nạp cây phần tử qua JMeter SaveService API (`CheckJmx.java`):**
  ```text
  LOADED_OK: 23120127_Load_20261122.jmx
  LOADED_OK: 23120127_Stress_20261122.jmx
  LOADED_OK: 23120127_Spike_20261122.jmx
  ```
- **Kiểm tra CLI thực tế:** Kế hoạch Load được chạy thử chế độ CLI với tham số `-Jvus=0` trên runtime Java 25.0.2:
  ```text
  Created the tree successfully using .\hw05-work\plans\23120127_Load_20261122.jmx
  Starting standalone test @ 2026 Nov 22 09:13:54 GMT+07:00
  summary = 0 in 00:00:00 ... Tidying up ... end of run
  ```
  *(Chưa thực hiện bất kỳ benchmark tải chính nào theo đúng yêu cầu).*

---

### 5. Lịch sử Commit Git

Các file đã được phân loại và commit riêng biệt vào kho git cục bộ `hw05-work`:
1. `fa56611` - `HW05: add test design and plan review specifications`
2. `df9c814` - `HW05: create Load test plan 23120127_Load_20261122.jmx`
3. `0994417` - `HW05: create Stress test plan 23120127_Stress_20261122.jmx`
4. `dee1d10` - `HW05: create Spike test plan 23120127_Spike_20261122.jmx`
5. `2545daa` - `HW05: add plan generator and static verification script`
````
- Human review/correction: Chờ người học tự kiểm tra và bổ sung; agent không tự nhận là đã human review.


---

### [P02] Thiết kế test và workload
- Tool/model: Google Antigravity / Gemini 3.8 Flash
- Time: 2026-11-22 16:40:46 +07:00
- Inputs/attachments: HW05_PLAN.md; workflow.md; CSV; API spec; server.js
- Prompt:

```text
ãy THỰC HIỆN thiết kế HW05 trên workspace hiện tại. Đọc HW05_PLAN.md, hw05-work/workflow.md, dữ liệu CSV mẫu, API spec và route thật trong server.js. Ghi design/test-design.md: bảng 6 request cố định, body/header, JWT và categoryId correlation, tạo categoryName một lần/iteration từ category_prefix+UUID, assertion, cách xử lý login/POST lỗi, cleanup category, ba report view khác nhau. Đề xuất Load/Stress/Spike với VU/ramp/hold/think-time và tiêu chí pass/fail TRƯỚC khi đo; các số chỉ là giả thuyết, không là kết quả. Nêu rủi ro “transactional” cho CRUD và workflow trùng nhóm chưa được xác nhận. Tự rà lại với code, ghi giả định và commit file thiết kế.
Cuối lượt: lưu NGUYÊN VĂN toàn bộ tin nhắn P02 này vào hw05-work/audit_inputs/P02.txt; soạn câu trả lời cuối (file đã tạo, kiểm tra, commit, việc cần người học xác nhận) trong hw05-work/audit_outputs/P02.md; chạy từ thư mục gốc: python hw05-work/scripts/append_ai_audit.py --id P02 --purpose "Thiết kế test và workload" --tool-model "<tool/model thực tế hoặc không hiển thị>" --prompt-file hw05-work/audit_inputs/P02.txt --output-file hw05-work/audit_outputs/P02.md --inputs "HW05_PLAN.md; workflow.md; CSV; API spec; server.js". Sau đó gửi đúng nội dung P02.md, không thêm lời khác. Script ghi vào ai_audit.md; không sửa P00/P01 hoặc tự ghi Human review.
```
- AI output:

```text
### Báo cáo Thực hiện P02: Thiết kế Test và Workload HW05

Đã hoàn thành phân tích toàn diện SUT, dữ liệu và quy trình kiểm thử, đồng thời lập tài liệu thiết kế chi tiết tại [design/test-design.md](file:///c:/Users/duong/Downloads/New%20folder%20(33)/hw05-work/design/test-design.md).

---

### 1. File Đã Tạo và Nội Dung Chi Tiết

Tài liệu thiết kế [design/test-design.md](file:///c:/Users/duong/Downloads/New%20folder%20(33)/hw05-work/design/test-design.md) bao gồm:
1. **Bảng 6 request cố định của workflow Admin:**
   - `01_login`: POST `/api/login` $\rightarrow$ Trích xuất Bearer token qua `JSONPostProcessor` (`$.token`), assertion 200 và JSON Assertion `$.user.role == "admin"`.
   - `02_categories_list`: GET `/api/categories` $\rightarrow$ Đọc danh sách categories, kèm Bearer token.
   - `03_products_list`: GET `/api/products` $\rightarrow$ Endpoint public đọc danh sách sản phẩm.
   - `04_category_create`: POST `/api/categories` $\rightarrow$ Tạo category mới với tên duy nhất, trích xuất `categoryId` từ `$.id`.
   - `05_category_update`: PUT `/api/categories/${categoryId}` $\rightarrow$ Cập nhật category vừa tạo với tên mới.
   - `06_category_delete`: DELETE `/api/categories/${categoryId}` $\rightarrow$ Dọn dẹp bản ghi category đã tạo trong iteration.
2. **Quy tắc sinh dữ liệu & Correlation:**
   - Nạp dữ liệu tài khoản từ `../data/admin${__threadNum}.csv` với các cột `email,password,category_prefix`.
   - Sinh tên category động và duy nhất tuyệt đối trong từng iteration bằng cú pháp:
     `${category_prefix}_${__time(yyyyMMddHHmmss,)}_${__UUID()}`.
   - Truyền biến tương quan: JWT `${token}` cho các request cần xác thực và `${categoryId}` cho bước cập nhật/xóa.
3. **Chiến lược xử lý lỗi & Dọn dẹp dữ liệu:**
   - Nếu `01_login` lỗi hoặc không lấy được token: Bộ điều khiển `IfController` (`"${token}" != "NOT_FOUND"`) kết hợp cờ Thread Group `on_sample_error=startnextloop` sẽ bỏ qua các bước còn lại và chuyển sang iteration tiếp theo, ngăn chặn phát sinh lỗi 401 giả tạo và giảm nguy cơ bị khóa tài khoản 180s.
   - Nếu `04_category_create` lỗi hoặc không có `categoryId`: Bộ điều khiển `IfController` (`"${categoryId}" != "NOT_FOUND"`) sẽ bỏ qua bước PUT và DELETE.
   - Dọn dẹp (Cleanup): Bước DELETE dọn dẹp trực tiếp trong luồng. Bổ sung quy trình kiểm tra số lượng category trong database trước và sau mỗi đợt đo.
4. **Phân định 3 Listener khác nhau:**
   - **Load Test:** Sử dụng `Summary Report` (`SummaryReport`).
   - **Stress Test:** Sử dụng `Aggregate Report` (`StatVisualizer`).
   - **Spike Test:** Sử dụng `View Results Tree` (`ViewResultsFullVisualizer`, mặc định đặt `enabled="false"` khi chạy CLI).
5. **Đề xuất tham số tải (Giả thuyết kỹ thuật ban đầu):**
   - **Load:** 20 VU, ramp-up 60s, duration 480s (8 phút), think-time 1–3s (`UniformRandomTimer`). Hỗ trợ tham số hóa `-Jvus`, `-Jramp`, `-Jduration` để tái sử dụng cho bài đo Soak (giữ tải 10–15 phút).
   - **Stress:** 4 tầng tuần tự (`serialize_threadgroups = true`): 10 VU $\rightarrow$ 20 VU $\rightarrow$ 40 VU $\rightarrow$ 80 VU; mỗi tầng ramp-up 15s, duration 120s.
   - **Spike:** 3 giai đoạn tuần tự: Nền 10 VU (120s) $\rightarrow$ Đột biến 80 VU (60s) $\rightarrow$ Hồi phục 10 VU (120s).
6. **Tiêu chí chấp nhận ban đầu (Pre-measurement Criteria):**
   - Tỷ lệ lỗi $\le 1\%$, không xuất hiện lỗi 500 hoặc crash Node.js.
   - Thời gian đáp ứng p95: Nhóm đọc $\le 500\text{ ms}$, nhóm ghi/auth $\le 2000\text{ ms}$.
   - Bộ nhớ RAM backend không tăng vô hạn (không memory leak nghiêm trọng).
   - Không tồn đọng bản ghi mồ côi sau phiên đo.

---

### 2. Kiểm Tra và Rà Soát với Mã Nguồn SUT

- **Xác thực mã nguồn backend (`server.js`, `database.js`):**
  - Route POST `/api/categories` trả về `{ message: "Category created", id: this.lastID }`, xác nhận trường `id` là chính xác.
  - Route PUT và DELETE trả về mã 200 và thông báo tĩnh mà không kiểm tra số bản ghi bị ảnh hưởng (`this.changes`), cần assertion kiểm tra response JSON chặt chẽ.
  - Các route category gọi `authenticateToken` nhưng chưa kiểm tra phân quyền `role === 'admin'`. Kịch bản vẫn dùng tài khoản admin để tuân thủ đúng workflow chuẩn và ghi nhận sai lệch phân quyền này làm báo cáo lỗi.
  - Mỗi lần khởi động lại server sẽ thực thi lại `database.js` và xóa sạch 100 tài khoản admin tổng hợp $\rightarrow$ duy trì server chạy liên tục trong suốt quá trình thử nghiệm.

---

### 3. Trạng Thái Commit Git

Tài liệu thiết kế đã được commit vào kho git cục bộ `hw05-work`:
- Commit hash: `fa56611` - `HW05: add test design and plan review specifications`

---

### 4. Các Vấn Đề Cần Người Học Xác Nhận

1. **Xác nhận workflow với nhóm:** Người học cần xác nhận với các thành viên khác trong nhóm kiểm thử rằng không có ai chọn trùng workflow Admin Category CRUD này.
2. **Xác nhận cách hiểu "Transactional":** Đề bài đưa ví dụ giỏ hàng/thanh toán cho nhóm transactional. Workflow này sử dụng chuỗi ghi/xóa dữ liệu danh mục quản trị (`POST/PUT/DELETE`). Người học cần xác nhận với giảng viên/nhóm nếu có yêu cầu bắt buộc transactional phải là checkout.
3. **Kiểm tra và đánh giá cá nhân:** Bổ sung nội dung đánh giá độc lập vào trường `Human review/correction` trong nhật ký kiểm toán.
```
- Human review/correction: Chờ người học tự kiểm tra và bổ sung; agent không tự nhận là đã human review.
