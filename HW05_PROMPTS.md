# Bộ 15 prompt HW05 cho agent (P00–P14)

MSSV `23120127`; workflow cố định: **Admin Login → Categories List → Products List → Create Category → Update Category → Delete Category**. P00 và P01 bên dưới được giữ nguyên vì bạn đã gửi chúng. Từ P02, mỗi prompt giao agent **làm việc trực tiếp trên file/chạy lệnh, tự kiểm, trả lời và ghi AI Audit**. Chỗ `<...>` phải thay bằng giá trị thật khi gửi; prompt thực tế trong audit phải đúng nội dung đã gửi, kể cả chỗ bạn sửa.

AI Audit ghi tiếp vào `hw05-work/ai_audit.md`, nơi đã có P00/P01. File `hw05-work/ai-audit.md` hiện là bản trùng nội dung; đừng để hai bản cập nhật lệch nhau rồi nộp cả hai. Script ghi `Time` lúc hoàn tất câu trả lời theo +07:00; nếu cần giờ bắt đầu, đối chiếu transcript/UI và bổ sung. Agent không thể làm phần `Human review/correction` thay bạn: nó chỉ ghi “chờ người học kiểm tra”; sau mỗi lượt, bạn xem lại file/log và bổ sung phần đó. File output của agent, JTL, ảnh chụp, hardware và video phải là kết quả thật. Không ghi token JWT hay mật khẩu cá nhân vào audit.

## P00–P01 đã dùng (giữ nguyên prompt cũ)

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

## Từ P02: agent được thao tác file và chạy lệnh

Mỗi prompt dưới đây là **một nhiệm vụ cho agent**, không chỉ hỏi lời khuyên. Gửi P02 sau P00/P01. Trong mỗi lượt, agent phải thực hiện việc được giao, kiểm tra kết quả, ghi file, rồi trả lời. Nếu công cụ không cho phép một thao tác (đặc biệt ảnh màn hình, micro, upload video, Moodle), ghi rõ `CHƯA THỰC HIỆN` và việc người học cần làm; không tạo bằng chứng giả.

**Một file audit đích:** `hw05-work/ai_audit.md` (dấu gạch dưới), vì file này hiện có P00/P01. `ai-audit.md` đang là bản trùng; không ghi song song vào hai file. Cuối bài chọn một tên để nộp và đối chiếu nội dung trước khi xóa bản trùng. Mỗi prompt sau yêu cầu lưu nguyên văn tin nhắn người dùng vào `hw05-work/audit_inputs/Pxx.txt`, soạn câu trả lời cuối vào `hw05-work/audit_outputs/Pxx.md`, chạy `scripts/append_ai_audit.py`, rồi gửi lại **đúng nội dung đã lưu**. Script tự ghi thời gian thực +07:00, không ghi đè ID cũ, và để `Human review/correction` ở trạng thái chờ người học. Sau khi tự xem lại, người học bổ sung nhận xét vào entry đó; agent không tự nhận thay.

### P02 — Chốt thiết kế và thông số dự kiến

**Công dụng:** Gộp rà workflow, dữ liệu CSV, thiết kế JMeter và giả thuyết Load/Stress/Spike. **Đầu ra:** `design/test-design.md`; chưa chạy tải chính.

```text
[P02] Hãy THỰC HIỆN thiết kế HW05 trên workspace hiện tại. Đọc HW05_PLAN.md, hw05-work/workflow.md, dữ liệu CSV mẫu, API spec và route thật trong server.js. Ghi design/test-design.md: bảng 6 request cố định, body/header, JWT và categoryId correlation, tạo categoryName một lần/iteration từ category_prefix+UUID, assertion, cách xử lý login/POST lỗi, cleanup category, ba report view khác nhau. Đề xuất Load/Stress/Spike với VU/ramp/hold/think-time và tiêu chí pass/fail TRƯỚC khi đo; các số chỉ là giả thuyết, không là kết quả. Nêu rủi ro “transactional” cho CRUD và workflow trùng nhóm chưa được xác nhận. Tự rà lại với code, ghi giả định và commit file thiết kế.
Cuối lượt: lưu NGUYÊN VĂN toàn bộ tin nhắn P02 này vào hw05-work/audit_inputs/P02.txt; soạn câu trả lời cuối (file đã tạo, kiểm tra, commit, việc cần người học xác nhận) trong hw05-work/audit_outputs/P02.md; chạy từ thư mục gốc: python hw05-work/scripts/append_ai_audit.py --id P02 --purpose "Thiết kế test và workload" --tool-model "<tool/model thực tế hoặc không hiển thị>" --prompt-file hw05-work/audit_inputs/P02.txt --output-file hw05-work/audit_outputs/P02.md --inputs "HW05_PLAN.md; workflow.md; CSV; API spec; server.js". Sau đó gửi đúng nội dung P02.md, không thêm lời khác. Script ghi vào ai_audit.md; không sửa P00/P01 hoặc tự ghi Human review.
```

