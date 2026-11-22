# Kiểm tra gói nộp HW05 — MSSV 23120127

**Nguồn đối chiếu:** `2026.HW05.Performance Testing_En (1).pdf`, trang 4–9, lưu ngoài ZIP tại thư mục cha. **Tên ZIP theo điểm sinh viên tự chấm:** `23120127_HW05_AI_Performance_100.zip`. Điểm 100 do sinh viên cung cấp, không phải điểm đã được chấm.

## 1. Đối chiếu trực tiếp với đề

| Yêu cầu trong đề | Trang | File/đường dẫn trong ZIP | Kết quả QA |
|---|---:|---|---|
| Báo cáo chính Markdown + PDF, mô tả quy trình, kết quả, critique | 4–6, 8 | `report.md`, `report.pdf` | Có; PDF đọc được, 6 trang. |
| Link GitHub repo công khai, plans và data | 8 | `README.md`, `report.md`, `plans/`, `data/` | Repo `duongtronghoa/Hw05` được `gh` xác nhận PUBLIC tại lượt QA; 3 plan và 100 CSV. |
| Ba plan đúng tên MSSV–scenario–ngày; workflow giống nhau; ba nhóm API; CSV; ba listener khác loại | 4, 7–8 | `plans/23120127_{Load,Stress,Spike}_20261122.jmx`, `data/admin1.csv`–`admin100.csv` | Có. Listener View Results Tree của Spike tắt khi chạy CLI để giảm tải; cấu hình vẫn ở JMX để xem lúc debug. |
| Human review plan: chỉ ra lỗi AI và sửa | 4–5 | `design/plan-review.md`, `report.md`, `ai_audit.md` | Có văn bản; lời khai ngôi thứ nhất cần sinh viên xác nhận. |
| Ba lần chạy, mỗi lần ảnh JMeter + Resource Monitor cùng khung | 5, 8 | `evidence/load-live.png`, `stress-live.png`, `spike-live.png` | Ảnh hiện diện và quan sát được hai cửa sổ. **Khoảng trống truy nguyên:** lệnh trong ảnh ghi `tmp_*.jtl`; file tạm không có trong ZIP, nên không chứng minh ảnh thuộc cùng lượt chạy với JTL chính thức. |
| Ba raw JTL đầy đủ và ba thư mục HTML report | 5, 7–8 | `results/{load,stress,spike}/*.jtl`, `results/{load,stress,spike}/html/` | Có; log thô đọc được, HTML có `index.html` và tài nguyên phụ. |
| Ảnh hardware và bảng cấu hình, hostname khớp | 5, 7–8 | `evidence/dxdiag-system.png`, `hardware-spec.md`, `hardware-spec.json` | Ảnh cho thấy TRONGHOA, i7-12700H, 16 GB; không có hồ sơ bài trước trong gói để xác minh đối chiếu hostname lịch sử. |
| Soak 10–15 phút; ngưỡng RPS/bộ nhớ có số liệu | 5 | `results/soak/`, `evidence/soak-run.md`, `report.md` | Có 630 giây giữ tải, 39,711 req/s, Private Bytes cao nhất 96,45 MiB. **Chưa xác định điểm bão hòa hoặc trần bộ nhớ**; báo cáo đã sửa để không gọi giá trị quan sát là trần. |
| Video YouTube Unlisted ≥6 phút, cùng khung tool + monitor, giọng sinh viên tiếng Việt | 5, 7–8 | `evidence/video-links.md` | URL `https://youtu.be/lk0vSGCapsc` được kiểm tra metadata: Unlisted, 424 giây (7:04). **Chưa kiểm độc lập toàn bộ hình ảnh, âm thanh và giọng**; sinh viên cần xem lại video. |
| Bug report có ảnh trên GitHub Issues, nếu phát hiện lỗi | 5, 8 | `analysis/edge-cases.json`, `analysis/human-review-draft.md` | **THIẾU:** C07/C08 có log tái hiện nhưng `gh issue list` trả 0 issue; chưa có ảnh lỗi. C09 là quan sát, chưa đủ căn cứ gọi bug. |
| AI phân tích JTL, người học sửa sai bằng giá trị raw log và đánh giá optimization | 5–6 | `analysis/ai-first-pass.md`, `analysis/jtl-metrics-ground-truth.json`, `analysis/human-review-draft.md`, `report.md` | Có; report đã sửa số p95 theo JTL. Bản human review vẫn là nháp để sinh viên xác nhận. |
| Continuous performance model, flow chart, cost/false alarms | 6 | `analysis/ci-proposal.md`, `design/` và mục 5 `report.md` | Có flow chart và phần trade-offs. |
| Agent Skill và video demo end-to-end trên một endpoint group để lấy điểm bonus | 6, 9 | `skill/hw05-api-performance/SKILL.md`, `demo.md`, `evidence/video-links.md` | Skill và mô tả demo có; **chưa kiểm độc lập video có thể hiện phần demo skill end-to-end**. |
| AI Audit có khai báo công cụ, thời gian, prompt, output; Markdown + PDF | 1–2, 6–8 | `ai_audit.md`, `ai_audit.pdf` | Có P00–P14 và QA bổ sung. **Khoảng trống:** các mục AI Output hiện là tóm tắt, không phải toàn văn; cần đối chiếu/xuất hội thoại gốc nếu còn. P14 đã đính chính khẳng định sai về ZIP/Moodle. |
| AI Critique 200–300 từ; Markdown + PDF | 7–8 | `ai-critique.md`, `ai-critique.pdf` | Có 284 từ phần thân theo khoảng trắng; PDF đọc được, 1 trang. Nội dung đã được AI hỗ trợ biên tập trong lượt QA, cần sinh viên đọc và xác nhận quan điểm của mình. |
| Git commit log text và README tự chấm + summary | 7–9 | `git-commits.txt`, `README.md` | Có; log cần cập nhật sau commit cuối; bảng tự chấm 30/20/20/10/10/10 = 100. |
| Nộp Moodle | 8 | Ngoài ZIP | **Chưa có bằng chứng đã nộp; sinh viên tự tải ZIP lên Moodle.** |

