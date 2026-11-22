# Nhận xét Phản biện AI (AI Critique — Phụ lục Bắt buộc)

**MSSV:** 23120127  
**Môn học:** Kiểm thử Phần mềm / Software Testing (HW05 AI)  
**Hệ thống kiểm thử (SUT):** EShop REST Backend API  
**Số từ:** 250 từ (Tiếng Việt) / 239 words (Tiếng Anh)

---

### Bản Tiếng Việt (Vietnamese Version — 250 từ)

Trong bài tập kiểm thử hiệu năng này, công cụ AI đã hỗ trợ kỹ thuật rất tốt trong việc tạo sinh nhanh các kịch bản JMeter ban đầu và trích xuất dữ liệu đo. Tuy nhiên, các lỗi sai nghiêm trọng đã bộc lộ trong giai đoạn phân tích kết quả. Nổi bật nhất là việc AI mắc phải ngụy biện gộp mẫu (aggregation bias): nó báo cáo độ trễ p95 của kịch bản Stress rất mượt mà ở mức 18 mili-giây, che giấu hoàn toàn sự thật là ở tầng tải cao nhất 80 VU, p95 toàn cục đã vọt lên 23 mili-giây và thao tác xóa danh mục lên tới 32 mili-giây (p99 đạt 152 mili-giây). Hơn thế nữa, AI đã phạm phải ảo tưởng kiến trúc (architectural hallucination) khi đề xuất cấu hình connection pool và đánh index cho SQLite—hoàn toàn phớt lờ thực tế SQLite là CSDL tệp nhúng đơn tiến trình và khóa chính ID vốn đã có sẵn chỉ mục B-Tree. Nó cũng hiểu sai việc Windows thu hồi working set bộ nhớ lúc 17:31:10 thành việc Node.js dọn rác đạt trần bộ nhớ 32,4 MiB.

AI thất bại trong việc phát hiện các lỗi này vì mô hình ngôn ngữ lớn thiếu khả năng tự đối chiếu với ground-truth thực tế; chúng tạo văn bản theo xác suất và luôn có xu hướng lấy trung bình tổng thể thay vì phân tích từng pha cụ thể. Đồng thời, AI chỉ nhìn mã trạng thái HTTP 200 để kết luận thành công, bỏ qua việc kiểm tra các bản ghi danh mục rác tồn dư trong CSDL hay việc API trả 200 cho ID không tồn tại.

Nguyên tắc cốt lõi em rút ra được là AI không bao giờ được xem là nguồn chân lý tuyệt đối trong kiểm thử hiệu năng. Kỹ sư phải luôn kiểm chứng chéo từng khẳng định của AI với log thực thi thô và mã nguồn hệ thống.

---

### Bản Tiếng Anh Đối chiếu (English Reference Version — 239 words)

During this performance testing assignment, the AI demonstrated significant technical assistance in generating initial JMeter test plans and parsing execution metrics. However, critical flaws emerged during the analysis phase. Most notably, the AI exhibited severe aggregation bias: it reported a smooth overall 95th-percentile latency of 18 ms for the Stress scenario, completely obscuring that latency in the final 80-VU tier spiked to 23 ms overall and 32 ms for DELETE operations. Furthermore, the AI committed architectural hallucinations by proposing a connection pool and index optimizations for SQLite—disregarding that SQLite is a file-based embedded engine whose primary key already indexes category records. It also misinterpreted an operating system working-set memory trim at 17:31:10 as V8 garbage collection achieving a supposed 32.4 MiB memory ceiling.

The AI failed to catch these issues because large language models lack autonomous ground-truth grounding; they generate probabilistic textual patterns and naturally favor global averages over phase-specific percentiles unless explicitly constrained. Moreover, the AI evaluated test success purely through HTTP 200 status codes, failing to detect residual database records caused by thread interruptions or recognize that the SUT returns HTTP 200 on non-existent IDs.

The fundamental principle I learned is that AI must never serve as an authoritative oracle in performance testing. While AI excels at rapid boilerplate authoring, human engineers must rigorously cross-examine every analytical assertion against raw execution logs and source code architecture. Verification must rely on ground-truth telemetry rather than persuasive AI prose.
