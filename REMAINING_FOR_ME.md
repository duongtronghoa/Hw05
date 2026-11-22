# Việc bạn cần làm để hoàn tất và nộp HW05

**MSSV:** 23120127. **Ngày rà soát:** 2026-11-22 (+07:00). **Repo:** https://github.com/duongtronghoa/Hw05. Workflow Admin Login → Categories List → Products List → Create → Update → Delete Category đã được bạn xác nhận không trùng trong nhóm. File này là checklist hành động cho chính bạn; chỉ đánh dấu xong khi đã mở và kiểm bằng chứng thật.

## 0. Trạng thái kỹ thuật đã có để bạn bắt đầu từ đúng chỗ

- Ba plan cuối nằm trong `plans/`, đã smoke đủ sáu request 1 VU/1 iteration. Các lần đo Load/Stress/Spike đã có raw JTL, `jmeter.log`, HTML Dashboard, CSV tài nguyên, snapshot category và manifest ở `results/load`, `results/stress`, `results/spike`.
- Có calibration 5/10/20/40/80 VU trong `results/calibration`, bảng `design/calibration.md`, cấu hình máy ở `evidence/hardware-spec.json`/`.md`, CI proposal, Agent Skill và demo đọc hai endpoint. Soak dùng 80 VU, ramp 30 giây, duration 660 giây, monitor Node+JMeter; xem `results/soak` sau khi kết thúc.
- Các lượt đo này là **bằng chứng kỹ thuật thật nhưng chưa có ảnh/video**. Scheduler JMeter dừng một số thread giữa POST và DELETE; sau mỗi run đã lưu ID/tên category thử rồi dọn về 3 seed. Báo cáo phải giữ sự thật này, không viết “toàn bộ workflow đều hoàn thành” chỉ vì JTL có 0 request lỗi.
- `ai_audit.md` là bản audit đang dùng. `ai-audit.md` là bản cũ trùng/thiếu các entry mới; **không nộp cả hai**. Các entry P04 trở đi ghi đúng yêu cầu bạn gửi cho agent cùng tham chiếu prompt mẫu trong `HW05_PROMPTS.md`; bạn cần tự viết phần Human review/correction.

## 1. Chuẩn bị các công cụ và xác minh máy trước khi quay

Các công cụ đã có trên máy: Apache JMeter 5.6.3 ở `C:\tools\apache-jmeter-5.6.3\bin\jmeter.bat`, Java 25, Node 25, Python 3.12, OBS Studio ở `C:\Program Files\obs-studio\bin\64bit\obs64.exe`, Task Manager, dxdiag và Chrome. Không cần tải thêm ứng dụng để quay nếu OBS hoạt động. Cần đăng nhập trình duyệt YouTube, GitHub và Moodle bằng tài khoản của bạn; kiểm tra dung lượng đĩa trước khi quay.

1. Mở PowerShell tại `C:\Users\duong\Downloads\New folder (33)`. Kiểm `http://localhost:3000/api/products`. Nếu backend không chạy, mở **PowerShell thứ hai**, vào `src\eshop-sut\backend`, chạy `node server.js` và giữ cửa sổ đó mở. **Mỗi lần khởi động lại Node, database bị DROP/seed**: quay về thư mục gốc, chạy `python hw05-work\scripts\prepare_admin_data.py`, kiểm lại 102 users và 3 categories trước khi chạy. Không chạy `database.js` riêng.
2. Mở `dxdiag` → tab **System**, chụp thật và lưu `hw05-work/evidence/dxdiag-system.png`. Kiểm hostname trên ảnh là `TRONGHOA` và **tự đối chiếu với bài triển khai trước**; nếu khác, giải thích trong report, không sửa ảnh. Bảng text ở `evidence/hardware-spec.md` đã có CPU/RAM/OS/GPU, nhưng không thay ảnh dxdiag.
3. Mở Task Manager → **Details** hoặc **Performance** để thấy CPU/RAM của backend `node.exe`, PID backend và tổng tài nguyên. Mở JMeter GUI/CLI bên cạnh, sắp cửa sổ sao cho **công cụ và Task Manager cùng một khung hình**. Nếu JMeter có hai `java.exe`, tiến trình con có Working Set lớn mới là load generator thực.
4. Mở OBS, chọn Display Capture và microphone của bạn; ghi clip thử 20–30 giây. Xem lại: chữ JMeter/Task Manager đọc được, mic tiếng Việt rõ, không lộ JWT hay mật khẩu trong CSV/terminal. Đảm bảo laptop cắm nguồn, các app nặng khác tắt. Bấm Record **trước** lệnh test, Stop sau khi đã chụp màn hình và nêu số đo.

