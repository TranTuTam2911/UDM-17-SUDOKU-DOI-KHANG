import socket
import threading
import json


# ============================================================
# CẤU HÌNH
# ============================================================

SERVER_IP = "127.0.0.1"
SERVER_PORT = 5000


# ============================================================
# BIẾN CLIENT
# ============================================================

client = None
running = True
username = None


# ============================================================
# GỬI JSON
# ============================================================

def send_json(data):

    try:

        message = json.dumps(
            data,
            ensure_ascii=False
        ) + "\n"

        client.sendall(
            message.encode("utf-8")
        )

    except Exception as e:

        print(
            "Không thể gửi dữ liệu:",
            e
        )


# ============================================================
# NHẬN DỮ LIỆU
# ============================================================

def receive_messages():

    global running

    buffer = ""

    while running:

        try:

            data = client.recv(4096)

            if not data:

                print(
                    "\nServer đã ngắt kết nối."
                )

                running = False
                break

            buffer += data.decode(
                "utf-8"
            )

            # Xử lý từng message
            while "\n" in buffer:

                line, buffer = buffer.split(
                    "\n",
                    1
                )

                if not line.strip():
                    continue

                try:

                    message = json.loads(
                        line
                    )

                    handle_server_message(
                        message
                    )

                except json.JSONDecodeError:

                    print(
                        "Nhận JSON không hợp lệ."
                    )

        except ConnectionResetError:

            print(
                "\nMất kết nối Server."
            )

            running = False
            break

        except Exception as e:

            if running:

                print(
                    "\nLỗi nhận dữ liệu:",
                    e
                )

            break


# ============================================================
# XỬ LÝ MESSAGE TỪ SERVER
# ============================================================

def handle_server_message(data):

    message_type = data.get(
        "type"
    )

    # --------------------------------------------------------
    # WELCOME
    # --------------------------------------------------------

    if message_type == "welcome":

        print(
            "\nSERVER:",
            data.get("message")
        )

    # --------------------------------------------------------
    # LOGIN
    # --------------------------------------------------------

    elif message_type == "login_success":

        print(
            "\nĐăng nhập thành công!"
        )

        print(
            "Username:",
            data.get("username")
        )

    elif message_type == "login_failed":

        print(
            "\nĐăng nhập thất bại:",
            data.get("message")
        )

    # --------------------------------------------------------
    # ROOM CREATED
    # --------------------------------------------------------

    elif message_type == "room_created":

        print(
            "\nĐã tạo phòng:",
            data.get("room_id")
        )

    # --------------------------------------------------------
    # JOIN ROOM
    # --------------------------------------------------------

    elif message_type == "joined_room":

        print(
            "\n",
            data.get("message")
        )

    # --------------------------------------------------------
    # PLAYER JOIN
    # --------------------------------------------------------

    elif message_type == "player_joined":

        print(
            "\n[ROOM]",
            data.get("player"),
            "đã tham gia phòng."
        )

    # --------------------------------------------------------
    # PLAYER LEFT
    # --------------------------------------------------------

    elif message_type == "player_left":

        print(
            "\n[ROOM]",
            data.get("player"),
            "đã rời phòng."
        )

    # --------------------------------------------------------
    # ROOM UPDATE
    # --------------------------------------------------------

    elif message_type == "room_update":

        room = data.get(
            "room"
        )

        print(
            "\n========== ROOM =========="
        )

        print(
            "Room ID:",
            room.get("room_id")
        )

        print(
            "Players:",
            room.get("players")
        )

        print(
            "Status:",
            room.get("status")
        )

        print(
            "=========================="
        )

    # --------------------------------------------------------
    # ROOM LIST
    # --------------------------------------------------------

    elif message_type == "room_list":

        rooms = data.get(
            "rooms",
            []
        )

        print(
            "\n========== ROOM LIST =========="
        )

        if not rooms:

            print(
                "Hiện chưa có phòng."
            )

        else:

            for room in rooms:

                print(
                    f"Room {room['room_id']} | "
                    f"Players: {room['players']} | "
                    f"Status: {room['status']}"
                )

        print(
            "==============================="
        )

    # --------------------------------------------------------
    # SUDOKU MOVE
    # --------------------------------------------------------

    elif message_type == "move":

        print(
            "\n[MOVE]",
            data.get("player"),
            "điền",
            data.get("value"),
            "vào",
            f"({data.get('row')},"
            f"{data.get('col')})"
        )

    # --------------------------------------------------------
    # CHAT
    # --------------------------------------------------------

    elif message_type == "chat":

        print(
            f"\n[CHAT] "
            f"{data.get('player')}: "
            f"{data.get('message')}"
        )

    # --------------------------------------------------------
    # PONG
    # --------------------------------------------------------

    elif message_type == "pong":

        print(
            "\nServer đang hoạt động."
        )

    # --------------------------------------------------------
    # ERROR
    # --------------------------------------------------------

    elif message_type == "error":

        print(
            "\n[ERROR]",
            data.get("message")
        )

    # --------------------------------------------------------
    # UNKNOWN
    # --------------------------------------------------------

    else:

        print(
            "\n[SERVER]",
            data
        )