### P03 — Tạo cả ba JMeter plan

**Công dụng:** Gộp sinh Load, Stress, Spike vì cùng workflow, rồi kiểm tĩnh. **Đầu ra:** đúng 3 `.jmx` trong `plans/`.

```text
[P03] Dựa vào design/test-design.md đã duyệt, hãy TẠO và kiểm tĩnh đúng ba file plans/23120127_Load_<ngày thực tế YYYYMMDD>.jmx, ..._Stress_..., ..._Spike_... bằng JMeter thành phần lõi. Cả ba dùng cùng 6 sampler và nhãn; CSV ../data/admin${__threadNum}.csv; trích token từ login, id từ POST category; không hardcode token/password/category ID; tên category duy nhất theo iteration. Load có Summary Report, Stress có Aggregate Report, Spike có View Results Tree chỉ dùng debug và tắt khi CLI. Thiết kế Stress tuần tự 10/20/40/80 VU; Spike 10->80->10; Load mặc định 20 VU/60s ramp/8 phút, có tham số -Jvus/-Jramp/-Jduration cho soak. Rà XML, scope timer/assertion, logic dừng iteration khi thiếu JWT/categoryId, và kiểm khác biệt ba listener. Nếu JMeter đã có, dùng CLI/GUI khả dụng để xác nhận file nạp được; chưa chạy benchmark chính. Ghi lỗi AI tạo plan và tự sửa trong design/plan-review.md, nói vì sao lỗi xuất hiện. Commit từng plan riêng nếu có thể, hoặc commit nêu rõ từng file.
Cuối lượt: lưu nguyên văn P03 vào hw05-work/audit_inputs/P03.txt; viết câu trả lời cuối và đường dẫn/hash ba JMX vào hw05-work/audit_outputs/P03.md; chạy python hw05-work/scripts/append_ai_audit.py --id P03 --purpose "Tạo và rà ba JMX" --tool-model "<tool/model thực tế hoặc không hiển thị>" --prompt-file hw05-work/audit_inputs/P03.txt --output-file hw05-work/audit_outputs/P03.md --inputs "design/test-design.md; CSV; API spec; server.js". Gửi đúng nội dung P03.md. Không sửa P00/P01, không tự điền Human review.
```

### P04 — Smoke test và sửa plan

**Công dụng:** Chạy 1 VU/1 iteration trên từng plan, sửa lỗi thật trước benchmark. **Đầu ra:** log smoke và plan đã sửa.

```text
[P04] Hãy chạy SMOKE 1 VU/1 iteration cho từng JMX, không coi là Load/Stress/Spike chính. Trước khi chạy kiểm backend port 3000, 100 admin account/CSV, 3 category seed. Lưu log/response đã che JWT vào results/smoke, kiểm từng sampler, role admin, đúng categoryId và category count trước/sau. Nếu lỗi, phân biệt script/SUT/môi trường, sửa JMX tối thiểu và chạy lại; lưu bản lỗi và bản sửa trong design/plan-review.md. Không xóa category dư trước khi ghi bằng chứng; chỉ dọn category có prefix HW05_23120127 sau khi xác định ID. Không restart server nếu không cần vì sẽ reset DB. Ghi kết quả thật và commit sửa plan/báo cáo smoke, không tạo ảnh/log giả.
Cuối lượt: lưu nguyên văn P04 vào hw05-work/audit_inputs/P04.txt; viết câu trả lời cuối kèm số mẫu/lỗi và file chứng cứ thật vào hw05-work/audit_outputs/P04.md; chạy python hw05-work/scripts/append_ai_audit.py --id P04 --purpose "Smoke test và sửa plan" --tool-model "<tool/model thực tế hoặc không hiển thị>" --prompt-file hw05-work/audit_inputs/P04.txt --output-file hw05-work/audit_outputs/P04.md --inputs "ba JMX; data CSV; backend; smoke logs". Gửi đúng P04.md. Không sửa P00/P01, Human review để chờ tôi.
```

