# Bộ prompt HW05 từ mục 4 đến khi nộp

Áp dụng cho MSSV `23120127`, workflow đã chọn: **Admin Login → Categories List → Products List → Create Category → Update Category → Delete Category**. Dùng các prompt **theo thứ tự** trong cùng một cuộc hội thoại AI. Nếu mở cuộc hội thoại mới, gửi lại P00 cùng dữ liệu liên quan. Những chỗ `[ ... ]` phải thay bằng file, kết quả đo hoặc thông tin thật. Prompt ở đây là **mẫu để sử dụng**, không phải log đã thực sự gửi cho AI; AI Audit phải ghi prompt/output thực tế cùng ngày giờ thực tế.

Trước khi bắt đầu: xác nhận với nhóm workflow không trùng; kiểm tra cách giảng viên chấp nhận nhóm “transactional” cho Category CRUD. SUT có chủ ý chứa lỗi; không sửa code SUT chỉ để bài đo đẹp. Không đưa JWT thật, mật khẩu cá nhân, ảnh/video hoặc `.jtl` do AI tạo vào bài. Khi gắn JTL lớn, đính kèm file thật hoặc các bảng thống kê có script/phép tính tái lập được; không cắt vài dòng rồi yêu cầu AI suy ra p95 toàn bộ.

## Quy tắc AI Audit cho **mọi** prompt bên dưới

Ngay khi gửi từng prompt, tạo một entry trong `ai-audit.md`:

```markdown
### [Pxx] [mục đích]
- Tool/model: [tên và phiên bản hiển thị nếu có]
- Time: [YYYY-MM-DD HH:MM:SS +07:00]
- Inputs/attachments: [tên file, commit hoặc hash nếu có]
- Prompt: [dán nguyên văn prompt thật đã gửi, gồm dữ liệu đã điền]
- AI output: [dán nguyên văn câu trả lời; nếu quá dài, lưu file riêng rồi dẫn đường dẫn]
- Human review/correction: [tự kiểm điều gì, sửa gì, vì sao, chứng cứ]
```

Không để AI tự dựng nhật ký hội thoại đã qua. Với các trao đổi ở mục 1–3, xuất lịch sử chat thật hoặc ghi lại chính xác từ cuộc hội thoại hiện có; nếu thiếu phần nào, ghi rõ là thiếu. Trong report, phân biệt **AI đề xuất**, **con người sửa**, **đã chạy và quan sát**.

## Mục 4 — Thiết kế bằng AI và tạo 3 plan

### P00 — Nạp bối cảnh chuẩn (gửi đầu mỗi chat mới)

**Công dụng:** Cho AI bối cảnh đúng, tránh nó tự chọn workflow khác hoặc bịa endpoint.

**Đính kèm:** `HW05_PLAN.md`, `hw05-work/workflow.md`, `src/eshop-sut/api_specification.md`; tốt hơn nữa là trích các route liên quan từ `src/eshop-sut/backend/server.js`. Không gửi cả database chứa dữ liệu thử.

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

### P01 — Kiểm tra công cụ trước khi dựng plan

**Công dụng:** Lấy checklist cài/kiểm JMeter phù hợp Windows, tránh lỗi chỉ xuất hiện lúc chạy. Chỉ dùng khi cần hướng dẫn công cụ; tự kiểm lệnh và phiên bản thật.

```text
Dựa trên Windows 11, Java [phiên bản từ java -version], Node [phiên bản], và Apache JMeter [phiên bản/đường dẫn thực tế], hãy cho tôi checklist ngắn để xác minh JMeter mở được, đọc được CSV UTF-8, kết nối được localhost:3000, và xuất được JTL dạng CSV cùng HTML Dashboard. Đưa lệnh kiểm tra cụ thể trong PowerShell. Nếu chỉ có ZIP JMeter thì hướng dẫn xác minh SHA-512 từ nguồn chính thức trước khi giải nén. Chưa tạo hay chạy test plan. Phân biệt điều đã xác nhận từ input với điều cần tôi thử trên máy.
```

### P02 — Rà workflow, correlation và dữ liệu

**Công dụng:** Buộc AI chỉ ra payload, extractor, assertion và nguy cơ đụng dữ liệu trước khi sinh JMX.

```text
Với 6 request trong workflow cố định, lập bảng theo thứ tự gồm: method/path, biến từ CSV, request body/header, expected response, biến cần trích xuất, assertion tối thiểu và lỗi có thể gây false positive. Giải thích cách tạo categoryName duy nhất MỘT LẦN mỗi iteration từ category_prefix + UUID, cách dùng cùng categoryId do POST trả về cho PUT/DELETE, và xử lý nếu POST/login thất bại để không sửa ID seed. Chỉ dùng API có thật trong tài liệu/code tôi đã cung cấp. Đừng sinh JMX ở lượt này.
```