## 2. Quay bổ sung bằng chứng Load, Stress, Spike

Các raw JTL hiện có vẫn giữ nguyên. Vì bạn chưa thể quay lúc agent chạy, hãy chạy lại **cùng tham số** khi sẵn sàng và lưu trong thư mục tên mới, không ghi đè `load.jtl`/`stress.jtl`/`spike.jtl` cũ. Trước từng run xác nhận backend còn sống, có 100 CSV, 102 users, 3 seed categories. Sau run ghi cả JTL mới, ảnh/video và thời gian vào report; nói rõ đâu là lượt đo kỹ thuật cũ, đâu là lượt quay bổ sung. Trong lúc chạy từng scenario, bấm `Win+Shift+S` (hoặc dùng OBS snapshot) và lưu đúng tên:

- `hw05-work/evidence/load-live.png`
- `hw05-work/evidence/stress-live.png`
- `hw05-work/evidence/spike-live.png`

Ảnh phải chụp khi **test đang chạy**, có JMeter/CLI + tài nguyên backend trong Task Manager cùng khung, không lấy ảnh HTML sau chạy để gọi là ảnh live. Với Stress nên bắt ít nhất tầng 80 VU; Spike nên có khung lúc 80 VU và khung hồi phục (có thể thêm `spike-recovery-live.png`). `View Results Tree` của Spike tắt trong CLI để tránh ngốn RAM; nếu muốn chứng minh view thứ ba, mở JTL trong JMeter GUI sau run, xem dữ liệu thật và chụp riêng ảnh debug, ghi rõ thời điểm.

**Lệnh Load**, chạy từ thư mục gốc trong khi OBS đang ghi:

```powershell
$run = Get-Date -Format 'yyyyMMdd_HHmmss'
$out = "hw05-work\results\load\recorded_$run"
New-Item -ItemType Directory -Path $out | Out-Null
& 'C:\tools\apache-jmeter-5.6.3\bin\jmeter.bat' -n -t 'hw05-work\plans\23120127_Load_20261122.jmx' -l "$out\load.jtl" -j "$out\jmeter.log" -e -o "$out\html"
```

**Lệnh Stress** (đổi `load` → `stress`, plan tương ứng):

```powershell
$run = Get-Date -Format 'yyyyMMdd_HHmmss'
$out = "hw05-work\results\stress\recorded_$run"
New-Item -ItemType Directory -Path $out | Out-Null
& 'C:\tools\apache-jmeter-5.6.3\bin\jmeter.bat' -n -t 'hw05-work\plans\23120127_Stress_20261122.jmx' -l "$out\stress.jtl" -j "$out\jmeter.log" -e -o "$out\html"
```

**Lệnh Spike**:

```powershell
$run = Get-Date -Format 'yyyyMMdd_HHmmss'
$out = "hw05-work\results\spike\recorded_$run"
New-Item -ItemType Directory -Path $out | Out-Null
& 'C:\tools\apache-jmeter-5.6.3\bin\jmeter.bat' -n -t 'hw05-work\plans\23120127_Spike_20261122.jmx' -l "$out\spike.jtl" -j "$out\jmeter.log" -e -o "$out\html"
```

Đợi CLI thoát mã 0 và kiểm `$out\html\index.html`. Sau đó lưu snapshot/dọn đúng dữ liệu thử **sau khi đã giữ JTL/log/ảnh**:

```powershell
python hw05-work\scripts\category_state.py --snapshot "$out\categories_after.csv" --cleanup
```

