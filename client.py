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

    @staticmethod
    def parse_server_message(message):
        message = message.strip()
        if not message:
            return {"type": "", "payload": ""}

        parts = message.split("|")
        message_type = parts[0]

        if message_type == "MATCH_START":
            return {
                "type": message_type,
                "first_player": parts[1],
                "opponent": parts[2],
                "time_limit": parts[3],
                "board": "|".join(parts[4:]),
            }

        if message_type == "TURN":
            return {
                "type": message_type,
                "current_player": parts[1],
                "remaining_time": parts[2],
                "board": "|".join(parts[3:]),
            }

        if message_type == "STATE":
            return {
                "type": message_type,
                "player_name": parts[1],
                "row": parts[2],
                "col": parts[3],
                "value": parts[4],
                "score": parts[5],
                "current_player": parts[6],
                "board": "|".join(parts[7:]),
            }

        if message_type == "RESULT":
            return {
                "type": message_type,
                "winner": parts[1] if len(parts) > 1 else "",
                "reason": parts[2] if len(parts) > 2 else "",
            }

        if message_type in {"INVALID", "WELCOME"}:
            return {
                "type": message_type,
                "payload": "|".join(parts[1:]),
            }

        return {"type": message_type, "raw": message}

    def _handle_message(self, message):
        print(f"[SERVER] {message}")
        parsed = self.parse_server_message(message)
        message_type = parsed.get("type")

        if message_type == "MATCH_START":
            print("Trận đấu bắt đầu. Lượt chơi của người đầu tiên sẽ được server quyết định.")
            print(f"Đối thủ: {parsed['opponent']} | Thời gian tối đa: {parsed['time_limit']}s")
            self.print_board(parsed["board"])
        elif message_type == "TURN":
            current_player = parsed["current_player"]
            remaining_time = parsed["remaining_time"]
            board_data = parsed["board"]
            print(f"Lượt hiện tại: {current_player} | Thời gian còn lại: {remaining_time}s")
            self.print_board(board_data)
            if current_player == self.name:
                self.send_move()
            else:
                print("Đợi lượt đối thủ...")
        elif message_type == "STATE":
            player_name = parsed["player_name"]
            row = parsed["row"]
            col = parsed["col"]
            value = parsed["value"]
            score = parsed["score"]
            current_player = parsed["current_player"]
            board_data = parsed["board"]
            print(f"{player_name} đã đi vào ô ({row}, {col}) với giá trị {value} | Điểm: {score} | Lượt tiếp theo: {current_player}")
            self.print_board(board_data)
        elif message_type == "INVALID":
            print(f"Nước đi không hợp lệ: {parsed['payload']}")
        elif message_type == "RESULT":
            print(f"Kết quả: {parsed['winner']} thắng ({parsed['reason']})")
            self.running = False
            self.sock.close()
        elif message_type == "WELCOME":
            print(f"Kết nối thành công với server. Bạn là: {parsed['payload']}")

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
