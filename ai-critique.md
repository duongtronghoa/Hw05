# Nhận xét Phản biện AI (AI Critique — Phụ lục Bắt buộc)

**MSSV:** 23120127  
**Môn học:** Kiểm thử Phần mềm / Software Testing (HW05 AI)  
**Hệ thống kiểm thử (SUT):** EShop REST Backend API  
**Số từ:** 286 từ (Quy định: 200–300 từ)

---

Trong bài tập kiểm thử hiệu năng này, công cụ AI đã hỗ trợ tốt việc tạo sinh các kịch bản JMeter ban đầu và trích xuất dữ liệu. Tuy nhiên, các lỗi sai nghiêm trọng đã bộc lộ trong giai đoạn phân tích kết quả. Nổi bật nhất là việc AI mắc ngụy biện gộp mẫu: nó báo cáo độ trễ p95 kịch bản Stress là 18 mili-giây, che giấu sự thật ở tầng 80 VU p95 toàn cục đã vọt lên 23 mili-giây và thao tác xóa danh mục lên tới 32 mili-giây (p99 đạt 152 mili-giây). Ngoài ra, AI phạm phải ảo tưởng kiến trúc khi đề xuất connection pool và index cho SQLite—phớt lờ thực tế SQLite là CSDL tệp nhúng đơn tiến trình và khóa chính ID vốn đã có sẵn chỉ mục. Nó cũng hiểu sai việc Windows thu hồi working set lúc 17:31:10 thành việc Node.js dọn rác đạt trần bộ nhớ 32,4 MiB.

AI thất bại vì mô hình ngôn ngữ lớn thiếu khả năng tự đối chiếu ground-truth thực tế; chúng tạo văn bản theo xác suất và thiên vị số trung bình thay vì phân tích từng pha độc lập. Đồng thời, AI chỉ dựa vào mã HTTP 200 để kết luận thành công, bỏ qua việc kiểm tra các bản ghi danh mục rác tồn dư trong CSDL hay việc API trả 200 cho ID không tồn tại.

Nguyên tắc cốt lõi tôi rút ra là AI không bao giờ được xem là nguồn chân lý tuyệt đối trong kiểm thử hiệu năng. Kỹ sư phải luôn kiểm chứng chéo từng khẳng định của AI với log thực thi thô và mã nguồn hệ thống.
