import socket
import threading
import json

HOST, PORT = "0.0.0.0", 5000
clients = {}          # username -> connection
rooms = {}            # room_id -> {"players": {username: conn}, "status": str}
lock = threading.Lock()


def send(conn, data):
    try:
        conn.sendall((json.dumps(data, ensure_ascii=False) + "\n").encode())
        return True
    except OSError:
        return False


def broadcast(room_id, data, exclude=None):
    with lock:
        room = rooms.get(room_id)
        connections = list(room["players"].values()) if room else []

    for conn in connections:
        if conn != exclude:
            send(conn, data)


def player_room(username):
    with lock:
        for room_id, room in rooms.items():
            if username in room["players"]:
                return room_id
    return None


def room_list(conn):
    with lock:
        rooms_data = [
            {
                "room_id": room_id,
                "players": list(room["players"]),
                "player_count": len(room["players"]),
                "status": room["status"],
            }
            for room_id, room in rooms.items()
        ]
    send(conn, {"type": "room_list", "rooms": rooms_data})


def create_room(username, conn):
    with lock:
        room_id = 1
        while room_id in rooms:
            room_id += 1

        rooms[room_id] = {
            "players": {username: conn},
            "status": "waiting",
        }

    send(conn, {
        "type": "room_created",
        "room_id": room_id,
        "message": f"Đã tạo phòng {room_id}",
    })
    print(f"[ROOM] {username} tạo phòng {room_id}")


def join_room(username, conn, room_id):
    with lock:
        room = rooms.get(room_id)

        if not room:
            send(conn, {"type": "error", "message": "Phòng không tồn tại."})
            return

        if username in room["players"]:
            send(conn, {"type": "error", "message": "Bạn đã ở trong phòng."})
            return

        if len(room["players"]) >= 2:
            send(conn, {"type": "error", "message": "Phòng đã đủ người."})
            return

        room["players"][username] = conn
        room["status"] = "playing"

    send(conn, {
        "type": "joined_room",
        "room_id": room_id,
        "message": f"Bạn đã tham gia phòng {room_id}.",
    })

    broadcast(room_id, {
        "type": "player_joined",
        "player": username,
        "room_id": room_id,
    }, exclude=conn)

    print(f"[ROOM] {username} tham gia phòng {room_id}")


def leave_room(username, conn):
    room_id = player_room(username)
    if room_id is None:
        return

    with lock:
        room = rooms.get(room_id)
        if not room:
            return

        room["players"].pop(username, None)

        if room["players"]:
            room["status"] = "waiting"
        else:
            del rooms[room_id]

    broadcast(room_id, {"type": "player_left", "player": username}, exclude=conn)
    print(f"[ROOM] {username} rời phòng {room_id}")


def handle_move(username, conn, data):
    room_id = player_room(username)
    if room_id is None:
        send(conn, {"type": "error", "message": "Bạn chưa tham gia phòng."})
        return

    row, col, value = data.get("row"), data.get("col"), data.get("value")

    if not all(isinstance(x, int) for x in (row, col, value)):
        return
    if not (0 <= row <= 8 and 0 <= col <= 8 and 1 <= value <= 9):
        return

    broadcast(room_id, {
        "type": "move",
        "player": username,
        "row": row,
        "col": col,
        "value": value,
    })

    print(f"[MOVE] {username}: ({row}, {col}) = {value}")


def handle_message(username, conn, data):
    msg_type = data.get("type")

    if msg_type == "room_list":
        room_list(conn)

    elif msg_type == "create_room":
        if player_room(username) is not None:
            send(conn, {"type": "error", "message": "Bạn đang ở trong một phòng."})
        else:
            create_room(username, conn)

    elif msg_type == "join_room":
        room_id = data.get("room_id")
        if not isinstance(room_id, int):
            send(conn, {"type": "error", "message": "Room ID không hợp lệ."})
        elif player_room(username) is not None:
            send(conn, {"type": "error", "message": "Bạn đang ở trong một phòng."})
        else:
            join_room(username, conn, room_id)

    elif msg_type == "leave_room":
        leave_room(username, conn)

    elif msg_type == "move":
        handle_move(username, conn, data)

    elif msg_type == "chat":
        room_id = player_room(username)
        if room_id:
            broadcast(room_id, {
                "type": "chat",
                "player": username,
                "message": data.get("message", ""),
            })

    elif msg_type == "ping":
        send(conn, {"type": "pong"})

    else:
        send(conn, {"type": "error", "message": "Không nhận diện được loại message."})


def remove_client(username, conn):
    leave_room(username, conn)

    with lock:
        clients.pop(username, None)

    try:
        conn.close()
    except OSError:
        pass

    print(f"[DISCONNECT] {username}")


def handle_client(conn, address):
    username = None
    buffer = ""

    print(f"[CONNECT] {address}")
    send(conn, {"type": "welcome", "message": "Chào mừng đến Sudoku Server."})

    try:
        while True:
            data = conn.recv(4096)
            if not data:
                break

            buffer += data.decode("utf-8")

            while "\n" in buffer:
                line, buffer = buffer.split("\n", 1)
                if not line.strip():
                    continue

                try:
                    message = json.loads(line)
                except json.JSONDecodeError:
                    send(conn, {"type": "error", "message": "JSON không hợp lệ."})
                    continue

                if message.get("type") == "login":
                    username = message.get("username")

                    if not username:
                        send(conn, {
                            "type": "login_failed",
                            "message": "Username không được rỗng.",
                        })
                        username = None
                        continue

                    with lock:
                        if username in clients:
                            username = None
                            send(conn, {
                                "type": "login_failed",
                                "message": "Username đang được sử dụng.",
                            })
                            continue
                        clients[username] = conn

                    send(conn, {"type": "login_success", "username": username})
                    room_list(conn)
                    print(f"[LOGIN] {username}")
                    continue

                if username is None:
                    send(conn, {"type": "error", "message": "Bạn chưa đăng nhập."})
                    continue

                handle_message(username, conn, message)

    except (ConnectionResetError, OSError) as e:
        print(f"[ERROR] {address}: {e}")
    finally:
        if username:
            remove_client(username, conn)
        else:
            try:
                conn.close()
            except OSError:
                pass


def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, PORT))
    server.listen(20)

    print(f"=== SUDOKU SERVER | {HOST}:{PORT} ===")

    try:
        while True:
            conn, address = server.accept()
            threading.Thread(
                target=handle_client,
                args=(conn, address),
                daemon=True,
            ).start()
    except KeyboardInterrupt:
        print("\nServer đang tắt...")
    finally:
        server.close()


if __name__ == "__main__":
    start_server()