import socket
import threading
import json
import os

HOST = "127.0.0.1"
PORT = 5000

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
running = True
messages = []
room = None
username = ""

def clear():
    os.system("cls" if os.name == "nt" else "clear")

def show():
    clear()
    print("=" * 55)
    print("                 SUDOKU CLIENT")
    print("=" * 55)
    print(f"User: {username or '-'}    Room: {room or '-'}")
    print("\n[ MENU ]")
    print("1. Xem phòng")
    print("2. Tạo phòng")
    print("3. Tham gia phòng")
    print("4. Rời phòng")
    print("5. Gửi nước đi")
    print("6. Chat")
    print("7. Ping Server")
    print("8. Thoát")
    print("\n[ SERVER ]")
    print("-" * 55)
    for msg in messages[-8:]:
        print(msg)
    print("-" * 55)

def send(data):
    sock.sendall((json.dumps(data, ensure_ascii=False) + "\n").encode())

def handle(data):
    global username, room

    t = data.get("type")

    if t == "login_success":
        username = data.get("username", username)
        messages.append(f"[LOGIN] Đăng nhập thành công: {username}")

    elif t == "room_created":
        room = data.get("room_id")
        messages.append(f"[ROOM] Đã tạo phòng: {room}")

    elif t == "joined_room":
        room = data.get("room_id", room)
        messages.append(f"[ROOM] {data.get('message', 'Đã tham gia phòng.')}")

    elif t == "left_room":
        room = None
        messages.append("[ROOM] Đã rời phòng.")

    elif t == "room_list":
        rooms = data.get("rooms", [])
        if not rooms:
            messages.append("[ROOM] Hiện chưa có phòng.")
        else:
            messages.append("[ROOM] Danh sách phòng:")
            for r in rooms:
                messages.append(
                    f"  Room {r.get('room_id')} | "
                    f"{r.get('players', [])} | {r.get('status', '')}"
                )

    elif t == "player_joined":
        messages.append(f"[ROOM] {data.get('player')} đã tham gia.")

    elif t == "player_left":
        messages.append(f"[ROOM] {data.get('player')} đã rời phòng.")

    elif t == "move":
        messages.append(
            f"[MOVE] {data.get('player')} -> "
            f"({data.get('row')},{data.get('col')}) = {data.get('value')}"
        )

    elif t == "chat":
        messages.append(
            f"[CHAT] {data.get('player')}: {data.get('message')}"
        )

    elif t == "pong":
        messages.append("[PING] Server đang hoạt động.")

    else:
        messages.append(f"[SERVER] {data.get('message', data)}")

def receive():
    global running
    buffer = ""

    while running:
        try:
            data = sock.recv(4096)
            if not data:
                break

            buffer += data.decode()

            while "\n" in buffer:
                line, buffer = buffer.split("\n", 1)
                if line.strip():
                    handle(json.loads(line))
                    show()
        except Exception:
            break

def ask(text):
    show()
    return input(f"\n> {text}").strip()

def main():
    global running

    try:
        sock.connect((HOST, PORT))
    except Exception as e:
        print(f"Không thể kết nối Server: {e}")
        return

    threading.Thread(target=receive, daemon=True).start()

    # Đăng nhập
    global username
    username = ask("Username: ")
    send({"type": "login", "username": username})

    while running:
        choice = ask("Chọn [1-8]: ")

        if choice == "1":
            send({"type": "room_list"})

        elif choice == "2":
            send({"type": "create_room"})

        elif choice == "3":
            try:
                room_id = int(ask("Room ID: "))
                send({"type": "join_room", "room_id": room_id})
            except ValueError:
                messages.append("[ERROR] Room ID phải là số.")

        elif choice == "4":
            send({"type": "leave_room"})

        elif choice == "5":
            try:
                row = int(ask("Row (0-8): "))
                col = int(ask("Column (0-8): "))
                value = int(ask("Value (1-9): "))

                send({
                    "type": "move",
                    "row": row,
                    "col": col,
                    "value": value
                })
            except ValueError:
                messages.append("[ERROR] Dữ liệu không hợp lệ.")

        elif choice == "6":
            text = ask("Tin nhắn: ")
            send({"type": "chat", "message": text})

        elif choice == "7":
            send({"type": "ping"})

        elif choice == "8":
            running = False
            try:
                send({"type": "leave_room"})
            except:
                pass
            sock.close()
            print("Đã thoát Client.")
            break

        else:
            messages.append("[ERROR] Chọn từ 1 đến 8.")

if __name__ == "__main__":
    main()