### P03 — Đề xuất workload và tiêu chí trước đo

**Công dụng:** Chọn tham số Load/Stress/Spike hợp lý, có lý do và điều kiện hiệu chỉnh sau calibration.

```text
Hãy đề xuất riêng Load, Stress, Spike cho CÙNG workflow 6 request. Máy chạy JMeter và Node/SQLite trên cùng Windows host, RAM [số GB], 100 account/CSV tương ứng tối đa 100 VU. Trình bày bảng: mục tiêu, số VU, ramp-up, thời gian giữ tải, think-time giữa hành động, cách chuyển giai đoạn, số iteration dự kiến (chỉ ước tính), rủi ro client trở thành bottleneck. Các mốc trong kế hoạch 20 VU Load; Stress 10/20/40/80; Spike 10->80->10 chỉ là điểm xuất phát. Đề xuất tiêu chí ổn định trước đo cho lỗi không mong đợi, p95 của POST/PUT/DELETE category, RPS và RAM, nói rõ đó là giả thuyết chứ chưa phải threshold của máy tôi. Đừng sinh JMX ở lượt này.
```

### P04 — Thiết kế cấu trúc JMeter trước khi sinh file

**Công dụng:** Review kiến trúc plan, CSV, timer, logger và listener trước khi có XML dài.

```text
Với JMeter [phiên bản đã kiểm tra], hãy mô tả cây Test Plan chỉ dùng thành phần lõi (không plugin) cho workflow đã chốt. Cần HTTP Request Defaults, CSV Data Set Config theo từng thread, Header Manager, JSON Extractor cho $.token và $.id, kiểm tra role=admin, response assertions, biến categoryName/categoryUpdatedName tạo một lần/iteration, think-time, xử lý lỗi login/POST và reset biến categoryId. Chỉ rõ scope của từng thành phần để timer không áp lên request ngoài ý muốn. Đề xuất ba report view KHÁC nhau: Load Summary Report, Stress Aggregate Report, Spike View Results Tree; giải thích cách dùng View Results Tree khi debug/nạp JTL sau run nhưng tắt trong CLI load để tránh lệch số đo. Đưa cây dạng text và checklist con người kiểm, chưa viết JMX.
```

### P05 — Sinh Load plan

**Công dụng:** Tạo bản dự thảo `.jmx` thứ nhất và các thuộc tính có thể tái dùng cho soak.

```text
Tạo bản dự thảo JMeter JMX hoàn chỉnh cho Load theo cấu trúc P04, tên 23120127_Load_[YYYYMMDD].jmx (thay ngày thực tế). 6 nhãn sampler: 01_login, 02_categories_list, 03_products_list, 04_category_create, 05_category_update, 06_category_delete. Dùng ../data/admin${__threadNum}.csv (header, UTF-8, current thread, recycle). Login lấy token và kiểm role admin; POST category lấy id; PUT/DELETE dùng đúng id. categoryName và tên cập nhật phải độc nhất, được tạo một lần mỗi iteration. Không hardcode token, email, password hay category ID. Dùng tham số JMeter -Jvus, -Jramp, -Jduration để tôi tái dùng plan cho soak. Giá trị mặc định tham khảo: 20 VU, ramp 60 giây, tổng 480 giây; think-time 1-3 giây giữa các bước. Có Summary Report đúng plan này, không có listener khác đang bật khi benchmark CLI. Trả về nội dung file và hướng dẫn mở/kiểm trong GUI; nêu điểm nào bạn không chắc về schema JMX phiên bản này. Không bảo rằng đã chạy thành công.
```

### P06 — Sinh Stress plan

**Công dụng:** Tạo bản `.jmx` thứ hai, giữ nguyên workflow nhưng tăng tải theo tầng có thể phân tích.

```text
Tạo 23120127_Stress_[YYYYMMDD].jmx trên cơ sở workflow/CSV/assertion đã duyệt ở Load; KHÔNG đổi 6 endpoint hoặc nhãn sampler. Dùng thành phần lõi JMeter và các giai đoạn chạy tuần tự 10, 20, 40, 80 VU (mỗi mức khoảng 2 phút với ramp 10-30 giây, đây là tham số khởi đầu có thể sửa sau calibration). Chỉ rõ cấu hình để Thread Groups thật sự chạy tuần tự và cách đặt tên thread group để đọc JTL theo từng mức. Dùng Aggregate Report làm report view của Stress, không lặp Summary Report. Mỗi thread vẫn dùng CSV riêng; category ID lấy từ POST trong cùng iteration. Cho nội dung file và các điểm cần con người kiểm trong JMeter GUI. Không tuyên bố đã chạy.
```