### P05 — Calibration và khóa cấu hình đo

**Công dụng:** Thăm dò mức tải, chốt tham số và chuẩn đánh giá trước ba run chính. **Đầu ra:** calibration log, config cuối và lý do.

```text
[P05] Hãy chạy calibration ngắn 5/10/20/40 VU, thêm 80 nếu máy còn ổn và dữ liệu đủ. Dùng cùng workflow đã smoke. Lưu JTL/log thăm dò riêng, theo dõi PID node.exe và Java/JMeter, CPU/RAM theo thời gian bằng công cụ thật có sẵn; nếu không thể chụp cùng màn hình, ghi nhiệm vụ ảnh cho tôi, đừng giả lập. Tính số mẫu, RPS, p95 từng sampler, lỗi và category dư theo từng mức. Chọn cấu hình cuối cho Load/Stress/Spike và tiêu chí ổn định trước đo; cập nhật JMX nếu cần. Kiểm tra TRƯỚC các run chính rằng có cách chụp tool + Task Manager cùng khung và quay video có giọng tôi; nếu chưa sẵn sàng, không bắt đầu P06–P08 mà báo việc cần chuẩn bị. Chỉ gọi đây là giả thuyết/calibration, chưa kết luận endurance threshold. Ghi phương pháp/tác động JMeter chạy cùng máy và commit bản thiết kế đã hiệu chỉnh.
Cuối lượt: lưu nguyên văn P05 vào hw05-work/audit_inputs/P05.txt; viết câu trả lời cuối với bảng đo thật và file nguồn vào hw05-work/audit_outputs/P05.md; chạy python hw05-work/scripts/append_ai_audit.py --id P05 --purpose "Calibration và tiêu chí đo" --tool-model "<tool/model thực tế hoặc không hiển thị>" --prompt-file hw05-work/audit_inputs/P05.txt --output-file hw05-work/audit_outputs/P05.md --inputs "JMX; calibration JTL; resource logs". Gửi đúng P05.md. Không tự ghi Human review.
```

### P06 — Chạy Load chính

**Công dụng:** Một prompt cho một run chính để audit và bằng chứng không lẫn. **Đầu ra:** JTL nguyên vẹn, HTML report, log, tài nguyên và ghi chú.

```text
[P06] Hãy chạy Load CHÍNH bằng JMX đã chốt, CLI JMeter -n -t -l -j -e -o, output riêng results/load, không ghi đè run cũ. Trước run kiểm server PID, 100 admin account/CSV, category count và cách chụp tool + Task Manager cùng khung/video thật đã sẵn sàng; nếu chưa, chuẩn bị phần độc lập và báo tôi trước khi bắt đầu run. Sau run kiểm .jtl đầy đủ, jmeter.log, html/index.html, số category dư. Ghi giờ bắt đầu/kết thúc, VU/ramp/hold/think-time và Node/JMeter CPU/RAM thật. Chụp ảnh thật nếu có UI; không tạo screenshot/video giả. Tóm tắt lỗi thực tế từ JTL nhưng chưa kết luận toàn bài; lưu run-manifest.md và commit metadata/báo cáo (không cần commit JTL lớn nếu đã lưu để zip).
Cuối lượt: lưu nguyên văn P06 vào hw05-work/audit_inputs/P06.txt; viết câu trả lời cuối với đường dẫn file kết quả, hash JTL, mục bằng chứng còn thiếu vào hw05-work/audit_outputs/P06.md; chạy python hw05-work/scripts/append_ai_audit.py --id P06 --purpose "Chạy Load chính" --tool-model "<tool/model thực tế hoặc không hiển thị>" --prompt-file hw05-work/audit_inputs/P06.txt --output-file hw05-work/audit_outputs/P06.md --inputs "Load JMX; CSV; JTL; HTML; resource evidence". Gửi đúng P06.md. Không tự ghi Human review.
```

