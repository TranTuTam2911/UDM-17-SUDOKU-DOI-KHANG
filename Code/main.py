import tkinter as tk
from tkinter import messagebox
import random
from backtrack import generate_sudoku, backtracking
from sudoku_logic import SudokuBoard, SudokuTimer, SudokuScoring
BG = "#0F172A"
CARD = "#1E293B"
CARD2 = "#273449"
PRIMARY = "#06B6D4"
PRIMARY_HOVER = "#0891B2"
TEXT = "#F8FAFC"
SUB_TEXT = "#94A3B8"
GREEN = "#22C55E"
RED = "#EF4444"
YELLOW = "#F59E0B"
rooms = [
    {
        "id": 101,
        "name": "Phòng Tân Binh",
        "level": "Tân binh",
        "player": "Nam"
    },
    {
        "id": 102,
        "name": "Phòng Cao Thủ",
        "level": "Cao thủ",
        "player": "Minh"
    },
    {
        "id": 103,
        "name": "Phòng Chuyên Gia",
        "level": "Chuyên gia",
        "player": "An"
    }
]
class SudokuApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Sudoku Đối Kháng")
        self.root.geometry("1000x700")
        self.root.configure(bg=BG)
        self.root.resizable(False, False)
        self.username = ""
        self.current_room = None
        self.current_level = "Tân binh"
        self.board = None
        self.solution = None
        self.timer = None
        self.scoring = None
        self.entries = []
        self.show_login()
    def clear_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()
    def button(
        self,
        parent,
        text,
        command,
        width=20,
        bg=PRIMARY
    ):
        return tk.Button(
            parent,
            text=text,
            command=command,
            width=width,
            height=2,
            bg=bg,
            fg=TEXT,
            activebackground=PRIMARY_HOVER,
            activeforeground=TEXT,
            font=("Arial", 11, "bold"),
            relief="flat",
            cursor="hand2"
        )
    def show_login(self):
        self.clear_screen()
        card = tk.Frame(
            self.root,
            bg=CARD,
            width=450,
            height=500
        )
        card.place(
            relx=0.5,
            rely=0.5,
            anchor="center"
        )
        card.pack_propagate(False)
        tk.Label(
            card,
            text="SUDOKU",
            bg=CARD,
            fg=PRIMARY,
            font=("Arial", 32, "bold")
        ).pack(pady=(55, 5))
        tk.Label(
            card,
            text="ĐỐI KHÁNG",
            bg=CARD,
            fg=TEXT,
            font=("Arial", 22, "bold")
        ).pack()
        tk.Label(
            card,
            text="Đăng nhập để bắt đầu",
            bg=CARD,
            fg=SUB_TEXT,
            font=("Arial", 12)
        ).pack(pady=(10, 35))
        tk.Label(
            card,
            text="Tên người chơi",
            bg=CARD,
            fg=TEXT,
            font=("Arial", 11, "bold")
        ).pack(anchor="w", padx=55)
        self.username_entry = tk.Entry(
            card,
            bg=CARD2,
            fg=TEXT,
            insertbackground=TEXT,
            font=("Arial", 13),
            relief="flat"
        )
        self.username_entry.pack(
            padx=55,
            fill="x",
            ipady=12,
            pady=10
        )
        self.button(
            card,
            "ĐĂNG NHẬP",
            self.login,
            25
        ).pack(pady=25)
    def login(self):
        name = self.username_entry.get().strip()
        if not name:
            messagebox.showwarning(
                "Thông báo",
                "Vui lòng nhập tên!"
            )
            return
        self.username = name
        self.show_lobby()
    def show_lobby(self):

        self.clear_screen()
        header = tk.Frame(
            self.root,
            bg=CARD,
            height=75
        )
        header.pack(fill="x")
        tk.Label(
            header,
            text="SUDOKU ĐỐI KHÁNG",
            bg=CARD,
            fg=PRIMARY,
            font=("Arial", 21, "bold")
        ).pack(
            side="left",
            padx=30,
            pady=20
        )
        tk.Label(
            header,
            text=f"👤 {self.username}",
            bg=CARD,
            fg=TEXT,
            font=("Arial", 12)
        ).pack(
            side="right",
            padx=30
        )
        content = tk.Frame(
            self.root,
            bg=BG
        )
        content.pack(
            fill="both",
            expand=True,
            padx=45,
            pady=30
        )
        tk.Label(
            content,
            text="LOBBY",
            bg=BG,
            fg=TEXT,
            font=("Arial", 28, "bold")
        ).pack(anchor="w")
        tk.Label(
            content,
            text="Danh sách phòng đang chờ",
            bg=BG,
            fg=SUB_TEXT,
            font=("Arial", 12)
        ).pack(
            anchor="w",
            pady=5
        )
        self.button(
            content,
            "+ TẠO PHÒNG",
            self.show_create_room,
            20
        ).pack(
            anchor="w",
            pady=20
        )
        tk.Label(
            content,
            text="DANH SÁCH PHÒNG",
            bg=BG,
            fg=TEXT,
            font=("Arial", 15, "bold")
        ).pack(
            anchor="w",
            pady=10
        )
        for room in rooms:
            self.create_room_card(
                content,
                room
            )
    def create_room_card(self, parent, room):
        card = tk.Frame(
            parent,
            bg=CARD,
            height=75
        )
        card.pack(
            fill="x",
            pady=5
        )
        card.pack_propagate(False)
        info = tk.Frame(
            card,
            bg=CARD
        )
        info.pack(
            side="left",
            padx=20
        )
        tk.Label(
            info,
            text=room["name"],
            bg=CARD,
            fg=TEXT,
            font=("Arial", 13, "bold")
        ).pack(anchor="w")
        tk.Label(
            info,
            text=(
                f'Mã phòng: #{room["id"]}   |   '
                f'Cấp độ: {room["level"]}   |   '
                f'👤 {room["player"]}'
            ),
            bg=CARD,
            fg=SUB_TEXT,
            font=("Arial", 10)
        ).pack(anchor="w", pady=5)
        self.button(
            card,
            "JOIN",
            lambda r=room: self.join_room(r),
            10
        ).pack(
            side="right",
            padx=20
        )
    def show_create_room(self):
        self.clear_screen()
        card = tk.Frame(
            self.root,
            bg=CARD,
            width=550,
            height=530
        )
        card.place(
            relx=0.5,
            rely=0.5,
            anchor="center"
        )
        card.pack_propagate(False)
        tk.Label(
            card,
            text="Tạo phòng",
            bg=CARD,
            fg=TEXT,
            font=("Arial", 30, "bold")
        ).pack(
            anchor="w",
            padx=50,
            pady=(40, 5)
        )
        tk.Label(
            card,
            text="Tạo phòng Sudoku mới",
            bg=CARD,
            fg=SUB_TEXT,
            font=("Arial", 13)
        ).pack(
            anchor="w",
            padx=50
        )
        tk.Label(
            card,
            text="Tên phòng",
            bg=CARD,
            fg=TEXT,
            font=("Arial", 12, "bold")
        ).pack(
            anchor="w",
            padx=50,
            pady=(30, 8)
        )
        self.room_name = tk.Entry(
            card,
            bg=CARD2,
            fg=TEXT,
            insertbackground=TEXT,
            font=("Arial", 13),
            relief="flat"
        )
        self.room_name.pack(
            padx=50,
            fill="x",
            ipady=12
        )
        tk.Label(
            card,
            text="Cấp độ người chơi",
            bg=CARD,
            fg=TEXT,
            font=("Arial", 12, "bold")
        ).pack(
            anchor="w",
            padx=50,
            pady=(25, 8)
        )
        self.level = tk.StringVar()
        self.level.set("Tân binh")
        level_menu = tk.OptionMenu(
            card,
            self.level,
            "Tân binh",
            "Cao thủ",
            "Chuyên gia"
        )
        level_menu.config(
            bg=CARD2,
            fg=TEXT,
            activebackground=PRIMARY,
            activeforeground=TEXT,
            font=("Arial", 12),
            relief="flat"
        )
        level_menu["menu"].config(
            bg=CARD2,
            fg=TEXT
        )
        level_menu.pack(
            padx=50,
            fill="x"
        )
        buttons = tk.Frame(
            card,
            bg=CARD
        )
        buttons.pack(pady=35)
        tk.Button(
            buttons,
            text="Hủy",
            command=self.show_lobby,
            width=18,
            height=2,
            bg=CARD2,
            fg=TEXT,
            relief="flat",
            font=("Arial", 11)
        ).pack(
            side="left",
            padx=5
        )
        self.button(
            buttons,
            "Tạo phòng",
            self.create_room,
            18
        ).pack(
            side="left",
            padx=5
        )
    def create_room(self):
        name = self.room_name.get().strip()
        level = self.level.get()
        if not name:
            messagebox.showwarning(
                "Thông báo",
                "Vui lòng nhập tên phòng!"
            )
            return
        room_id = random.randint(100, 999)
        room = {
            "id": room_id,
            "name": name,
            "level": level,
            "player": self.username
        }
        rooms.append(room)
        self.current_room = room
        self.current_level = level
        self.show_room()
    def join_room(self, room):
        self.current_room = room
        self.current_level = room["level"]
        self.show_room()
    def show_room(self):
        self.clear_screen()
        card = tk.Frame(
            self.root,
            bg=CARD,
            width=700,
            height=600
        )
        card.place(
            relx=0.5,
            rely=0.5,
            anchor="center"
        )
        card.pack_propagate(False)
        tk.Label(
            card,
            text="PHÒNG SUDOKU",
            bg=CARD,
            fg=PRIMARY,
            font=("Arial", 28, "bold")
        ).pack(pady=(35, 10))
        tk.Label(
            card,
            text=self.current_room["name"],
            bg=CARD,
            fg=TEXT,
            font=("Arial", 20, "bold")
        ).pack()
        tk.Label(
            card,
            text=f'Mã phòng: #{self.current_room["id"]}',
            bg=CARD,
            fg=SUB_TEXT,
            font=("Arial", 13)
        ).pack(pady=8)
        tk.Label(
            card,
            text=f'Cấp độ: {self.current_room["level"]}',
            bg=CARD,
            fg=YELLOW,
            font=("Arial", 13, "bold")
        ).pack(pady=10)
        player_box = tk.Frame(
            card,
            bg=CARD2,
            width=550,
            height=120
        )
        player_box.pack(pady=15)
        player_box.pack_propagate(False)
        tk.Label(
            player_box,
            text="NGƯỜI CHƠI",
            bg=CARD2,
            fg=SUB_TEXT,
            font=("Arial", 11, "bold")
        ).pack(pady=(20, 5))
        tk.Label(
            player_box,
            text=f"👤 {self.username}",
            bg=CARD2,
            fg=TEXT,
            font=("Arial", 16, "bold")
        ).pack()
        tk.Label(
            card,
            text="🟡 Đang chờ người chơi thứ 2...",
            bg=CARD,
            fg=YELLOW,
            font=("Arial", 14, "bold")
        ).pack(pady=20)
        self.button(
            card,
            "BẮT ĐẦU GAME",
            self.start_game,
            25
        ).pack(pady=10)
        tk.Button(
            card,
            text="RỜI PHÒNG",
            command=self.show_lobby,
            width=25,
            height=2,
            bg=RED,
            fg=TEXT,
            relief="flat",
            font=("Arial", 11, "bold")
        ).pack()
    def start_game(self):

        self.clear_screen()
        difficulty_map = {
            "Tân binh": "de",
            "Cao thủ": "vua",
            "Chuyên gia": "kho"
        }
        difficulty = difficulty_map.get(
            self.current_level,
            "vua"
        )
        self.board = generate_sudoku(
            difficulty
        )
        self.solution = [
            row[:] for row in self.board
        ]
        backtracking(
            self.solution
        )
        self.sudoku = SudokuBoard(
            self.board,
            self.solution
        )
        self.timer = SudokuTimer(
            mode="countdown",
            duration_seconds=600
        )
        self.scoring = SudokuScoring(
            correct_points=10,
            incorrect_penalty=5
        )
        self.timer.start()
        header = tk.Frame(
            self.root,
            bg=CARD,
            height=70
        )
        header.pack(fill="x")
        tk.Label(
            header,
            text="SUDOKU ĐỐI KHÁNG",
            bg=CARD,
            fg=PRIMARY,
            font=("Arial", 20, "bold")
        ).pack(
            side="left",
            padx=25,
            pady=18
        )
        self.timer_label = tk.Label(
            header,
            text="10:00",
            bg=CARD,
            fg=TEXT,
            font=("Arial", 17, "bold")
        )
        self.timer_label.pack(
            side="right",
            padx=30
        )
        info = tk.Frame(
            self.root,
            bg=BG
        )
        info.pack(
            fill="x",
            padx=35,
            pady=12
        )
        tk.Label(
            info,
            text=f"👤 {self.username}",
            bg=BG,
            fg=TEXT,
            font=("Arial", 12, "bold")
        ).pack(side="left")
        self.score_label = tk.Label(
            info,
            text="🎯 Điểm: 0",
            bg=BG,
            fg=GREEN,
            font=("Arial", 12, "bold")
        )
        self.score_label.pack(
            side="left",
            padx=30
        )
        tk.Label(
            info,
            text=f"⚔ Độ khó: {self.current_level}",
            bg=BG,
            fg=YELLOW,
            font=("Arial", 12, "bold")
        ).pack(side="right")
        board_frame = tk.Frame(
            self.root,
            bg=TEXT
        )
        board_frame.pack(
            pady=5
        )
        self.entries = []
        for r in range(9):
            row_entries = []
            for c in range(9):
                value = self.board[r][c]
                entry = tk.Entry(
                    board_frame,
                    width=2,
                    font=("Arial", 18, "bold"),
                    justify="center",
                    relief="solid",
                    bd=1
                )
                entry.grid(
                    row=r,
                    column=c,
                    padx=2,
                    pady=2,
                    ipady=5
                )
                if value != 0:
                    entry.insert(
                        0,
                        str(value)
                    )
                    entry.config(
                        state="disabled"
                    )
                else:
                    entry.bind(
                        "<FocusOut>",
                        lambda event,
                        rr=r,
                        cc=c:
                        self.check_cell(rr, cc)
                    )
                row_entries.append(entry)
            self.entries.append(row_entries)
        self.button(
            self.root,
            "NỘP BÀI",
            self.submit_game,
            20
        ).pack(pady=15)
        tk.Button(
            self.root,
            text="RỜI GAME",
            command=self.leave_game,
            width=20,
            height=2,
            bg=RED,
            fg=TEXT,
            relief="flat",
            font=("Arial", 10, "bold")
        ).pack()
        self.update_timer()
    def check_cell(self, row, col):
        entry = self.entries[row][col]
        value = entry.get().strip()
        if value == "":
            return
        try:
            number = int(value)
        except ValueError:
            entry.delete(0, tk.END)
            return
        if number < 1 or number > 9:
            entry.delete(0, tk.END)
            messagebox.showwarning(
                "Lỗi",
                "Chỉ được nhập số từ 1 đến 9."
            )
            return
        try:
            correct = self.sudoku.set_value(
                row,
                col,
                number
            )
            if correct:
                entry.config(
                    fg=GREEN
                )
                self.scoring.on_correct_move()
            else:
                entry.config(
                    fg=RED
                )
                self.scoring.on_incorrect_move()
            self.score_label.config(
                text=f"🎯 Điểm: {self.scoring.get_score()}"
            )
        except ValueError:
            messagebox.showwarning(
                "Lỗi",
                "Không thể nhập vào ô này."
            )
    def update_timer(self):
        if self.timer is None:
            return
        remaining = self.timer.get_remaining_time()
        minutes = int(remaining) // 60
        seconds = int(remaining) % 60
        self.timer_label.config(
            text=f"{minutes:02d}:{seconds:02d}"
        )
        if remaining > 0:
            self.root.after(
                1000,
                self.update_timer
            )
        else:
            messagebox.showinfo(
                "Hết giờ",
                "Đã hết thời gian!"
            )
    def submit_game(self):
        if self.sudoku.check_win_condition():
            remaining = self.timer.get_remaining_time()
            bonus = self.scoring.add_time_bonus(
                remaining
            )
            messagebox.showinfo(
                "KẾT QUẢ",
                f"🎉 Bạn đã hoàn thành Sudoku!\n\n"
                f"Điểm: {self.scoring.get_score()}\n"
                f"Thưởng thời gian: +{bonus}"
            )
        else:
            messagebox.showwarning(
                "Chưa hoàn thành",
                "Bảng Sudoku vẫn chưa chính xác!"
            )
    def leave_game(self):
        self.timer = None
        self.show_lobby()
if __name__ == "__main__":
    root = tk.Tk()
    app = SudokuApp(root)
    root.mainloop()