### P07 — Sinh Spike plan

**Công dụng:** Tạo bản `.jmx` thứ ba để kiểm phản ứng khi tăng tải đột ngột và phục hồi.

```text
Tạo 23120127_Spike_[YYYYMMDD].jmx giữ nguyên workflow/CSV/assertion/nhãn sampler. Dùng giai đoạn nền 10 VU khoảng 2 phút, spike 80 VU ramp 1-5 giây và giữ 1 phút, sau đó phục hồi 10 VU khoảng 2 phút; giải thích nếu chuyển Thread Group tuần tự tạo khoảng trống cần ghi nhận khi phân tích. Chỉ dùng thành phần lõi JMeter. Report view của Spike là View Results Tree để debug/nạp JTL sau run; nó phải tắt khi chạy tải CLI. Không thêm Summary/Aggregate Report vào plan này. Cho nội dung file và checklist GUI, không tuyên bố đã chạy.
```

### P08 — Review tĩnh ba JMX do AI tạo

**Công dụng:** Tìm lỗi sinh XML, sai scope, trùng listener hoặc category ID trước khi chạy.

**Đính kèm:** Ba `.jmx` vừa tạo, 1 CSV mẫu (có thể che mật khẩu), `workflow.md`, trích API/code.

```text
Review TĨNH ba JMX đính kèm theo từng file. Lập bảng PASS/FAIL với vị trí node XML cụ thể cho: đúng tên 23120127_{Load|Stress|Spike}_[YYYYMMDD].jmx; cùng 6 endpoint/nhãn; CSV ../data/admin${__threadNum}.csv; token và categoryId được trích đúng response; JWT chỉ gắn cho request cần xác thực; tên category không trùng mỗi iteration; không dùng id seed; timer đúng scope; assertion không chỉ dựa vào HTTP 200 khi PUT/DELETE có thể báo thành công giả; thread group/stage đúng; ba listener khác loại, View Results Tree không hoạt động lúc CLI; không chứa password/token thật. Chỉ đề xuất bản vá cho FAIL, giữ nguyên phần đã đúng. Không coi review XML là bằng chứng plan chạy được.
```

## Mục 5 — Smoke test và hiệu chỉnh tải

### P09 — Phân tích smoke run 1 VU

**Công dụng:** Sửa lỗi plan dựa trên chạy thật trước khi đo. Chạy 1 VU/1 iteration trong GUI, lưu request/response đã che token và ảnh lỗi nếu có, rồi gửi prompt.

```text
Đây là kết quả smoke run THẬT 1 VU/1 iteration ngày [ngày giờ] của [tên JMX]: [đính kèm ảnh/log hoặc dán bảng sáu sampler, response code, assertion result, dữ liệu đã che JWT]. Hãy tìm lỗi test script theo thứ tự ưu tiên: CSV không đọc, login/role/token sai, header Bearer, categoryName không độc nhất, JSON Extractor $.id sai, PUT/DELETE dùng ID khác, Timer/Thread Group sai, category thử còn sót. Phân biệt lỗi script, lỗi SUT và điều chưa đủ bằng chứng. Đề xuất sửa tối thiểu và cách chạy lại để chứng minh đã sửa. Không tự điền kết quả thiếu.
```

### P10 — Chọn thông số sau calibration

**Công dụng:** Dùng số đo thăm dò 5/10/20/40/80 VU để chọn cấu hình cuối, tránh lấy số VU trong kế hoạch làm kết luận.

```text
Đây là bảng calibration THẬT ở 5/10/20/40/[80] VU: [mỗi mức ghi thời lượng, mẫu, RPS, p95 từng request ghi category, error%, CPU/RAM node.exe, CPU/RAM JMeter, số category dư]. Dựa đúng bảng này, đề xuất VU/ramp/duration/think-time cuối cho Load, Stress, Spike và mức ứng viên cho soak 10-15 phút. Chỉ rõ khi nào client JMeter cùng máy là nút thắt, khi nào SQLite/Node là nút thắt; nếu dữ liệu chưa đủ thì nói cần đo thêm gì. Đưa bảng “AI đề xuất / tôi cần kiểm chứng”, không gọi thông số đề xuất là ngưỡng chịu tải đã đo.
```

### P11 — Rà tiêu chí pass/fail và cách đo

**Công dụng:** Chốt trước cách phân tích, để sau khi thấy kết quả không đổi chuẩn tùy tiện.

