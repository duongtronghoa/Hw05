# Báo cáo Rà soát và Tự sửa Kế hoạch Kiểm thử JMeter (Plan Review)

**MSSV:** 23120127  
**Ngày thực hiện:** 2026-11-22  
**Đối tượng rà soát:**
- `plans/23120127_Load_20261122.jmx`
- `plans/23120127_Stress_20261122.jmx`
- `plans/23120127_Spike_20261122.jmx`

---

## 1. Các Lỗi Phát hiện Được và Biện pháp Tự sửa

### Lỗi 1: Sử dụng Class Plugin bên thứ ba thay vì JMeter Core
- **Mô tả lỗi:** Bản nháp JMX ban đầu do AI sinh ra có chứa phần tử `<com.atlantbh.jmeter.plugins.jsonutils.jsonpathassertion.JSONPathAssertion>` (dù được đặt cờ `enabled="false"`). Khi nạp vào Apache JMeter 5.6.3 nguyên bản, bộ phân giải XStream cố gắng nạp class này và phát sinh lỗi nghiêm trọng:
  ```text
  CannotResolveClassException: com.atlantbh.jmeter.plugins.jsonutils.jsonpathassertion.JSONPathAssertion
  ```
- **Nguyên nhân:** AI tham chiếu theo các mẫu JMeter thế hệ cũ phụ thuộc vào bộ thư viện ngoài `jmeter-plugins-json`. Bản cài JMeter 5.6.3 chuẩn không có plugin này sẵn.
- **Biện pháp sửa:** Xóa bỏ hoàn toàn định nghĩa plugin bên thứ ba, chuyển sang sử dụng thành phần lõi chính thức của JMeter 5.6.3:
  - `class`: `JSONPathAssertion`
  - `guiclass`: `JSONPathAssertionGui`
  - `package`: `org.apache.jmeter.assertions.JSONPathAssertion`

---

### Lỗi 2: Trình khởi động `jmeter.bat` lỗi khi đường dẫn chứa dấu ngoặc đơn `()`
- **Mô tả lỗi:** Khi giải nén và gọi `jmeter.bat` từ đường dẫn workspace `c:\Users\duong\Downloads\New folder (33)\tools\apache-jmeter-5.6.3\bin\jmeter.bat`, `cmd.exe` báo lỗi:
  ```cmd
  \tools\apache-jmeter-5.6.3\bin\ was unexpected at this time.
  ```
- **Nguyên nhân:** File batch khởi động `jmeter.bat` có đoạn mã `if not defined JMETER_BIN (`. Khi biến đường dẫn `%~dp0` chứa ký tự dấu đóng ngoặc `)` (từ thư mục `New folder (33)`), trình thông dịch CMD coi đó là ký tự kết thúc khối lệnh IF, dẫn đến sai cú pháp.
- **Biện pháp sửa:** Giải nén và định vị JMeter tại đường dẫn ngắn chuẩn `C:\tools\apache-jmeter-5.6.3` (không chứa dấu cách hay ngoặc đơn), tuân thủ đúng khuyến nghị tại mục 0.2 của `HW05_PLAN.md`.

---

## 2. Rà soát Logic Điều khiển, Scope và Assertions

1. **Phạm vi Timer (Think Time):**
   - Đặt `UniformRandomTimer` (trễ 1000ms, biên độ 2000ms $\rightarrow$ khoảng 1–3s) tại cấp Thread Group. Mọi request trước khi gửi đi đều dừng chờ ngẫu nhiên, mô phỏng đúng hành vi người dùng thật.
2. **Phân nhánh xử lý lỗi JWT (Logic tránh lockout):**
   - Sau sampler `01_login`, token được trích xuất qua `JSONPostProcessor` vào biến `token` với giá trị mặc định `NOT_FOUND`.
   - Một bộ điều khiển `IfController` với biểu thức `"${token}" != "NOT_FOUND" && "${token}" != ""` bao bọc các sampler từ 02 đến 06. Nếu đăng nhập thất bại, luồng bỏ qua các bước ghi, đồng thời Thread Group có cờ `on_sample_error=startnextloop` chuyển ngay sang iteration kế tiếp, tránh phát sinh hàng loạt lỗi 401 và ngăn tài khoản bị khóa trong 180s.