### P07 — Chạy Stress chính

**Công dụng:** Ghi mức tải bắt đầu mất ổn định và dữ liệu từng tầng. **Đầu ra:** `results/stress/` và run manifest.

```text
[P07] Hãy chạy Stress CHÍNH bằng JMX đã chốt, các tầng VU tuần tự, CLI JMeter; lưu .jtl nguyên vẹn, jmeter.log và HTML trong results/stress, không ghi đè. Kiểm trước/sau giống P06, đặc biệt cách chụp tool + Task Manager cùng khung/video thật phải sẵn sàng trước run; nếu chưa, báo tôi trước khi bắt đầu. Ghi thời gian chính xác từng tầng, active threads, p95/error/RPS theo tầng từ log thật; không lấy p95 tổng run làm p95 từng tầng. Theo dõi Node/JMeter CPU/RAM và category dư. Nếu lockout/SQLITE_BUSY/crash, lưu bằng chứng trước khi xử lý; không tự loại lỗi khỏi JTL. Ảnh cùng khung phải là ảnh thật. Commit metadata/báo cáo của run.
Cuối lượt: lưu nguyên văn P07 vào hw05-work/audit_inputs/P07.txt; viết câu trả lời cuối, file/hash JTL và bằng chứng còn thiếu vào hw05-work/audit_outputs/P07.md; chạy python hw05-work/scripts/append_ai_audit.py --id P07 --purpose "Chạy Stress chính" --tool-model "<tool/model thực tế hoặc không hiển thị>" --prompt-file hw05-work/audit_inputs/P07.txt --output-file hw05-work/audit_outputs/P07.md --inputs "Stress JMX; CSV; JTL; HTML; resource evidence". Gửi đúng P07.md. Không tự ghi Human review.
```

### P08 — Chạy Spike chính

**Công dụng:** Đo đỉnh và hồi phục. **Đầu ra:** `results/spike/` và run manifest.

```text
[P08] Hãy chạy Spike CHÍNH bằng JMX đã chốt, nền -> spike -> hồi phục, CLI JMeter; lưu .jtl, jmeter.log, HTML riêng results/spike, không ghi đè. Kiểm trước/sau giống P06, đặc biệt cách chụp tool + Task Manager cùng khung/video thật phải sẵn sàng trước run; nếu chưa, báo tôi trước khi bắt đầu. Ghi mốc thời gian chuyển giai đoạn, active threads, p95/error/RPS theo từng giai đoạn và thời gian phục hồi; đừng nhầm khoảng trống do Thread Group tuần tự với downtime server. Theo dõi Node/JMeter CPU/RAM, category dư và log lỗi thật. Cần ảnh thật JMeter/CLI + Task Manager cùng khung khi đang chạy; không làm ảnh giả. Commit metadata/báo cáo.
Cuối lượt: lưu nguyên văn P08 vào hw05-work/audit_inputs/P08.txt; viết câu trả lời cuối, file/hash JTL và thiếu sót vào hw05-work/audit_outputs/P08.md; chạy python hw05-work/scripts/append_ai_audit.py --id P08 --purpose "Chạy Spike chính" --tool-model "<tool/model thực tế hoặc không hiển thị>" --prompt-file hw05-work/audit_inputs/P08.txt --output-file hw05-work/audit_outputs/P08.md --inputs "Spike JMX; CSV; JTL; HTML; resource evidence". Gửi đúng P08.md. Không tự ghi Human review.
```

### P09 — Soak 10–15 phút và ngưỡng phần cứng

**Công dụng:** Xác định mức chịu tải duy trì bằng thực nghiệm, không suy từ peak ngắn. **Đầu ra:** `results/soak/` và bảng ngưỡng.