```text
Từ workflow Category CRUD và kết quả calibration đã cung cấp, hãy đề xuất bảng tiêu chí pass/fail để tôi duyệt TRƯỚC ba run chính: lỗi không mong đợi, p95 theo endpoint (đặc biệt POST/PUT/DELETE category), RPS, số mẫu tối thiểu, CPU và xu hướng RAM, độ sạch dữ liệu category sau run. Nêu phép tính chính xác, đơn vị và cửa sổ thời gian loại ramp/warm-up. Phân biệt lỗi HTTP, assertion failure và chức năng sai dù HTTP 200. Các con số chỉ là tiêu chí đề xuất cho máy này, không phải tiêu chuẩn phổ quát.
```

## Mục 6 — Chạy Load, Stress, Spike và soak

### P12 — Runbook CLI và bằng chứng cho từng run

**Công dụng:** Có lệnh chạy/ghi bằng chứng nhất quán. AI chỉ viết runbook; bạn tự chạy, quay và chụp thật.

```text
Viết runbook PowerShell cho 3 JMX đã duyệt trong hw05-work/plans và soak tái dùng Load plan. JMeter thực tế ở [đường dẫn bin/jmeter.bat]; ngày chạy [YYYYMMDD]. Mỗi run cần lệnh -n -t -l -j -e -o, thư mục HTML mới/rỗng, JTL CSV đầy đủ, jmeter.log, giờ bắt đầu/kết thúc và tham số VU/ramp/duration. Trước mỗi run hãy kiểm tra backend PID, 100 admin account, 100 CSV, category count; sau run kiểm tra JTL không rỗng, HTML/index.html, category còn sót, PID backend và log. Cho bảng checklist ảnh chụp một khung chứa JMeter/CLI + Task Manager hiện node.exe cùng CPU/RAM; ảnh dxdiag và bảng hardware. Không tự chạy lệnh hoặc tạo bằng chứng.
```

### P13 — Xử lý lỗi giữa các run (chỉ dùng khi gặp lỗi)

**Công dụng:** Chẩn đoán 401/403, khóa tài khoản, database reset hoặc category sót mà không xóa chứng cứ.

```text
Run [tên scenario] gặp hiện tượng THẬT: [dán lỗi, JMeter log, vài dòng JTL liên quan, PID/DB counts; che JWT]. Hãy lập cây chẩn đoán để phân biệt sai CSV/mật khẩu, login lockout (SUT tăng 2 lần sai và khóa 180 giây), token extractor/header, server restart reset DB, SQLite busy và category chưa được DELETE. Đề xuất cách phục hồi ít can thiệp nhất; chỉ rõ dữ liệu/bằng chứng cần lưu TRƯỚC khi reset hoặc dọn category. Không bảo tôi loại lỗi khỏi JTL gốc. Nếu cần một run mới, đặt tên file mới để không ghi đè.
```

### P14 — Xác nhận soak 10–15 phút và ngưỡng máy

**Công dụng:** Tách kết luận endurance thực đo khỏi stress peak ngắn.

```text
Đây là kết quả soak THẬT tại [VU] với [ramp] và [thời gian giữ ổn định 10-15 phút], JTL [file], bảng tài nguyên theo phút [đính kèm], và tiêu chí đã chốt trước run [đính kèm]. Tính/kiểm tra RPS sustained của cửa sổ giữ tải, p95/error% từng endpoint, RAM node.exe min/max/đầu/cuối, xu hướng có plateau hay tiếp tục tăng. Có đủ bằng chứng để gọi [VU] là mức ổn định cao nhất đã thử chưa? Nếu chưa, nói chính xác giới hạn của kết luận. Không lấy spike RPS làm endurance threshold và không dùng “memory ceiling” nếu RAM vẫn tăng.
```

### P15 — Kịch bản video và danh sách cảnh

**Công dụng:** Lên dàn ý quay video tối thiểu 6 phút, không để thiếu công cụ và resource monitor trong cùng khung.

```text
Lập dàn ý video YouTube Unlisted tối thiểu 6 phút cho HW05, giọng thuyết minh tiếng Việt do chính tôi nói. Bố cục phải cho thấy trong cùng khung hình công cụ JMeter/CLI và Task Manager đang theo dõi node.exe ở mỗi Load/Stress/Spike; có đoạn trình bày CSV/JMX, HTML report/JTL, soak threshold và một lỗi/thay đổi AI tôi tự sửa. Cho timeline theo phút, câu gợi ý thuyết minh bằng tiếng Việt và checklist xem lại trước upload. Không tạo video, ảnh, giọng nói, screenshot hay số đo thay tôi.
```

## Mục 7 — Phân tích JTL và phản biện AI

### P16 — Tạo bộ phân tích JTL có thể chạy lại

**Công dụng:** Tính thống kê từ log gốc bằng code, làm chuẩn để đối chiếu nhận xét AI.