Kiểm dòng `remaining=3`. Nếu không phải 3, mở snapshot, kiểm ID/tên; chỉ xóa category của bài có prefix `HW05_23120127_`, không reset database trước khi giữ chứng cứ. Nếu login bị khóa, giữ lỗi trong JTL rồi xử lý: tài khoản demo bị lock 180 giây do code hiện tại; đợi đủ thời gian hoặc restart Node và chuẩn bị lại 100 admin, ghi phương án. Không xóa các dòng lỗi khỏi JTL.

## 3. Video Unlisted ít nhất 6 phút, giọng Việt của bạn

Theo storyboard `evidence/video-storyboard.md`: giới thiệu máy/workflow; chứng minh Load/Stress/Spike với **công cụ + Task Manager trong cùng khung**; giải thích soak/ngưỡng, một chỗ AI sai/thiếu, rồi demo Agent Skill trên **cả nhóm read-heavy** gồm `02_categories_list` và `03_products_list`. Bạn phải tự thuyết minh bằng tiếng Việt. Có thể một video hoặc nhiều clip theo scenario, tổng thời lượng ≥6 phút; nếu tách clip, ghi URL và thời lượng từng clip, tổng thời lượng. Đừng cắt ghép làm sai phase/thời điểm tài nguyên. YouTube chọn **Unlisted**, kiểm link bằng cửa sổ ẩn danh. Tạo `evidence/video-links.md` với URL thật, thời lượng, nội dung từng clip; cập nhật report và README. File `skill/hw05-api-performance/demo.md` có output text thật để bạn trình bày, **không thay video**.

## 4. Phần bạn phải tự đọc, nhận xét và sửa

1. Mở `ai_audit.md`. Với **từng entry P00–P14 và P90–P92**, đọc Prompt/AI output, mở file nguồn và ghi vào `Human review/correction` điều bạn tự xác nhận, sửa gì, vì sao, bằng chứng cụ thể (JTL/line code/ảnh/commit). Không sao chép lời AI thành nhận xét của mình. P00/P01 đã có nhận xét trong bản trước: tự xác nhận lại, đặc biệt P01 nhắc SHA-512 nhưng chưa lưu hash đối chiếu. P02 được ghi sau P03 theo thời gian; giữ đúng lịch sử và giải thích là lượt rà soát sau nếu transcript xác nhận. P02/P03 prompt đã lưu có thể khác mẫu hiện tại, đối chiếu chính tin nhắn thật trước khi sửa, không thay bằng prompt mẫu cho “đẹp”.
2. Xem `design/plan-review.md` và diff commit `59aaf16`: P03 chỉ nạp XML, điều kiện If Controller làm mất 5 request; bản sửa Groovy lỗi với Java 25; bản cuối `__jexl3` đã smoke sáu request. Tự mở `results/smoke/*jtl` để xác nhận. Nhận xét rõ timer 1–3 giây áp dụng cả login, POST/PUT/DELETE trả 200 chưa đủ chứng minh cập nhật đúng nếu ID sai.
3. Xem `design/calibration.md`, `evidence/*-run.md`, JTL/manifest gốc. Tự tính lại ít nhất vài p95, RPS, số mẫu/lỗi; đối chiếu số của AI first pass và bảng kiểm độc lập. Viết bằng lời của bạn vì sao AI diễn giải sai hoặc thiếu, không tạo lỗi giả. Nhận xét mức 80 VU chỉ là mức cao nhất **đã thử** trên máy chung Node+JMeter, không phải sức chịu tải tối đa tuyệt đối.
4. Đọc `ai-critique.md` (bản nháp agent) và sửa thành trải nghiệm của chính bạn 200–300 từ: AI sai/thiếu ở đâu, nguyên nhân, bạn kiểm/sửa thế nào, nguyên tắc học được. Cập nhật cả phụ lục trong `report.md`, rồi xuất lại PDF nếu sửa Markdown. Không ghi “tôi đã tự kiểm” nếu chưa thật sự làm.
5. Kiểm phần CI flowchart và trade-offs trong report; các ngưỡng 20%/100 mẫu/2 lượt là **đề xuất**, không phải số đo SUT. Kiểm Agent Skill và demo thật sự áp dụng trọn nhóm endpoint. Nếu rubric transactional bị hiểu hẹp là cart/checkout, hỏi giảng viên/TA trước khi nộp; nhóm bạn đã xác nhận không trùng, nhưng phân loại Category CRUD vẫn cần được giải thích rõ.