## 2. Cấu trúc dự kiến trong ZIP và lý do giữ từng nhóm

- Gốc: `README.md`, `report.md/pdf`, `ai-critique.md/pdf`, `ai_audit.md/pdf`, `git-commits.txt`, `SUBMISSION_CHECKLIST.md` — tài liệu theo mục 14 và biên bản tự kiểm.
- `plans/` — đúng **3 JMX chính thức**. JMX smoke bổ trợ ở `results/smoke/plans/` được loại khỏi ZIP để tránh hiểu nhầm có thêm test plan nộp chính.
- `data/` — **100 CSV** cho 100 VU theo yêu cầu data-driven.
- `results/load/`, `stress/`, `spike/` — raw JTL, JMeter log, resource CSV, manifest và toàn bộ HTML Dashboard/asset; không lược bỏ asset vì sẽ làm hỏng báo cáo HTML.
- `results/soak/`, `calibration/`, `smoke/` — chứng cứ bổ trợ cho soak, hiệu chỉnh tải, và xác nhận workflow; smoke chứa cả lượt lỗi Java/Groovy được giải thích trong `design/plan-review.md`.
- `evidence/` — ảnh thật, cấu hình máy, video URL, mô tả cách chạy và monitor.
- `analysis/`, `design/` — kết quả tính từ JTL, AI first pass, human review nháp, edge case và tài liệu thiết kế/CI.
- `skill/` — skill và demo bonus.
- `scripts/` — mã tạo/kiểm tra plan, tính metric, chạy probe, xuất PDF, đóng gói; cho phép tái lập kết quả.

**Loại khỏi ZIP:** `.git/`, `.gitignore`, `node_modules/`, `src/eshop-sut/`, công cụ JMeter đã tải, database SQLite cục bộ, file `.pyc`, `tmp_*.jtl`, ảnh render QA ngoài workspace, các JMX smoke trùng tên. Đề trang 8 cho phép "Any other supporting materials"; các file hỗ trợ nêu trên có liên hệ trực tiếp tới quá trình kiểm thử, không phải file rác.

## 3. Việc sinh viên cần hoàn thành trước khi nộp

1. **C07/C08:** Chạy lại probe trong môi trường SUT, chụp màn hình thật thể hiện request, status, body và thời điểm; đăng hai GitHub Issues vào repo công khai, đính kèm ảnh, dẫn link Issue trong README/report. Nếu không đăng được, phải ghi rõ lý do và không nói đã có Issue.
2. **Ảnh/JTL:** Nếu muốn chứng minh ảnh cùng lượt với raw log nộp, quay/chụp lại lần chạy lưu vào đường dẫn JTL chính thức hoặc giữ nguyên JTL tạm cùng manifest liên kết; không gán ảnh hiện tại cho một lượt chạy khác.
3. **Video:** Xem đủ 7:04 ở chế độ người xem, xác nhận có chính giọng tiếng Việt, JMeter + monitor cùng khung và demo Agent Skill end-to-end; sửa mô tả/link nếu thực tế khác.
4. **AI Audit & critique:** Đọc lại mọi dòng "Tôi đã tự kiểm" và quan điểm critique. Bổ sung câu trả lời AI nguyên văn từ lịch sử hội thoại nếu còn; không dựng lại. Ghi rõ những mục không thể phục hồi.
5. **Git log:** Sau commit cuối, cập nhật `git-commits.txt`; chạy lại đóng gói/kiểm ZIP nếu có thay đổi.
6. **Moodle:** Tải đúng ZIP tên `23120127_HW05_AI_Performance_100.zip`, mở lại bản đã tải để kiểm tra, rồi giữ ảnh/trạng thái xác nhận nộp. Không có bằng chứng Moodle trong lần QA này.

## 4. Giới hạn của kết luận QA

QA có thể chứng minh file hiện diện, định dạng đọc được, số liệu đối chiếu JTL và ZIP không hỏng. QA **không thể chứng minh** người nào thuyết minh video, sự trùng khớp ảnh với JTL khi tên file khác, lịch sử hostname của bài trước, hoặc có GitHub Issues khi GitHub trả danh sách rỗng. Vì vậy hiện **chưa thể kết luận bài nộp không thiếu chứng cứ theo toàn bộ đề**, dù ZIP vẫn được tạo đúng tên để người học hoàn thiện.