```text
Hãy viết script Python 3.12 đọc ba file JTL CSV của JMeter và soak (tôi sẽ cung cấp header và 5 dòng mẫu đã che dữ liệu). Script phải đọc toàn file thật, kiểm tra cột bắt buộc, xử lý lỗi/giá trị thiếu, xuất số mẫu, success/error, responseCode, p50/p95/p99 của elapsed (ms) theo label và theo giai đoạn Stress/Spike, RPS theo cửa sổ thời gian rõ ràng, và tách ramp/plateau bằng thời điểm tôi cung cấp. Nêu quy ước percentile (ví dụ nearest-rank hoặc numpy) và không lấy trung bình các p95. Tránh tính gộp parent transaction sample với child request nếu cả hai có mặt. Script chỉ tính từ input, không chứa số liệu minh họa dễ nhầm là số thật. Cho lệnh chạy và cách đối chiếu vài dòng với HTML Dashboard.
```

### P17 — AI phân tích lần đầu từ số liệu thật

**Công dụng:** Tạo **AI analysis output gốc** để sau đó bạn phản biện. Không sửa lời AI này sau khi đã lưu audit.

```text
Đây là JTL THẬT của Load/Stress/Spike/soak [đính kèm file hoặc bảng xuất từ script với hash/tên file], cùng thông số run, cửa sổ ramp/plateau và tài nguyên backend [đính kèm]. Hãy phân tích từng scenario: throughput request/giây, p50/p95/p99 theo sáu nhãn, error rate và mã lỗi, giai đoạn stress đầu tiên mất ổn định, spike/recovery, ngưỡng endurance tối đa đã chứng minh trên phần cứng này. Đề xuất ngưỡng vận hành và tối ưu hóa. Với mỗi số, nêu file, nhãn, cửa sổ thời gian, số mẫu, đơn vị và cách tính; ghi “không đủ dữ liệu” nếu thiếu. Phân biệt RPS với workflow/giây; không coi HTTP 200 là đủ chứng minh CRUD đúng. Trả lời trước khi tôi đưa phần phản biện của mình.
```

### P18 — Tìm chỗ AI đọc sai và tự kiểm lại

**Công dụng:** Kiểm tra output P17 bằng JTL/script; không yêu cầu AI cố tình tạo sai lầm.

```text
Đây là nguyên văn phân tích trước của bạn [dán output P17] và bảng kết quả tôi tự tính trực tiếp từ JTL bằng [script/Excel; đính kèm đầu ra]. Hãy audit TỪNG khẳng định số của bạn: đúng/sai/chưa thể chứng minh, giá trị đúng, file/label/cửa sổ/số mẫu tương ứng, nguyên nhân sai (ms thành s, average thành p95, gộp ramp với plateau, lẫn RPS với workflow/s, tính cả assertion failures, v.v.). Đừng tự tạo “AI misinterpretation” nếu không có trong output gốc. Đưa danh sách câu tôi cần trích nguyên văn trong report và phép tính độc lập để tôi kiểm tra lại.
```

### P19 — Đánh giá tối ưu hóa theo code và số đo

**Công dụng:** Phân loại đề xuất AI là khả thi, chưa có căn cứ, hoặc hallucinated.

```text
Đây là danh sách tối ưu bạn đề xuất ở P17 [dán nguyên văn], code liên quan của server.js/database.js [đính kèm], schema SQLite [đính kèm], và bằng chứng nút thắt từ JTL/resource monitor [đính kèm]. Đánh giá TỪNG đề xuất: feasible / cần đo thêm / hallucinated-không phù hợp. Nêu vị trí code/schema, cơ chế dự kiến, chi phí/rủi ro, cách đo A/B để chứng minh; không khẳng định index hay WAL chắc chắn cải thiện nếu chưa benchmark. Ưu tiên login query, GET category/product, và ba thao tác category trên SQLite; đừng dùng lập luận từ checkout/cart vì không thuộc workflow này.
```

### P20 — Soạn GitHub Issue từ lỗi đã tái hiện (chỉ dùng khi có)

**Công dụng:** Viết issue rõ ràng từ bằng chứng thật; bạn kiểm tra và tự đăng.

```text
Tôi đã tái hiện lỗi THẬT sau [mô tả từng bước và request/response đã che token]. SUT commit [hash], môi trường [Node/OS], ảnh [tên file], log [JTL dòng/thời gian hoặc server log]. Hãy viết GitHub Issue ngắn gồm title, environment, preconditions, steps to reproduce, expected result theo spec, actual result, evidence links/placeholders và tác động. Nếu bằng chứng chưa đủ, liệt kê điều cần đo thêm thay vì khẳng định bug. Không tự đăng issue hoặc chế ảnh/log. Lỗi này [có/không] thuộc các endpoint Category CRUD.
```

