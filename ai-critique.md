# Nhận xét Phản biện AI (AI Critique — Phụ lục Bắt buộc)

**MSSV:** 23120127  
**Môn học:** Kiểm thử Phần mềm / Software Testing (HW05 AI)  
**Hệ thống kiểm thử (SUT):** EShop REST Backend API  
**Số từ:** 284 từ (Quy định: 200–300 từ; đếm theo khoảng trắng phần thân)

---

Trong bài tập kiểm thử hiệu năng này, công cụ AI đã hỗ trợ tạo kịch bản JMeter và trích xuất dữ liệu. Tuy nhiên, phần phân tích có những nhận định sai. AI báo cáo p95 Stress gộp là 18 mili-giây rồi suy ra mức 80 VU vẫn ổn định; riêng tầng 80 VU có p95 toàn cục 23 mili-giây, DELETE p95 32 mili-giây và p99 152 mili-giây. AI cũng đề xuất thêm index cho khóa chính `categories.id` dù SQLite đã đánh chỉ mục cho cột này. Đề xuất pool 10–20 connection SQLite thiếu căn cứ từ mã nguồn hiện tại và cần đo thử trước khi áp dụng. Cuối cùng, AI suy đoán RSS giảm xuống 32,4 MiB là do Node.js dọn rác và coi đó là trần bộ nhớ. Private Bytes thực tế quanh 95–96 MiB; dữ liệu không chứng minh nguyên nhân giảm RSS hay trần bộ nhớ.

Sai sót xảy ra vì AI tổng hợp số liệu toàn bài mà chưa tách từng tầng tải, và đưa ra giải thích kiến trúc khi chưa kiểm tra mã nguồn hoặc phép đo bổ sung. AI còn dựa vào HTTP 200 để kết luận nghiệp vụ thành công, trong khi dữ liệu sau test còn bản ghi danh mục chưa được xóa. PUT/DELETE ID không tồn tại cũng trả 200; đây là hành vi cần đối chiếu đặc tả trước khi gọi là bug.

Nguyên tắc cốt lõi tôi rút ra là AI không bao giờ được xem là nguồn chân lý tuyệt đối trong kiểm thử hiệu năng. Kỹ sư phải luôn kiểm chứng chéo từng khẳng định của AI với log thực thi thô và mã nguồn hệ thống.
