# [ UDM_17 ] - [ Game Sudoku đối kháng ]

## Thành viên

| STT | MSSV | Họ và tên | Vai trò |
|---:|---|---|---|
| 1 | 051206002296 | Nguyễn Trương Quang Nam | Trưởng nhóm |
| 2 | 079306042880 | Trần Tú Tâm | Thành viên |
| 3 | 077206000799 | Lê Chí Công | Thành viên |
| 4 | 080206005689 | Nguyễn Hoài Vũ | Thành viên |
| 5 | 080305014159 | Trần Thị Phương Uyên | Thành viên |
| 6 | 089305003420 | Trần Thị Hồng Thắm | Thành viên |

## Giới thiệu

Đề tài **Game Sudoku Đối Kháng** là trò chơi giải đố trí tuệ trực tuyến được phát triển trên nền tảng Python, cho phép nhiều người chơi tham gia thi đấu đối kháng trong thời gian thực. 

- **Mục tiêu:** Xây dựng hệ thống game đối kháng trực tuyến hoàn chỉnh với cơ chế đồng bộ mạng Client–Server tin cậy, thuật toán sinh đề & giải Sudoku tự động bằng Backtracking và giao diện người dùng hiện đại, trực quan.
- **Đối tượng sử dụng:** Người yêu thích các trò chơi giải đố logic, học sinh, sinh viên và người dùng giải trí.
- **Phạm vi đề tài:** Hỗ trợ xác thực người chơi, sảnh chờ (Lobby), tạo và tham gia phòng theo độ khó (Dễ, Vừa, Khó), tính điểm đối kháng theo nước đi và thời gian thực.

## Kiến trúc hệ thống

- **Mô hình:** Client–Server (sử dụng đa luồng `threading` để xử lý đồng thời nhiều kết nối người chơi).
- **Protocol:** TCP Socket – đảm bảo tính toàn vẹn và đúng thứ tự của các gói tin trong suốt trận đấu.
- **Port mặc định:** `5000` (Host: `127.0.0.1` / `0.0.0.0`).
- **Cấu trúc message:** Chuỗi định dạng JSON kết thúc bằng ký tự ngắt dòng `\n`.
  - Cấu trúc chung:
    ```json
    {
      "type": "MOVE",
      "playerId": "Nam",
      "roomId": 101,
      "row": 0,
      "column": 2,
      "value": 5,
      "score": 10,
      "time": 580,
      "status": "playing"
    }
    ```
  - Các loại Message chính:
    - `LOGIN`: Gửi thông tin đăng nhập và xác thực.
    - `CREATE_ROOM`: Tạo phòng chơi mới với mức độ khó tùy chọn.
    - `JOIN_ROOM`: Tham gia vào phòng đang chờ.
    - `START_GAME`: Khởi tạo trận đấu và gửi đề Sudoku.
    - `MOVE`: Gửi tọa độ và giá trị ô cờ mà người chơi vừa điền.
    - `UPDATE`: Đồng bộ trạng thái trận đấu giữa các đối thủ.
    - `SCORE`: Cập nhật điểm số khi giải đúng/sai.
    - `FINISH` / `RESULT`: Thông báo hoàn thành và tổng kết kết quả trận đấu.

## Yêu cầu môi trường

- **Hệ điều hành:** Windows 10/11, macOS, hoặc Linux.
- **Ngôn ngữ và phiên bản:** Python 3.8+ (khuyến nghị Python 3.10 trở lên).
- **Công cụ / Dependency:** Sử dụng hoàn toàn thư viện chuẩn tích hợp sẵn trong Python (`tkinter`, `socket`, `threading`, `json`, `random`, `time`). Không yêu cầu cài đặt thêm thư viện bên ngoài (Zero external dependencies).

## Cài đặt

1. **Clone repository:**
   ```bash
   git clone https://github.com/TranTuTam2911/UDM-17-SUDOKU-DOI-KHANG.git
   cd UDM-17-SUDOKU-DOI-KHANG
   ```