## Mục 8 — Report, AI Critique/Audit, CI và Agent Skill

### P21 — Dàn ý report bám đúng chứng cứ

**Công dụng:** Tạo cấu trúc báo cáo Markdown/PDF đủ các mục, chưa viết kết luận trước khi có log.

```text
Hãy lập outline report HW05 theo đúng đề và workflow Admin Category CRUD. Dùng dữ liệu thật tôi đính kèm: ba JMX, CSV, bảng JTL/HTML, ảnh hardware/resource, soak, AI output + human review, GitHub Issues, video. Với mỗi mục, ghi bảng/ảnh/link cần đặt vào, số liệu nguồn cần đối chiếu và điều chưa có. Bắt buộc có: mục tiêu/phạm vi, AI-first và các sửa plan của con người, phương pháp Load/Stress/Spike/soak, hardware và hạn chế JMeter chạy cùng SUT, kết quả theo endpoint/giai đoạn, threshold có số, AI misinterpretation với giá trị đúng từ JTL, đánh giá tối ưu, CI proposal, kết luận. Không điền giá trị nào chưa có bằng chứng.
```

### P22 — Viết phần continuous performance testing (G9.6)

**Công dụng:** Hoàn thành đề xuất CI có flow chart và trade-off, không trộn kết quả chạy local với CI giả định.

```text
Đề xuất continuous performance testing cho EShop Node/Express/SQLite và workflow Admin Category CRUD. Trình bày flow chart Mermaid: commit/push -> phân loại file thay đổi -> smoke hoặc bỏ qua -> lịch nightly/PR có nguy cơ chạy load ngắn trên runner có cấu hình cố định -> thu JTL -> so p95 theo từng label với baseline và số mẫu tối thiểu -> cảnh báo/review -> phê duyệt cập nhật baseline. Đề xuất ngưỡng regression ví dụ >20% VÀ >200 ms nhưng ghi rõ chỉ là rule đề xuất, chưa phải SLO thực đo. Nêu cost, thời gian CI, dữ liệu category dọn không hết, nhiễu CPU vì máy chung, false alarms, false negatives, cách ổn định seed/runner và cách triage. Liên hệ với dữ liệu HW05 thật tôi cung cấp, không bịa pipeline đã triển khai.
```

### P23 — Viết AI Critique 200–300 từ từ bằng chứng riêng

**Công dụng:** Tạo bản nháp để bạn tự sửa thành đánh giá của mình, đúng giới hạn từ.

```text
Từ các mục AI Audit và bảng human review THẬT sau [đính kèm], hãy viết bản NHÁP AI Critique tiếng Anh 200–300 words. Phải trả lời: AI đã sai/thiếu/thiên lệch chỗ nào (trích ví dụ cụ thể từ Pxx và JTL), vì sao nó bỏ sót (prompt hoặc giới hạn mô hình/đặc điểm endpoint), tôi đã kiểm và sửa bằng cách nào, và nguyên tắc hợp tác với AI rút ra. Không tạo lỗi AI giả, không thêm số JTL chưa cung cấp. Đếm từ và ghi word count. Tôi sẽ tự sửa ngôn từ và đối chiếu lại mọi ví dụ trước khi đưa vào ai-critique.md/PDF.
```

### P24 — Sắp AI Audit từ transcript thật

**Công dụng:** Chuyển lịch sử AI đã dùng thành phụ lục có thể kiểm, không để AI dựng lại prompt theo trí nhớ.

```text
Tôi đính kèm transcript/export THẬT của các phiên AI và các file output. Hãy sắp xếp thành ai-audit.md với câu khai báo “I use AI tools for the following tasks,”. Với MỖI interaction, ghi tool/model, thời gian +07:00 nếu transcript có, prompt nguyên văn, output nguyên văn hoặc link tới file lưu nguyên văn, input attachment, và phần human review do tôi cung cấp. Giữ thứ tự thời gian, dùng ID Pxx khi khớp; prompt đã sửa khác mẫu thì lưu bản thực tế. Đánh dấu MISSING cho thông tin không có, tuyệt đối không bịa thời gian, prompt hay output. Cuối file liệt kê interaction/ảnh/log còn thiếu để tôi bổ sung. Bao gồm cả các trao đổi AI ở mục 1–3 nếu transcript có.
```

### P25 — Thiết kế Agent Skill tái dùng

**Công dụng:** Làm mục Agent Skill 10 điểm khi bạn quyết định thực hiện; phải có demo dùng thật.