## 5. Bug issue và ảnh (sau khi xem bằng chứng)

Các case phụ C07–C09 được tách khỏi benchmark. Nếu `analysis/edge-cases.json` có kết quả tái hiện, đọc JSON và `src/eshop-sut/README.md` FR-02/FR-12 trước khi đăng issue. C07: lock sau hai lần sai và 180 giây so với đặc tả ba lần/30 giây. C08: user thường ghi category dù FR-12 đòi admin. C09: PUT/DELETE ID không tồn tại trả 200, nhưng API spec chưa nêu rõ 404 nên không tự gọi là bug đã xác nhận. Tự chạy lại case cần chụp, lấy **ảnh màn hình thật** của request/response đã che JWT/mật khẩu, lưu `evidence/issue-c07.png`/`issue-c08.png`, rồi đăng GitHub Issues ở repo public với expected/actual, bước tái hiện, commit SUT, ảnh và link. Nếu đã có issue do agent tạo, bổ sung ảnh/comment thay vì tạo trùng. Ghi URL vào report/README; nếu không có bug tái hiện, ghi trung thực 0 issue.

## 6. Kiểm report, PDF, GitHub, tự chấm và ZIP

1. Đọc `report.md`, `ai-critique.md`, `ai_audit.md` và các PDF tương ứng. Đối chiếu mọi số với JTL/manifest. Các PDF phải mở được, chữ Việt và bảng không bị cắt. Nếu bạn sửa Markdown, chạy `python hw05-work\scripts\export_markdown_pdf.py hw05-work\report.md hw05-work\report.pdf` (tương tự Critique/Audit), rồi xem lại PDF. Đảm bảo report có phần ảnh, link video, hardware, ba nhóm endpoint, ba scenario, soak, AI correction, issue và CI chart.
2. Kiểm https://github.com/duongtronghoa/Hw05 public và đã có plan/data/commit mới. Không push `node_modules`, database SQLite, JWT, mật khẩu cá nhân hoặc video raw. `git-commits.txt` phải xuất từ `git log` thật. Trong README tự cho điểm **theo sáu dòng 30/20/20/10/10/10**, tổng 0–100, viết ba chữ số `000`–`100`, có lý do ngắn cho từng dòng. Điền link repo, video, issue và tóm tắt ngưỡng đo thật.
3. Khi đủ ảnh/video/Human review/PDF/điểm, chạy từ thư mục gốc: `python hw05-work\scripts\package_submission.py --grade <điểm bạn tự chấm>`. Script chỉ tạo `23120127_HW05_AI_Performance_<3 chữ số>.zip` khi các file bắt buộc có mặt; mở ZIP kiểm lại raw JTL nguyên vẹn, ba HTML folders, PDF, ảnh và link. Nếu script báo thiếu, bổ sung đúng file rồi chạy lại; đừng đổi tên một file khác để qua kiểm tra.
4. Tự upload ZIP lên Moodle trước hạn **hiển thị ở link nộp**, không suy ra hạn từ tên PDF. Giữ ảnh/xác nhận Moodle đã nhận bài. Chuẩn bị giải thích 5–7 phút: workflow/CSV/correlation, lỗi AI sửa plan, số p95/RPS theo phase, category tồn dư, ngưỡng soak và giới hạn máy chung, CI proposal, AI critique.

**Không có cách tự động hợp lệ thay cho** ảnh/live video có giọng bạn, Human review cá nhân, điểm tự chấm và thao tác nộp Moodle. Sau khi bạn có các file đó, có thể yêu cầu agent rà lại lần cuối để phát hiện số/link/định dạng lệch trước khi nộp.