3. **Phân nhánh xử lý lỗi `categoryId`:**
   - Sau sampler `04_category_create`, `categoryId` được trích xuất từ `$.id`.
   - Một bộ điều khiển `IfController` kiểm tra `"${categoryId}" != "NOT_FOUND" && "${categoryId}" != ""` bọc sampler `05_category_update` và `06_category_delete`, ngăn ngừa việc gọi PUT/DELETE với ID rỗng.
4. **Tính duy nhất của tên danh mục:**
   - Sampler 04 sử dụng payload `{"name":"${category_prefix}_${__time(yyyyMMddHHmmss,)}_${__UUID()}"}`, đảm bảo mỗi VU và mỗi lần lặp đều tạo ra một danh mục có tên duy nhất tuyệt đối.
5. **Kiểm tra sự khác biệt của 3 Listener giữa các plan:**
   - **Load Test (`23120127_Load_20261122.jmx`):** Sử dụng `Summary Report` (`SummaryReport`, `enabled="true"`).
   - **Stress Test (`23120127_Stress_20261122.jmx`):** Sử dụng `Aggregate Report` (`StatVisualizer`, `enabled="true"`).
   - **Spike Test (`23120127_Spike_20261122.jmx`):** Sử dụng `View Results Tree` (`ViewResultsFullVisualizer`, đặt cờ `enabled="false"` theo mặc định để tránh tiêu tốn bộ nhớ khi chạy tải dòng lệnh, chỉ kích hoạt khi debug).

---

## 3. Kết quả Kiểm thử Tĩnh và Tải thử (Static & Load Verification)

Đã chạy kiểm thử nạp cây phần tử qua công cụ kiểm tra độc lập `SaveService.loadTree` bằng JMeter Engine lõi trên Java 25.0.2:
- `23120127_Load_20261122.jmx`: **LOADED_OK** (Đã xác minh khởi chạy CLI với 0 VU thành công).
- `23120127_Stress_20261122.jmx`: **LOADED_OK** (Cây phần tử gồm 4 Thread Group tuần tự 10/20/40/80 VU nạp thành công).
- `23120127_Spike_20261122.jmx`: **LOADED_OK** (Cây phần tử gồm 3 Thread Group 10/80/10 VU nạp thành công).

## 4. Bổ sung sau khi chạy smoke thực tế

Phần 2 ở trên mô tả bản P03 ban đầu và đã **không còn đúng** ở các điểm `IfController`, `on_sample_error` và tên category. Không dùng phần đó để mô tả JMX cuối.

- Review độc lập phát hiện `IfController.useExpression=true` với điều kiện so sánh thô; tất cả request sau login bị bỏ qua.
- Sửa đầu tiên dùng `__groovy` và JSR223 Groovy để tạo tên. Lượt `results/smoke/load.jtl` chỉ có 3 mẫu; `load.log` báo `Unsupported class file major version 69` vì Groovy đóng gói với JMeter 5.6.3 không tương thích Java 25 hiện tại. Giữ nguyên file lỗi làm chứng cứ, không tính là benchmark.
- Bản sửa thứ hai dùng JMeter core `__jexl3` cho hai điều kiện và `UserParameters` + `__UUID()` cho tên. POST dùng `${categoryName}` và PUT dùng `${categoryName}_updated`. `on_sample_error=continue` giảm nguy cơ bỏ qua DELETE khi PUT lỗi. Timer ở cấp Thread Group nên login cũng chờ 1–3 giây.
- Tạo bản sao smoke bằng `scripts/make_smoke_plans.py`: chỉ bật Thread Group đầu, 1 VU/1 iteration, CSV trỏ tới dữ liệu thật. Kết quả `results/smoke/load_v2.jtl`, `stress.jtl`, `spike.jtl`: mỗi file đúng sáu nhãn 01–06, tất cả HTTP 200 và `success=true`. SQLite có 102 users, 3 categories, 5 products trước smoke; categories vẫn là 3 sau cả ba lượt. JTL/log trong `results/smoke` bị `.gitignore` loại khỏi Git, cần đóng gói riêng khi nộp.
- PUT/DELETE của SUT trả 200 kể cả ID không tồn tại; smoke xác nhận chuỗi sáu bước và số category cuối, chưa chứng minh bản ghi cụ thể đã được cập nhật rồi xóa. Cần case chức năng riêng. Nếu một request ghi thất bại trong đợt sau, kiểm tra và dọn category có prefix bài làm sau khi lưu chứng cứ.