```text
Thiết kế một Agent Skill tái sử dụng cho hiệu năng REST API, không gắn cứng MSSV hoặc endpoint EShop. Input: API spec/code, workflow 3 nhóm, CSV, giới hạn máy, JTL, resource logs. Output: checklist API, gợi ý Load/Stress/Spike, review JMX, script phân tích JTL, bảng AI-vs-human và AI Audit. Viết SKILL.md có trigger, workflow từng bước, quy tắc chứng cứ và các bước human approval/review; thêm ví dụ CHỈ minh họa bằng Category CRUD nhưng không giả vờ đã demo. Cho tôi checklist chạy demo end-to-end trên một endpoint group và những file/video thật phải lưu. Tránh tự thực thi test, upload hoặc publish nếu tôi chưa yêu cầu hành động đó.
```

### P26 — Kiểm tra demo Skill và video

**Công dụng:** Rà bản demo trước khi đưa link YouTube; AI chỉ review bằng chứng bạn cung cấp.

```text
Đây là SKILL.md thật, transcript lần tôi dùng skill trên [endpoint group], file đầu vào/đầu ra và timeline video [đính kèm]. Hãy đối chiếu rubric: có trigger rõ, quy trình tái sử dụng, AI Audit, human review, và demo end-to-end trên một nhóm endpoint không? Lập bảng PASS/FAIL và chỉ ra đoạn video/phút cần minh họa. Không nói đã xem video nếu tôi chỉ cung cấp transcript/timeline; không bịa cảnh quay.
```

## Mục 9 — Git, README, ZIP và nộp Moodle

### P27 — Hoàn thiện README và tự chấm

**Công dụng:** Đảm bảo README đúng mẫu chấm, mọi con số có nguồn.

```text
Đây là trạng thái file/repo, số liệu JTL đã kiểm, issue links, video URL và kết quả soak [đính kèm]. Hãy cập nhật bản NHÁP README.md có bảng tự chấm Load 30, Stress 20, Spike 20, AI analysis/misinterpretation 10, CI proposal 10, Agent Skill 10, tổng 100; cột điểm tự chấm để tôi tự quyết định. Thêm tóm tắt scenario đã chạy, ba nhóm endpoint trong workflow Admin, endurance threshold với số thật và điều kiện đo, số bug/performance issues, repo URL, video unlisted URL. Chỗ chưa có dữ liệu ghi TODO, không tự chấm tối đa hoặc bịa link.
```

### P28 — Rà commit log và cấu trúc repo

**Công dụng:** Kiểm tra mỗi bước có commit, không rò token/database thật vào GitHub.

```text
Đây là `git log --date=iso --pretty=fuller`, `git status`, danh sách file repo và `.gitignore` [đính kèm]. Hãy đối chiếu yêu cầu commit sau từng bước: ba plan, data, từng run/soak, AI analysis/critique, CI proposal, Skill. Chỉ ra bước nào chưa có commit hoặc commit thiếu file. Kiểm tra đường dẫn file/log/HTML report trong zip và cảnh báo nếu có JWT, mật khẩu cá nhân, database.sqlite đã sửa hoặc node_modules trong repo. Đưa lệnh PowerShell/Git để sửa các thiếu sót, nhưng không tự commit/push hay xóa dữ liệu.
```

### P29 — Soát báo cáo/PDF, bằng chứng và ZIP cuối

**Công dụng:** Kiểm tra trước khi nộp; AI chỉ đánh giá file/link thật.

```text
Audit bộ nộp HW05 hiện tại theo đề gốc. Tôi cung cấp cây file ZIP, tên file, report.md/PDF, ai-audit.md/PDF, ai-critique.md/PDF, 3 JMX, 3 JTL nguyên vẹn, 3 HTML folder, soak evidence, ảnh monitor/hardware, Git commit log, README, GitHub repo/Issues URL, YouTube Unlisted URL [đính kèm]. Lập bảng từng yêu cầu: PASS/FAIL/NOT VERIFIED, đường dẫn/link bằng chứng, thiếu gì, ưu tiên sửa. Kiểm tra tên ZIP 23120127_HW05_AI_Performance_[000-100].zip, ngày trong tên plan, 200–300 words AI Critique, video ≥6 phút có giọng tôi và tool+monitor cùng khung (chỉ xác nhận nếu có video thật), hostname phù hợp bài trước (chỉ xác nhận nếu có chứng cứ). Không đánh dấu PASS vì file chỉ được liệt kê mà chưa mở/kiểm. Kết luận readiness nộp Moodle và danh sách việc tôi phải tự kiểm cuối.
```

### P30 — Luyện vấn đáp 5–7 phút (tùy chọn)

**Công dụng:** Chuẩn bị giải thích công việc thật nếu được mời oral defense.