2. **Kiểm tra môi trường Python:**
   ```bash
   python --version
   ```

## Hướng dẫn chạy

### Server

Khởi động máy chủ Socket để quản lý kết nối và các phòng chơi:

```bash
python Code/server.py
```

### Client

Mở cửa sổ giao diện người chơi (có thể chạy nhiều cửa sổ Client cùng lúc để thử nghiệm đối kháng):

```bash
python Code/main.py
```

## Cấu hình

- **Cấu hình Server:** Mở file `Code/server.py`, thay đổi biến `HOST` và `PORT` (mặc định: `HOST = "0.0.0.0"`, `PORT = 5000`).
- **Cấu hình Client:** Mở file `Code/client.py`, chỉnh sửa `HOST` trỏ đến địa chỉ IP của máy chủ (mặc định: `127.0.0.1`) và `PORT = 5000`.

> **Lưu ý:** Không lưu password hoặc khóa bảo mật nhạy cảm vào mã nguồn repository.

## Chức năng

- [x] **Xác thực người chơi:** Đăng nhập, kiểm tra hợp lệ, hiển thị/ẩn mật khẩu linh hoạt.
- [x] **Sảnh chờ (Lobby):** Xem danh sách phòng đang mở, số lượng người chơi trong phòng.
- [x] **Quản lý phòng:** Tạo phòng với 3 cấp độ (Tân binh, Cao thủ, Chuyên gia), tham gia phòng của đối thủ.
- [x] **Thuật toán Sudoku:** 
  - Sinh bảng Sudoku hợp lệ ngẫu nhiên và loại bỏ ô theo độ khó.
  - Tự động giải và kiểm tra tính hợp lệ bằng giải thuật **Backtracking**.
- [x] **Chế độ đối kháng thời gian thực:**
  - Đồng bộ bảng Sudoku và nước đi qua TCP Socket.
  - Cơ chế tính điểm: Cộng điểm khi điền đúng (`+10`), trừ điểm khi điền sai (`-5`), cộng điểm thưởng thời gian khi hoàn thành.
  - Đếm ngược thời gian thi đấu và tự động kết thúc khi hết giờ.
- [x] **Nộp bài & Phân định thắng thua:** Kiểm tra điều kiện hoàn thành bảng và thông báo kết quả.

## Kiểm thử

- **Functional test:** Đã kiểm thử đầy đủ các luồng đăng nhập, tạo phòng, ghép cặp, nhập số trên bảng Sudoku, tính điểm và kết thúc trận (Chi tiết tại `TEST CASE/Test Case.xlsx`).
- **Test dữ liệu không hợp lệ:** Kiểm tra bắt lỗi khi bỏ trống username/mật khẩu, nhập ký tự ngoài khoảng 1–9, hoặc điền vào ô mặc định của đề bài.
- **Test mất kết nối:** Xử lý ngoại lệ ngắt kết nối mạng bất ngờ để đảm bảo Server không bị crash và giải phóng tài nguyên phòng.
- **Stress test & Performance test:** Đảm bảo giải thuật Backtracking tạo bảng nhanh chóng (< 0.1s) và Server xử lý đa luồng mượt mà.

Bằng chứng kiểm thử được lưu chi tiết tại thư mục `Extra/` và `TEST CASE/`.

## Demo

- **Video:** [Public hoặc Unlisted URL]
- **Báo cáo:** Thư mục `DOCX/BaoCao.docx`

## Giới hạn

- Dữ liệu phòng chơi hiện được lưu trữ trực tiếp trên bộ nhớ RAM của Server trong suốt phiên chạy (chưa tích hợp Database vĩnh viễn như MySQL/PostgreSQL).
- Giao diện người dùng sử dụng Tkinter được thiết kế với kích thước cố định `1000x700`, chưa hỗ trợ responsive đa kích thước màn hình.