```text
[P09] Dùng Load plan với -Jvus/-Jduration theo mức cao nhất còn ổn ở calibration/Stress, chạy soak giữ tải thật 10–15 phút SAU ramp. Lưu JTL, log, HTML và tài nguyên Node/JMeter theo phút trong results/soak, không ghi đè. Tính RPS sustained, p95/error từng endpoint, RAM đầu/cuối/max và xu hướng plateau hay tăng tiếp; nêu mức VU/RPS cao nhất ĐÃ THỬ và đạt tiêu chí, không gọi đó là khả năng tối đa tuyệt đối. Nếu chưa có mức ổn, ghi đúng như vậy. Kiểm category dư, backend PID và lưu ảnh/tài nguyên thật; nếu không chụp được, đánh dấu việc người học cần làm. Commit kết quả tóm tắt.
Cuối lượt: lưu nguyên văn P09 vào hw05-work/audit_inputs/P09.txt; viết câu trả lời cuối, file/hash và giới hạn kết luận vào hw05-work/audit_outputs/P09.md; chạy python hw05-work/scripts/append_ai_audit.py --id P09 --purpose "Soak và ngưỡng thực nghiệm" --tool-model "<tool/model thực tế hoặc không hiển thị>" --prompt-file hw05-work/audit_inputs/P09.txt --output-file hw05-work/audit_outputs/P09.md --inputs "Load JMX; soak JTL; resource log; tiêu chí trước đo". Gửi đúng P09.md. Không tự ghi Human review.
```

### P10 — Phân tích JTL bằng AI, lưu bản đầu tiên

**Công dụng:** Tạo script phân tích tái lập và giữ nguyên AI analysis ban đầu để phản biện ở P11. **Đầu ra:** script, bảng số và `analysis/ai-first-pass.md`.

```text
[P10] Hãy đọc bốn JTL THẬT (Load/Stress/Spike/soak), run manifests, resource logs và HTML. TRƯỚC TIÊN viết AI analysis lần đầu vào analysis/ai-first-pass.md từ log: từng scenario, đề xuất threshold và tối ưu, mỗi số dẫn file/label/cửa sổ/n mẫu; lưu file này NGUYÊN TRẠNG, không sửa lại sau khi tự kiểm. SAU ĐÓ tạo scripts/analyze_jtl.py độc lập đọc toàn file, kiểm header/cột, tính n, lỗi, responseCode, RPS, p50/p95/p99 elapsed-ms theo 6 nhãn và từng giai đoạn; công bố quy ước percentile, tách ramp/hold và tránh tính trùng parent/child. Chạy script, lưu bảng output riêng để P11 đối chiếu với AI first pass. Không bịa số hoặc lấy trung bình p95. Commit script và bản phân tích đầu.
Cuối lượt: lưu nguyên văn P10 vào hw05-work/audit_inputs/P10.txt; viết câu trả lời cuối, đường dẫn/hash JTL, script, bảng và các giả định vào hw05-work/audit_outputs/P10.md; chạy python hw05-work/scripts/append_ai_audit.py --id P10 --purpose "Phân tích JTL lần đầu" --tool-model "<tool/model thực tế hoặc không hiển thị>" --prompt-file hw05-work/audit_inputs/P10.txt --output-file hw05-work/audit_outputs/P10.md --inputs "4 JTL; manifests; resource logs; HTML". Gửi đúng P10.md. Không tự ghi Human review.
```

### P11 — Phản biện AI, tối ưu và issue

**Công dụng:** So lại AI first pass với JTL/code, viết bảng misinterpretation và issue có chứng cứ. **Đầu ra:** `analysis/human-review-draft.md`, issue draft hoặc link issue thật.

