import socket
import threading
import json

HOST = "0.0.0.0"
PORT = 5000

# DỮ LIỆU SERVER

clients = {}
rooms = {}

clients_lock = threading.Lock()
rooms_lock = threading.Lock()

# HÀM GỬI JSON

def send_json(conn, data):
    """
    Gửi một message JSON qua TCP.
    Mỗi message kết thúc bằng ký tự newline.
    """
    try:
        message = json.dumps(data, ensure_ascii=False) + "\n"
        conn.sendall(message.encode("utf-8"))
        return True

    except (ConnectionResetError, BrokenPipeError, OSError):
        return False


# HÀM GỬI MESSAGE CHO NHIỀU CLIENT

def broadcast(room_id, data, exclude=None):
    """
    Gửi dữ liệu đến tất cả người chơi trong phòng.
    exclude: không gửi cho Client này.
    """

    with rooms_lock:
        room = rooms.get(room_id)

        if not room:
            return

        player_connections = list(room["players"].values())

    for conn in player_connections:
        if conn == exclude:
            continue

        if not send_json(conn, data):
            print("Không thể gửi dữ liệu đến Client.")


# LẤY THÔNG TIN PHÒNG

def get_room_info(room_id):
    with rooms_lock:
        room = rooms.get(room_id)

        if room is None:
            return None

        return {
            "room_id": room_id,
            "players": list(room["players"].keys()),
            "player_count": len(room["players"]),
            "status": room["status"]
        }


# GỬI DANH SÁCH PHÒNG

def send_room_list(conn):
    with rooms_lock:
        room_list = []

        for room_id, room in rooms.items():
            room_list.append({
                "room_id": room_id,
                "players": list(room["players"].keys()),
                "player_count": len(room["players"]),
                "status": room["status"]
            })

    send_json(conn, {
        "type": "room_list",
        "rooms": room_list
    })


# TẠO PHÒNG

def create_room(username, conn):
    with rooms_lock:

        # Tìm ID phòng chưa sử dụng
        room_id = 1

        while room_id in rooms:
            room_id += 1

        rooms[room_id] = {
            "players": {
                username: conn
            },

            "status": "waiting",

            # Dữ liệu Sudoku sau này có thể đặt ở đây
            "game_data": {
                "board": None,
                "start_time": None
            }
        }

    print(f"[ROOM] {username} tạo phòng {room_id}")

    send_json(conn, {
        "type": "room_created",
        "room_id": room_id,
        "message": f"Đã tạo phòng {room_id}"
    })

    return room_id


# THAM GIA PHÒNG

def join_room(username, conn, room_id):

    with rooms_lock:

        room = rooms.get(room_id)

        if room is None:
            send_json(conn, {
                "type": "error",
                "message": "Phòng không tồn tại."
            })
            return False

        if username in room["players"]:
            send_json(conn, {
                "type": "error",
                "message": "Bạn đã ở trong phòng."
            })
            return False

        # Giới hạn 2 người chơi
        if len(room["players"]) >= 2:
            send_json(conn, {
                "type": "error",
                "message": "Phòng đã đủ người."
            })
            return False

        room["players"][username] = conn

        room["status"] = "playing"

    print(f"[ROOM] {username} tham gia phòng {room_id}")

    send_json(conn, {
        "type": "joined_room",
        "room_id": room_id,
        "message": f"Bạn đã tham gia phòng {room_id}."
    })

    # Thông báo cho những người chơi khác
    broadcast(
        room_id,
        {
            "type": "player_joined",
            "player": username,
            "room_id": room_id
        },
        exclude=conn
    )

    # Gửi thông tin phòng
    info = get_room_info(room_id)

    broadcast(
        room_id,
        {
            "type": "room_update",
            "room": info
        }
    )

    return True


# RỜI PHÒNG

def leave_room(username, conn):

    room_id = None

    with rooms_lock:

        for rid, room in rooms.items():

            if username in room["players"]:
                room_id = rid

                del room["players"][username]

                # Nếu không còn người chơi
                if len(room["players"]) == 0:
                    del rooms[rid]

                else:
                    room["status"] = "waiting"

                break

    if room_id is not None:

        print(
            f"[ROOM] {username} rời phòng {room_id}"
        )

        broadcast(
            room_id,
            {
                "type": "player_left",
                "player": username
            }
        )

    return room_id


# TÌM PHÒNG CỦA PLAYER

def get_player_room(username):

    with rooms_lock:

        for room_id, room in rooms.items():

            if username in room["players"]:
                return room_id

    return None


# XỬ LÝ NƯỚC ĐI SUDOKU

def handle_move(username, conn, data):

    room_id = get_player_room(username)

    if room_id is None:

        send_json(conn, {
            "type": "error",
            "message": "Bạn chưa tham gia phòng."
        })

        return

    row = data.get("row")
    col = data.get("col")
    value = data.get("value")

    # Kiểm tra dữ liệu
    if not isinstance(row, int):
        return

    if not isinstance(col, int):
        return

    if not isinstance(value, int):
        return

    if not (0 <= row <= 8):
        return

    if not (0 <= col <= 8):
        return

    if not (1 <= value <= 9):
        return

    print(
        f"[MOVE] {username}: "
        f"row={row}, col={col}, value={value}"
    )

    # --------------------------------------------------------
    # Ở đây sau này có thể gọi Sudoku Engine
    # để kiểm tra đáp án đúng/sai.
    # --------------------------------------------------------

    broadcast(
        room_id,
        {
            "type": "move",
            "player": username,
            "row": row,
            "col": col,
            "value": value
        }
    )


