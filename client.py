import socket
import threading
import time


class SudokuClient:
    def __init__(self, host="127.0.0.1", port=9000):
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((self.host, self.port))
        self.name = input("Tên người chơi: ").strip() or "Player"
        self.sock.sendall(f"NAME|{self.name}\n".encode())

        self.running = True
        self.receiver = threading.Thread(target=self._receive_loop, daemon=True)
        self.receiver.start()

    def _receive_loop(self):
        while self.running:
            try:
                data = self.sock.recv(4096)
                if not data:
                    break
                for message in data.decode(errors="ignore").splitlines():
                    if not message:
                        continue
                    self._handle_message(message)
            except socket.timeout:
                continue
            except OSError:
                break

    def _handle_message(self, message):
        print(f"[SERVER] {message}")
        parts = message.split("|")

        if parts[0] == "MATCH_START":
            print("Trận đấu bắt đầu. Lượt chơi của người đầu tiên sẽ được server quyết định.")
            print(f"Đối thủ: {parts[2]} | Thời gian tối đa: {parts[3]}s")
            self.print_board(parts[4])
        elif parts[0] == "TURN":
            current_player = parts[1]
            remaining_time = parts[2]
            board_data = parts[3]
            print(f"Lượt hiện tại: {current_player} | Thời gian còn lại: {remaining_time}s")
            self.print_board(board_data)
            if current_player == self.name:
                self.send_move()
            else:
                print("Đợi lượt đối thủ...")
        elif parts[0] == "STATE":
            player_name = parts[1]
            row = parts[2]
            col = parts[3]
            value = parts[4]
            score = parts[5]
            current_player = parts[6]
            board_data = parts[7]
            print(f"{player_name} đã đi vào ô ({row}, {col}) với giá trị {value} | Điểm: {score} | Lượt tiếp theo: {current_player}")
            self.print_board(board_data)
        elif parts[0] == "INVALID":
            print(f"Nước đi không hợp lệ: {parts[1]}")
        elif parts[0] == "RESULT":
            print(f"Kết quả: {parts[1]} thắng ({parts[2]})")
            self.running = False
            self.sock.close()
        elif parts[0] == "WELCOME":
            print(f"Kết nối thành công với server. Bạn là: {parts[1]}")

    def print_board(self, board_data):
        try:
            rows = board_data.split("|")
            print("\nBảng Sudoku hiện tại:")
            for idx, row in enumerate(rows):
                values = [int(v) for v in row.split(",")]
                print(" ".join(str(v) if v != 0 else "." for v in values))
                if (idx + 1) % 3 == 0 and idx != 8:
                    print("-" * 20)
        except Exception:
            print("Board chưa sẵn sàng")

    def send_move(self):
        while self.running:
            try:
                raw = input("Nhập nước đi theo định dạng: row col value (vd: 0 1 5): ").strip()
                if not raw:
                    continue
                row, col, value = map(int, raw.split())
                self.sock.sendall(f"MOVE|{row}|{col}|{value}\n".encode())
                break
            except ValueError:
                print("Dữ liệu không hợp lệ. Ví dụ: 0 1 5")

    def run(self):
        try:
            while self.running:
                time.sleep(0.2)
        finally:
            self.sock.close()


if __name__ == "__main__":
    client = SudokuClient()
    client.run()