# ============================================================
# LOGIN
# ============================================================

def login():

    global username

    while True:

        name = input(
            "\nNhập username: "
        ).strip()

        if not name:

            print(
                "Username không được rỗng."
            )

            continue

        send_json({
            "type": "login",
            "username": name
        })

        # Đợi người dùng kiểm tra
        # kết quả đăng nhập từ Server
        username = name

        break


# ============================================================
# HIỂN THỊ MENU
# ============================================================

def show_menu():

    print("\n")
    print("=" * 40)
    print("          SUDOKU CLIENT")
    print("=" * 40)

    print("1. Xem danh sách phòng")
    print("2. Tạo phòng")
    print("3. Tham gia phòng")
    print("4. Rời phòng")
    print("5. Gửi nước đi Sudoku")
    print("6. Chat")
    print("7. Ping Server")
    print("8. Thoát")

    print("=" * 40)


# ============================================================
# MENU
# ============================================================

def menu():

    global running

    while running:

        show_menu()

        choice = input(
            "Chọn chức năng: "
        ).strip()

        # ----------------------------------------------------
        # ROOM LIST
        # ----------------------------------------------------

        if choice == "1":

            send_json({
                "type": "room_list"
            })

        # ----------------------------------------------------
        # CREATE ROOM
        # ----------------------------------------------------

        elif choice == "2":

            send_json({
                "type": "create_room"
            })

        # ----------------------------------------------------
        # JOIN ROOM
        # ----------------------------------------------------

        elif choice == "3":

            try:

                room_id = int(
                    input(
                        "Nhập Room ID: "
                    )
                )

                send_json({
                    "type": "join_room",
                    "room_id": room_id
                })

            except ValueError:

                print(
                    "Room ID phải là số."
                )

        # ----------------------------------------------------
        # LEAVE ROOM
        # ----------------------------------------------------

        elif choice == "4":

            send_json({
                "type": "leave_room"
            })

        # ----------------------------------------------------
        # MOVE
        # ----------------------------------------------------

        elif choice == "5":

            try:

                row = int(
                    input(
                        "Row (0-8): "
                    )
                )

                col = int(
                    input(
                        "Column (0-8): "
                    )
                )

                value = int(
                    input(
                        "Value (1-9): "
                    )
                )

                send_json({
                    "type": "move",
                    "row": row,
                    "col": col,
                    "value": value
                })

            except ValueError:

                print(
                    "Dữ liệu không hợp lệ."
                )

        # ----------------------------------------------------
        # CHAT
        # ----------------------------------------------------

        elif choice == "6":

            message = input(
                "Tin nhắn: "
            )

            send_json({
                "type": "chat",
                "message": message
            })

        # ----------------------------------------------------
        # PING
        # ----------------------------------------------------

        elif choice == "7":

            send_json({
                "type": "ping"
            })

        # ----------------------------------------------------
        # EXIT
        # ----------------------------------------------------

        elif choice == "8":

            running = False

            try:

                send_json({
                    "type": "leave_room"
                })

            except Exception:
                pass

            try:

                client.close()

            except Exception:
                pass

            print(
                "Đã thoát Client."
            )

            break

        else:

            print(
                "Lựa chọn không hợp lệ."
            )


# ============================================================
# START CLIENT
# ============================================================

def start_client():

    global client

    client = socket.socket(
        socket.AF_INET,
        socket.SOCK_STREAM
    )

    try:

        client.connect(
            (
                SERVER_IP,
                SERVER_PORT
            )
        )

        print(
            f"Đã kết nối Server "
            f"{SERVER_IP}:{SERVER_PORT}"
        )

    except ConnectionRefusedError:

        print(
            "Không thể kết nối Server."
        )

        return

    except Exception as e:

        print(
            "Lỗi kết nối:",
            e
        )

        return

    # Thread nhận dữ liệu
    receiver = threading.Thread(
        target=receive_messages,
        daemon=True
    )

    receiver.start()

    # Đăng nhập
    login()

    # Menu
    menu()


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    start_client()