# XỬ LÝ MESSAGE

def handle_message(username, conn, data):

    message_type = data.get("type")


    # GET ROOM LIST

    if message_type == "room_list":

        send_room_list(conn)

    # CREATE ROOM

    elif message_type == "create_room":

        # Không cho một người tạo nhiều phòng
        current_room = get_player_room(username)

        if current_room is not None:

            send_json(conn, {
                "type": "error",
                "message": "Bạn đang ở trong một phòng."
            })

            return

        create_room(username, conn)

    # JOIN ROOM

    elif message_type == "join_room":

        room_id = data.get("room_id")

        if not isinstance(room_id, int):

            send_json(conn, {
                "type": "error",
                "message": "Room ID không hợp lệ."
            })

            return

        current_room = get_player_room(username)

        if current_room is not None:

            send_json(conn, {
                "type": "error",
                "message": "Bạn đang ở trong một phòng."
            })

            return

        join_room(
            username,
            conn,
            room_id
        )

    # LEAVE ROOM

    elif message_type == "leave_room":

        leave_room(
            username,
            conn
        )

    # SUDOKU MOVE

    elif message_type == "move":

        handle_move(
            username,
            conn,
            data
        )

    # CHAT

    elif message_type == "chat":

        message = data.get("message", "")

        room_id = get_player_room(username)

        if room_id is not None:

            broadcast(
                room_id,
                {
                    "type": "chat",
                    "player": username,
                    "message": message
                }
            )

    # PING

    elif message_type == "ping":

        send_json(conn, {
            "type": "pong"
        })

    # UNKNOWN

    else:

        send_json(conn, {
            "type": "error",
            "message": "Không nhận diện được loại message."
        })


# XÓA CLIENT

def remove_client(username, conn):

    # Rời phòng trước
    leave_room(
        username,
        conn
    )

    with clients_lock:

        if username in clients:
            del clients[username]

    try:
        conn.close()
    except OSError:
        pass

    print(
        f"[DISCONNECT] {username} đã ngắt kết nối."
    )

# XỬ LÝ CLIENT

def handle_client(conn, address):

    username = None

    print(
        f"[CONNECT] Client: {address}"
    )

    buffer = ""

    try:

        # ĐĂNG NHẬP

        send_json(conn, {
            "type": "welcome",
            "message": "Chào mừng đến Sudoku Server."
        })

        while True:

            data = conn.recv(4096)

            if not data:
                break

            buffer += data.decode(
                "utf-8"
            )

            # TCP có thể nhận nhiều message cùng lúc
            while "\n" in buffer:

                line, buffer = buffer.split(
                    "\n",
                    1
                )

                if not line.strip():
                    continue

                try:

                    message = json.loads(line)

                except json.JSONDecodeError:

                    send_json(conn, {
                        "type": "error",
                        "message": "JSON không hợp lệ."
                    })

                    continue

                # LOGIN

                if message.get("type") == "login":

                    username = message.get(
                        "username"
                    )

                    if not username:
                        send_json(conn, {
                            "type": "login_failed",
                            "message": "Username không được rỗng."
                        })
                        continue

                    with clients_lock:

                        if username in clients:

                            send_json(conn, {
                                "type": "login_failed",
                                "message": "Username đang được sử dụng."
                            })

                            username = None
                            continue

                        clients[username] = conn

                    print(
                        f"[LOGIN] {username}"
                    )

                    send_json(conn, {
                        "type": "login_success",
                        "username": username
                    })

                    send_room_list(conn)

                    continue

                # PHẢI LOGIN TRƯỚC

                if username is None:

                    send_json(conn, {
                        "type": "error",
                        "message": "Bạn chưa đăng nhập."
                    })

                    continue

                # MESSAGE KHÁC

                handle_message(
                    username,
                    conn,
                    message
                )

    except ConnectionResetError:

        print(
            f"[ERROR] Client {address} reset connection."
        )

    except Exception as e:

        print(
            f"[ERROR] {address}: {e}"
        )

    finally:

        if username is not None:

            remove_client(
                username,
                conn
            )

        else:

            try:
                conn.close()
            except OSError:
                pass


# START SERVER

def start_server():

    server = socket.socket(
        socket.AF_INET,
        socket.SOCK_STREAM
    )

    # Cho phép tái sử dụng port
    server.setsockopt(
        socket.SOL_SOCKET,
        socket.SO_REUSEADDR,
        1
    )

    server.bind(
        (HOST, PORT)
    )

    server.listen(20)

    print("=" * 50)
    print("       SUDOKU TCP SERVER")
    print("=" * 50)

    print(
        f"Server đang chạy tại "
        f"{HOST}:{PORT}"
    )

    print(
        "Đang chờ Client..."
    )

    try:

        while True:

            conn, address = server.accept()

            thread = threading.Thread(
                target=handle_client,
                args=(conn, address),
                daemon=True
            )

            thread.start()

    except KeyboardInterrupt:

        print(
            "\nServer đang tắt..."
        )

    finally:

        server.close()

# MAIN

if __name__ == "__main__":

    start_server()