```text
[P11] Audit từng khẳng định trong analysis/ai-first-pass.md bằng script/JTL gốc, tìm sai lệch THẬT (ms/s, average/p95, RPS/workflow/s, gộp giai đoạn, 200 nhưng CRUD sai). Lập bảng câu AI nguyên văn -> giá trị đúng -> file/label/cửa sổ/n -> phép tính -> nguyên nhân sai; nếu không có sai số, ghi không tìm thấy, không dựng lỗi AI. Đối chiếu mỗi đề xuất tối ưu với server.js, database.js/schema và resource evidence: feasible/cần đo thêm/hallucinated, cách đo A/B. Kiểm lỗi thật liên quan Category CRUD (role thường, PUT/DELETE ID không tồn tại) bằng test nhỏ tách khỏi benchmark; lưu bằng chứng, soạn issue chỉ khi tái hiện. Tôi cho phép agent đăng GitHub Issue vào repo HW05 của tôi cho lỗi đã tái hiện và có bằng chứng thật; nếu chưa có repo/link hoặc công cụ không truy cập được, lưu draft và báo rõ. Không sửa AI first pass. Commit bản review/issue draft.
Cuối lượt: lưu nguyên văn P11 vào hw05-work/audit_inputs/P11.txt; viết câu trả lời cuối với số JTL đã kiểm, các lỗi AI thật và issue URL/draft vào hw05-work/audit_outputs/P11.md; chạy python hw05-work/scripts/append_ai_audit.py --id P11 --purpose "Phản biện AI và đánh giá tối ưu" --tool-model "<tool/model thực tế hoặc không hiển thị>" --prompt-file hw05-work/audit_inputs/P11.txt --output-file hw05-work/audit_outputs/P11.md --inputs "ai-first-pass; JTL; script output; code/schema; evidence". Gửi đúng P11.md. Human review chờ tôi xác nhận.
```

### P12 — Report, CI proposal và AI Critique

**Công dụng:** Gộp tài liệu phân tích cuối và đề xuất G9.6. **Đầu ra:** `report.md`, PDF nếu có công cụ, `ai-critique.md`/PDF, flow chart.

```text
[P12] Từ bằng chứng thật và P11, viết report.md đầy đủ cho HW05 workflow Admin: mục tiêu, AI-first và sửa plan, cấu hình/hardware, 3 run + soak với bảng có đơn vị/n mẫu, threshold, hình/link thật, AI misinterpretation có số JTL đúng, đánh giá tối ưu, hạn chế cùng máy, GitHub Issues và kết luận. Thêm continuous performance testing model với flow chart Mermaid: commit -> chọn run -> runner cố định -> JTL -> so p95 theo endpoint và baseline -> cảnh báo/review; bàn cost và false alarms, threshold CI chỉ là đề xuất. Viết ai-critique.md tiếng Anh 200–300 từ dựa đúng lỗi AI đã tìm; đếm từ và để tôi tự chỉnh. Xuất PDF bằng công cụ có sẵn nếu làm được, mở/kiểm trang; nếu không, ghi rõ cách tôi xuất. Chỗ thiếu ảnh/video/link để TODO, không tạo giả. Commit tài liệu.
Cuối lượt: lưu nguyên văn P12 vào hw05-work/audit_inputs/P12.txt; viết câu trả lời cuối, file PDF đã kiểm và các TODO vào hw05-work/audit_outputs/P12.md; chạy python hw05-work/scripts/append_ai_audit.py --id P12 --purpose "Report CI và AI Critique" --tool-model "<tool/model thực tế hoặc không hiển thị>" --prompt-file hw05-work/audit_inputs/P12.txt --output-file hw05-work/audit_outputs/P12.md --inputs "JTL analysis; human review; evidence; issues; HW05 PDF". Gửi đúng P12.md. Human review chờ tôi.
```

### P13 — Agent Skill, demo và video chính

**Công dụng:** Làm Skill 10 điểm và chuẩn bị video ≥6 phút, phần hình/giọng do bạn quay thật. **Đầu ra:** `skill/SKILL.md`, demo files, storyboard.