```text
Hãy phỏng vấn tôi như TA trong 5–7 phút về HW05 Category CRUD: vì sao chọn workflow và ba nhóm endpoint, CSV/100 admin account dựng thế nào, JWT/categoryId correlation, vì sao 3 scenario cùng workflow, cách xác định p95/RPS/soak threshold, một chỗ AI hiểu sai và tôi đã kiểm lại, tính khả thi của tối ưu, CI false alarm, nguồn gốc video/JTL/hardware. Hỏi từng câu một, chờ tôi trả lời rồi phản biện bằng dữ liệu report thật tôi đã đính kèm. Không đưa câu trả lời mẫu trước khi tôi trả lời.
```

## Prompt tìm hiểu riêng (dùng khi cần, cũng phải ghi AI Audit)

### P31 — Kiểm tra cách hiểu “transactional” của workflow

**Công dụng:** Chuẩn bị câu hỏi cho giảng viên nếu lo Category CRUD chưa đúng phạm vi. AI không thể thay quyết định của giảng viên.

```text
Đọc nguyên văn mục Scope — Endpoint Selection và workflow Category CRUD tôi chọn [đính kèm đề/trích đoạn]. Phân tích hai cách hiểu có thể có của “transactional”, trích đúng câu trong đề hỗ trợ từng cách hiểu, và soạn một câu hỏi ngắn lịch sự để tôi hỏi giảng viên/TA. Không tự khẳng định giảng viên đã chấp nhận workflow và không đề nghị đổi workflow nếu chưa có câu trả lời.
```

### P32 — Hiểu JTL, p95, throughput từ tài liệu chính thức

**Công dụng:** Kiểm tra kiến thức đo trước khi đọc kết quả, nhất là ms, percentile, RPS và sample cha/con.

```text
Giải thích cho tôi bằng ví dụ nhỏ do bạn tự gắn nhãn “minh họa” (không phải số liệu HW05): các cột timeStamp, elapsed, label, responseCode, success, threadName trong JTL CSV; cách tính p95 có quy ước rõ; throughput request/giây so với workflow/giây; vì sao không trung bình p95 và không tính trùng Transaction Controller parent với child. Nếu dựa vào hành vi JMeter, dẫn link tài liệu Apache chính thức và nêu điều nào phụ thuộc cấu hình phiên bản [phiên bản]. Kết thúc bằng checklist tôi phải kiểm trên JTL thật.
```

### P33 — Tìm hiểu SQLite/Node trước khi đánh giá tối ưu

**Công dụng:** Có kiến thức nền để phản biện gợi ý index/WAL/pool, không kết luận bằng suy đoán.

```text
Dựa trên code EShop tôi cung cấp và tài liệu SQLite/Node chính thức, giải thích ngắn: một sqlite3.Database kết nối trong database.js có ý nghĩa gì với nhiều request Express; lock/contention có thể xuất hiện ở Category CRUD thế nào; WAL giải quyết vấn đề nào và không giải quyết vấn đề nào; index trên users.email/categories.name có thể giúp trường hợp nào; cách dùng EXPLAIN QUERY PLAN hoặc đo A/B để xác minh. Tách “suy luận từ code” khỏi “đã đo trên máy tôi”. Không đề xuất sửa SUT trước khi có dữ liệu nút thắt.
```

### P34 — Kiểm tra bản ghi tài nguyên cùng máy

**Công dụng:** Chọn chỉ số monitor phù hợp khi JMeter và backend chạy chung Windows.

```text
Gợi ý bảng ghi tài nguyên mỗi 30 hoặc 60 giây trong Windows Task Manager/Performance Monitor cho bài test backend trên cùng máy với JMeter: node.exe PID, CPU%, working set/private bytes, tổng CPU/RAM, Java/JMeter PID và RAM, dung lượng database, thời gian. Giải thích dấu hiệu client generator bị giới hạn và cách báo hạn chế này trong report. Không tạo screenshot hoặc điền số liệu giả.
```

## Trình tự tối thiểu để không bỏ sót

`P00 → P02 → P03 → P04 → P05 → P06 → P07 → P08 → chạy smoke → P09 → calibration → P10/P11 → chạy 3 scenario + soak với P12 (P13 nếu gặp lỗi) → P14/P15 → P16 → P17 → P18 → P19 → P20 nếu có bug → P21/P22 → P23/P24 → P25/P26 nếu làm Skill → P27/P28/P29`.

P01 và P31–P34 dùng khi cần. P30 tùy chọn. Sau mỗi prompt, lưu audit ngay; sau mỗi mốc quan trọng, con người mở file/đọc số liệu/chạy thử rồi ghi quyết định sửa. Bài nộp phải dùng JTL, screenshot, hardware và video do bạn tạo từ chạy thật.
