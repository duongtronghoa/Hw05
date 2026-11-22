# Cấu hình máy chạy HW05

Trích từ Windows CIM lúc 2026-11-22 17:00:02 +07:00; dữ liệu gốc ở `hardware-spec.json`.

| Thành phần | Giá trị |
|---|---|
| Hostname | `TRONGHOA` |
| CPU | Intel Core i7-12700H, 14 core, 20 logical processors |
| RAM | 16.781.979.648 bytes (~15,63 GiB) |
| OS | Windows 11 Home Single Language, 64-bit, build 10.0.26300 |
| GPU | Intel Iris Xe; NVIDIA GeForce RTX 3050 Laptop GPU; MuMuPlayer Virtual Display Adapter |
| Backend | Node.js 25.9.0, SQLite, local port 3000, PID 3420 tại các run kỹ thuật |
| Load generator | Apache JMeter 5.6.3 trên Java 25.0.2 LTS, cùng máy với backend |

**Còn thiếu:** ảnh dxdiag/System thật và ảnh Task Manager + công cụ trong lúc từng scenario chạy. Người học cần đối chiếu `TRONGHOA` với hostname các bài triển khai trước. Phép đo JMeter và backend cùng máy chịu ảnh hưởng từ tải của chính load generator, ứng dụng nền và nhiệt/nguồn laptop; không coi RPS đo được là năng lực máy chủ riêng.