```text
[P13] Hãy tạo reusable Agent Skill trong hw05-work/skill/SKILL.md cho thiết kế performance REST API, rà JMX, chạy log và phân tích JTL, AI Audit + human review. Đừng gắn cứng MSSV/Category CRUD trong phần tái dùng; demo Skill bằng một endpoint group thật của EShop nếu môi trường sẵn có, lưu transcript và output thật, không tuyên bố demo nếu chưa chạy. Tạo storyboard/thuyết minh tiếng Việt cho video YouTube Unlisted tổng ≥6 phút: từng Load/Stress/Spike phải có công cụ + Task Manager cùng khung, giọng nói của tôi, hardware, soak, AI critique, và đoạn demo skill hoặc video riêng. Agent chỉ chuẩn bị script/checklist, không tạo giọng/ảnh/video giả hoặc upload thay tôi khi chưa có khả năng/quyền. Ghi link thật khi tôi cung cấp. Commit Skill và storyboard.
Cuối lượt: lưu nguyên văn P13 vào hw05-work/audit_inputs/P13.txt; viết câu trả lời cuối, demo thật đã chạy và việc tôi phải tự quay/nói vào hw05-work/audit_outputs/P13.md; chạy python hw05-work/scripts/append_ai_audit.py --id P13 --purpose "Agent Skill và video demo" --tool-model "<tool/model thực tế hoặc không hiển thị>" --prompt-file hw05-work/audit_inputs/P13.txt --output-file hw05-work/audit_outputs/P13.md --inputs "skill files; demo transcript; run evidence; video link nếu có". Gửi đúng P13.md. Human review chờ tôi.
```

### P14 — Hoàn thiện audit, README, Git log, ZIP và QA

**Công dụng:** Rà gói nộp cuối, không đánh dấu PASS khi bằng chứng còn thiếu. **Đầu ra:** README, audit PDF, git log, ZIP theo tên, checklist.

```text
[P14] Hãy kiểm toàn bộ bài theo PDF đề và HW05_PLAN.md. Gộp/chuẩn hóa các entry THẬT P00–P13 trong ai_audit.md (không bịa prompt/output/time; Human review chưa có thì ghi pending); xuất ai_audit.pdf và ai-critique.pdf nếu chưa có. Cập nhật README bảng tự chấm 30/20/20/10/10/10 bằng điểm tôi cung cấp, tóm tắt 3 scenario, endpoint groups, endurance số thật, số issue và video URL. Tạo git-commits.txt từ git log thật, kiểm repo public/link, ba JMX đúng tên 23120127_*_<YYYYMMDD>.jmx, ba JTL đầy đủ, ba HTML, ảnh hardware + tool/monitor, video Unlisted ≥6 phút có giọng tôi, Skill/demo, report/Audit/Critique Markdown+PDF. Nếu thiếu bằng chứng, dừng đóng gói và liệt kê TODO rõ. Nếu đủ, commit tài liệu, xuất lại git-commits.txt, tạo ZIP 23120127_HW05_AI_Performance_<điểm 3 chữ số>.zip và mở kiểm nội dung. Sau khi ghi entry P14 bằng lệnh audit cuối prompt, xuất lại ai_audit.pdf, tạo lại ZIP để chứa entry P14 và PDF mới, rồi mở kiểm ZIP lần nữa. Nếu lần kiểm cuối lỗi, báo đúng lỗi và sửa entry P14/output trước khi gửi; không tự submit Moodle.
Cuối lượt: lưu nguyên văn P14 vào hw05-work/audit_inputs/P14.txt; viết câu trả lời cuối với bảng PASS/FAIL/NOT VERIFIED và đường dẫn ZIP nếu có vào hw05-work/audit_outputs/P14.md; chạy python hw05-work/scripts/append_ai_audit.py --id P14 --purpose "QA và đóng gói HW05" --tool-model "<tool/model thực tế hoặc không hiển thị>" --prompt-file hw05-work/audit_inputs/P14.txt --output-file hw05-work/audit_outputs/P14.md --inputs "toàn bộ bài; đề PDF; git log; links; video". Gửi đúng P14.md. Human review chờ tôi.
```

## Thứ tự và điểm dừng cần người học

`P00, P01` đã dùng. Tiếp tục `P02 → P03 → P04 → P05 → P06 → P07 → P08 → P09 → P10 → P11 → P12 → P13 → P14`. Tổng cộng **15 prompt**. Trước P06–P09, bố trí quay màn hình/chụp Task Manager khi run đang diễn ra; ảnh sau run không thay thế được. Sau mỗi lượt, tự mở file/log, bổ sung mục `Human review/correction` ở đúng entry trong `ai_audit.md`. Trước P14, cung cấp video thật, link GitHub/Issues, điểm tự chấm và xác nhận workflow với nhóm. Nếu thiếu đầu vào, agent phải báo thiếu và tiếp tục phần độc lập; không điền số hay bằng chứng giả.
