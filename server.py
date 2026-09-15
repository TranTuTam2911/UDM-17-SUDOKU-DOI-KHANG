import socket
import threading
import time

from backtrack import generate_puzzle_with_solution
from game_logic import SudokuMatch


class SudokuServer:
    def __init__(self, host="127.0.0.1", port=9000, time_limit=500):
        self.host = host
        self.port = port
        self.time_limit = time_limit
        self.lock = threading.Lock()
        self.connections = {}  # name -> socket
        self.match = None
        self.server_socket = None
        self.ready_event = threading.Event()

    def start(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)
        print(f"[SERVER] Chạy trên {self.host}:{self.port}")

        while True:
            conn, addr = self.server_socket.accept()
            threading.Thread(target=self._handle_client, args=(conn, addr), daemon=True).start()

    def _handle_client(self, conn, addr):
        name = None
        try:
            conn.sendall(b"ASK_NAME\n")
            name_data = conn.recv(2048).decode().strip()
            if not name_data:
                return

            if name_data.startswith("NAME|"):
                name = name_data.split("|", 1)[1].strip()
            else:
                name = name_data

            if not name:
                return

            with self.lock:
                self.connections[name] = conn
                print(f"[SERVER] Client {name} đã kết nối từ {addr}")

            conn.sendall(f"WELCOME|{name}\n".encode())

            if self.match is None and len(self.connections) >= 2:
                self._start_match()

            buffer = ""
            while True:
                data = conn.recv(2048)
                if not data:
                    break

                buffer += data.decode(errors="ignore")
                while "\n" in buffer:
                    line, buffer = buffer.split("\n", 1)
                    message = line.strip()
                    if message:
                        self._process_message(name, message)
        except socket.timeout:
            print(f"[SERVER] Hết thời gian chờ client {addr}")
        except Exception as exc:
            print(f"[SERVER] Lỗi client {addr}: {exc}")
        finally:
            try:
                conn.close()
            except Exception:
                pass
            with self.lock:
                if name is not None and name in self.connections:
                    del self.connections[name]

    def _start_match(self):
        names = list(self.connections.keys())[:2]
        if len(names) < 2:
            return

        puzzle, solution = generate_puzzle_with_solution(40)
        self.match = SudokuMatch(puzzle, names, time_limit=self.time_limit, solution=solution)

        board_payload = self.match.serialize_board()
        start_message = (
            f"MATCH_START|{names[0]}|{names[1]}|{self.time_limit}|"
            f"{self.match.scores[names[0]]}|{self.match.scores[names[1]]}|{board_payload}\n"
        )
        self._broadcast(start_message)

        print(f"[SERVER] Bắt đầu ván mới giữa {names[0]} và {names[1]}")
        self.ready_event.set()

        timer_thread = threading.Thread(target=self._timer_loop, daemon=True)
        timer_thread.start()

    def _timer_loop(self):
        while self.match is not None and not self.match.finished:
            time.sleep(1)
            winner = self.match.tick_time(1)
            if winner:
                score1 = self.match.scores[self.match.players[0]]
                score2 = self.match.scores[self.match.players[1]]
                self._broadcast(f"RESULT|{winner}|TIMEOUT|{score1}|{score2}\n")
                self.match.finished = True
                self.match.winner = winner
                self.match = None
                break

            current = self.match.current_player
            score1 = self.match.scores[self.match.players[0]]
            score2 = self.match.scores[self.match.players[1]]
            self._broadcast(
                f"TURN|{current}|{self.match.remaining_time[current]}|{score1}|{score2}|{self.match.serialize_board()}\n"
            )

    def _process_message(self, player_name, message):
        if self.match is None:
            return

        if message.startswith("MOVE|"):
            print(f"[SERVER] Nhận nước đi từ {player_name}: {message}")
            parts = message.split("|")
            if len(parts) != 4:
                self._send_to(player_name, "INVALID|Dữ liệu nước đi không hợp lệ\n")
                return

            try:
                row, col, value = int(parts[1]), int(parts[2]), int(parts[3])
            except ValueError:
                self._send_to(player_name, "INVALID|Nước đi phải là số\n")
                return

            if player_name != self.match.current_player:
                self._send_to(player_name, f"INVALID|Chưa đến lượt của {player_name}\n")
                return

            if not self.match.valid_move(row, col, value):
                penalty = 5
                current_score = self.match.scores.get(player_name, 0)
                self.match.scores[player_name] = max(0, current_score - penalty)
                print(
                    f"[SERVER] Nước đi sai từ {player_name} tại ({row}, {col}) = {value}. "
                    f"Bị trừ {penalty} điểm. Điểm hiện tại: {self.match.scores[player_name]}"
                )
                score1 = self.match.scores[self.match.players[0]]
                score2 = self.match.scores[self.match.players[1]]
                self._broadcast(
                    f"INVALID|{player_name}|{row}|{col}|{value}|{self.match.scores[player_name]}|"
                    f"{self.match.current_player}|{score1}|{score2}|{self.match.serialize_board()}\n"
                )
                return

            ok = self.match.apply_move(player_name, row, col, value)
            if not ok:
                self._send_to(player_name, "INVALID|Nước đi không hợp lệ\n")
                return

            print(
                f"[SERVER] Nước đi hợp lệ từ {player_name} tại ({row}, {col}) = {value}. "
                f"Điểm hiện tại: {self.match.scores[player_name]}"
            )

            if self.match.finished:
                score1 = self.match.scores[self.match.players[0]]
                score2 = self.match.scores[self.match.players[1]]
                self._broadcast(f"RESULT|{self.match.winner}|VICTORY|{score1}|{score2}\n")
                self.match = None
                return

            score1 = self.match.scores[self.match.players[0]]
            score2 = self.match.scores[self.match.players[1]]
            self._broadcast(
                f"STATE|{player_name}|{row}|{col}|{value}|{self.match.scores[player_name]}|"
                f"{self.match.current_player}|{score1}|{score2}|{self.match.serialize_board()}\n"
            )
            current = self.match.current_player
            self._broadcast(
                f"TURN|{current}|{self.match.remaining_time[current]}|{score1}|{score2}|{self.match.serialize_board()}\n"
            )

    def _broadcast(self, message):
        with self.lock:
            for conn in list(self.connections.values()):
                try:
                    conn.sendall(message.encode())
                except Exception as exc:
                    print(f"[SERVER] Gửi thất bại: {exc}")

    def _send_to(self, player_name, message):
        with self.lock:
            conn = self.connections.get(player_name)
            if conn is not None:
                try:
                    conn.sendall(message.encode())
                except Exception as exc:
                    print(f"[SERVER] Gửi thất bại tới {player_name}: {exc}")


if __name__ == "__main__":
    server = SudokuServer()
    server.start()
