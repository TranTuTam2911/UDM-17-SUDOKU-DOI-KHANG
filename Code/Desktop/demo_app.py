import tkinter as tk
from tkinter import messagebox
from sudoku_logic import SudokuBoard, SudokuTimer, SudokuScoring
from backtrack import generate_sudoku, backtracking

# ----- Hàm sinh đề bài ngỪu nhiên -----
DEFAULT_DIFFICULTY = "kho"  # "de" | "vua" | "kho"

def new_puzzle(difficulty=DEFAULT_DIFFICULTY):
    """Sinh một cặp (initial_grid, solution_grid) mới ngỪu nhiên."""
    solution = generate_sudoku(difficulty)   # Bảng đã xóa bớt (là đề bài)
    # Sao chép đề bài trước khi giải để giữ lại initial
    initial = [row[:] for row in solution]
    backtracking(solution)                   # Điền đầy đủ → lời giải
    return initial, solution


# Color Palette Definitions
COLOR_BG = "#F5F6F8"
COLOR_SIDEBAR_BG = "#FFFFFF"
COLOR_CELL_BG = "#FFFFFF"
COLOR_FIXED_TEXT = "#2C3E50"
COLOR_USER_TEXT = "#0056B3"
COLOR_SELECTED = "#D2E5FC"       # Ô đang chọn
COLOR_HIGHLIGHTED = "#EBF3FC"    # Hàng / cột / khối 3x3 liên quan
COLOR_SAME_NUMBER = "#C8E6FA"    # Các ô có cùng số với ô đang chọn
COLOR_CORRECT_BG = "#E2F0D9"
COLOR_CORRECT_TEXT = "#385723"
COLOR_INCORRECT_BG = "#FCE4D6"
COLOR_INCORRECT_TEXT = "#C00000"
COLOR_BORDER = "#1E293B"

class SudokuDemoApp(tk.Tk):
    def __init__(self):
        super().__init__()
        
        self.title("Sudoku PvP Logic Demo")
        self.geometry("900x700")
        self.configure(bg=COLOR_BG)
        self.resizable(False, False)
        
        # Sinh đề bài ngỪu nhiên cho ván đầu tiên
        initial_grid, solution_grid = new_puzzle()
        
        # Game State Objects
        self.board = SudokuBoard(initial_grid, solution_grid)
        self.timer = SudokuTimer(mode="countdown", duration_seconds=300) # 5 minutes countdown
        self.scoring = SudokuScoring(correct_points=10, incorrect_penalty=5)
        
        self.selected_cell = None  # Tuple: (row, col)
        self.game_over = False      # Khóa input khi game kết thúc
        self.timer_loop_id = None   # ID của vòng lặp after() để có thể hủy
        
        # Grid of Label widgets for the board
        # Size is 9x9, mapped to row, col
        self.cells = [[None for _ in range(9)] for _ in range(9)]
        
        self.setup_ui()
        
        # Bind keyboard events
        self.bind("<Key>", self.handle_key_press)
        
        # Start game
        self.timer.start()
        self.update_stats()      # Hiển thị tiến độ ban đầu ngay khi khởi động
        self.update_timer_loop()
        
    def setup_ui(self):
        # Header title
        header_frame = tk.Frame(self, bg="#1E293B", height=60)
        header_frame.pack(side="top", fill="x")
        
        title_label = tk.Label(
            header_frame, 
            text="SUDOKU PVP ENGINE - LOGIC DEMO", 
            font=("Segoe UI", 16, "bold"), 
            fg="#FFFFFF", 
            bg="#1E293B"
        )
        title_label.pack(pady=15)
        
        # Main container split into Left (Board) and Right (Sidebar)
        container = tk.Frame(self, bg=COLOR_BG)
        container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Left Panel (Board Frame)
        left_panel = tk.Frame(container, bg=COLOR_BG)
        left_panel.pack(side="left", fill="both", expand=True)
        
        # The 9x9 Sudoku Board Frame
        board_outer_frame = tk.Frame(left_panel, bg=COLOR_BORDER, bd=3, relief="solid")
        board_outer_frame.pack(anchor="center", pady=10)
        
        # Create 3x3 Box Frames to easily format thick border lines
        self.box_frames = [[None for _ in range(3)] for _ in range(3)]
        for br in range(3):
            for bc in range(3):
                box = tk.Frame(board_outer_frame, bg=COLOR_BORDER, bd=1.5, relief="solid")
                box.grid(row=br, column=bc, padx=1, pady=1)
                self.box_frames[br][bc] = box

        # Place cells inside the 3x3 Box Frames
        for r in range(9):
            for c in range(9):
                br, bc = r // 3, c // 3
                box = self.box_frames[br][bc]
                
                cell_val = self.board.get_value(r, c)
                is_fixed = self.board.is_fixed(r, c)
                
                text = str(cell_val) if cell_val != 0 else ""
                fg_color = COLOR_FIXED_TEXT if is_fixed else COLOR_USER_TEXT
                font_style = ("Segoe UI", 16, "bold") if is_fixed else ("Segoe UI", 16)
                
                cell_lbl = tk.Label(
                    box, 
                    text=text, 
                    font=font_style, 
                    fg=fg_color, 
                    bg=COLOR_CELL_BG,
                    width=4, 
                    height=2, 
                    relief="flat",
                    cursor="hand2"
                )
                cell_lbl.grid(row=r % 3, column=c % 3, padx=1, pady=1)
                
                # Bind events to labels
                cell_lbl.bind("<Button-1>", lambda event, r=r, c=c: self.select_cell(r, c))
                self.cells[r][c] = cell_lbl

        # Right Panel (Sidebar for info, stats, and keypad)
        sidebar = tk.Frame(container, bg=COLOR_SIDEBAR_BG, width=280, bd=1, relief="solid")
        sidebar.pack(side="right", fill="y", padx=(10, 0))
        sidebar.pack_propagate(False)
        
        # Timer Display
        timer_section = tk.Frame(sidebar, bg=COLOR_SIDEBAR_BG)
        timer_section.pack(fill="x", pady=15)
        
        tk.Label(timer_section, text="⏰ THỜI GIAN CÒN LẠI", font=("Segoe UI", 10, "bold"), fg="#555", bg=COLOR_SIDEBAR_BG).pack()
        self.timer_label = tk.Label(timer_section, text="05:00", font=("Segoe UI", 24, "bold"), fg="#D32F2F", bg=COLOR_SIDEBAR_BG)
        self.timer_label.pack(pady=5)
        
        # Stats Display
        stats_frame = tk.Frame(sidebar, bg=COLOR_SIDEBAR_BG)
        stats_frame.pack(fill="x", pady=10, padx=20)
        
        # Score
        self.score_label = tk.Label(stats_frame, text="Điểm số: 0", font=("Segoe UI", 12, "bold"), fg="#2E7D32", bg=COLOR_SIDEBAR_BG, anchor="w")
        self.score_label.pack(fill="x", pady=3)
        
        # Errors
        self.error_label = tk.Label(stats_frame, text="Số lỗi: 0 / 3", font=("Segoe UI", 12, "bold"), fg="#C62828", bg=COLOR_SIDEBAR_BG, anchor="w")
        self.error_label.pack(fill="x", pady=3)
        
        # Progress Bar & Percent Label
        progress_frame = tk.Frame(sidebar, bg=COLOR_SIDEBAR_BG)
        progress_frame.pack(fill="x", pady=10, padx=20)
        
        tk.Label(progress_frame, text="Tiến độ hoàn thành:", font=("Segoe UI", 10), fg="#555", bg=COLOR_SIDEBAR_BG, anchor="w").pack(fill="x")
        self.progress_lbl = tk.Label(progress_frame, text="0.0%", font=("Segoe UI", 12, "bold"), fg="#1E293B", bg=COLOR_SIDEBAR_BG, anchor="w")
        self.progress_lbl.pack(fill="x", pady=2)
        
        # Progress canvas bar
        self.progress_canvas = tk.Canvas(progress_frame, height=12, bg="#E2E8F0", highlightthickness=0)
        self.progress_canvas.pack(fill="x", pady=5)
        self.progress_bar = self.progress_canvas.create_rectangle(0, 0, 0, 12, fill="#0284C7")
        self.update_progress_bar(0.0)

        # Separator line
        tk.Frame(sidebar, height=1, bg="#E2E8F0").pack(fill="x", pady=10)

        # Virtual Keypad Frame
        keypad_lbl = tk.Label(sidebar, text="BÀN PHÍM ẢO", font=("Segoe UI", 10, "bold"), fg="#555", bg=COLOR_SIDEBAR_BG)
        keypad_lbl.pack(pady=5)
        
        keypad_frame = tk.Frame(sidebar, bg=COLOR_SIDEBAR_BG)
        keypad_frame.pack(pady=5)
        
        # Generate keypad buttons 1-9
        for i in range(9):
            num = i + 1
            btn = tk.Button(
                keypad_frame, 
                text=str(num), 
                font=("Segoe UI", 12, "bold"), 
                width=4, 
                height=2,
                command=lambda n=num: self.input_number(n),
                bg="#F1F5F9", 
                activebackground="#E2E8F0",
                relief="groove"
            )
            btn.grid(row=i // 3, column=i % 3, padx=4, pady=4)
            
        # Action Buttons
        actions_frame = tk.Frame(sidebar, bg=COLOR_SIDEBAR_BG)
        actions_frame.pack(fill="x", pady=15, padx=20)
        
        clear_btn = tk.Button(
            actions_frame, 
            text="❌ XÓA Ô", 
            font=("Segoe UI", 11, "bold"), 
            bg="#EF4444", 
            fg="#FFFFFF", 
            command=self.clear_cell,
            relief="flat",
            activebackground="#DC2626",
            activeforeground="#FFFFFF"
        )
        clear_btn.pack(fill="x", pady=5)
        
        reset_btn = tk.Button(
            actions_frame, 
            text="🔄 CHƠI LẠI", 
            font=("Segoe UI", 11, "bold"), 
            bg="#475569", 
            fg="#FFFFFF", 
            command=self.reset_game,
            relief="flat",
            activebackground="#334155",
            activeforeground="#FFFFFF"
        )
        reset_btn.pack(fill="x", pady=5)

    def select_cell(self, row, col):
        self.selected_cell = (row, col)
        self.redraw_highlights()

    def redraw_highlights(self):
        # Lấy giá trị ô đang chọn để tô sáng các ô cùng số
        selected_val = 0
        if self.selected_cell:
            selected_val = self.board.get_value(*self.selected_cell)

        # Refresh colors of all cells
        for r in range(9):
            for c in range(9):
                is_fixed = self.board.is_fixed(r, c)
                val = self.board.get_value(r, c)
                cell_lbl = self.cells[r][c]

                # --- Xác định background ---
                is_selected = self.selected_cell and (r, c) == self.selected_cell
                is_related = self.selected_cell and (
                    r == self.selected_cell[0]
                    or c == self.selected_cell[1]
                    or (r // 3 == self.selected_cell[0] // 3 and c // 3 == self.selected_cell[1] // 3)
                )
                is_same_num = (
                    selected_val != 0
                    and val == selected_val
                    and not is_selected
                )

                # Ư u tiên: ô đang chọn > cùng số > hàng/cột/khối > nền trắng
                if is_selected:
                    bg_color = COLOR_SELECTED
                elif is_same_num:
                    bg_color = COLOR_SAME_NUMBER
                elif is_related:
                    bg_color = COLOR_HIGHLIGHTED
                else:
                    bg_color = COLOR_CELL_BG

                # --- Xác định foreground (chữ) ---
                # Ô người dùng điền: tô xanh lá (dúng) hoặc đỏ (sai)
                if val != 0 and not is_fixed:
                    if self.board.is_correct_value(r, c, val):
                        cell_lbl.configure(bg=bg_color if is_selected or is_same_num else COLOR_CORRECT_BG,
                                           fg=COLOR_CORRECT_TEXT)
                    else:
                        cell_lbl.configure(bg=bg_color if is_selected or is_same_num else COLOR_INCORRECT_BG,
                                           fg=COLOR_INCORRECT_TEXT)
                    continue

                fg_color = COLOR_FIXED_TEXT if is_fixed else COLOR_USER_TEXT
                cell_lbl.configure(bg=bg_color, fg=fg_color)

    def input_number(self, num):
        # Chặn thao tác khi game đã kết thúc
        if self.game_over:
            return
            
        if not self.selected_cell:
            messagebox.showinfo("Thông báo", "Vui lòng chọn một ô trống trên bàn cờ trước!")
            return
            
        r, c = self.selected_cell
        
        if self.board.is_fixed(r, c):
            return
            
        old_val = self.board.get_value(r, c)
        if old_val == num:
            return  # No change

        # Apply move via board logic
        is_correct = self.board.set_value(r, c, num)
        
        # Display number
        self.cells[r][c].configure(text=str(num))
        
        # Run scoring & feedback
        if is_correct:
            self.scoring.on_correct_move()
        else:
            self.scoring.on_incorrect_move()
            # Penalize game time: deduct 15 seconds for incorrect answer (Game Rule)
            self.timer.add_penalty(15)
            
        self.update_stats()
        self.redraw_highlights()
        
        # Check end conditions
        if self.scoring.get_errors() >= 3:
            self.timer.stop()
            self.game_over = True
            messagebox.showerror("THẤT BẠI", f"Bạn đã phạm quá 3 lỗi!\nĐiểm số chung cuộc: {self.scoring.get_score()}\nNhấn CHƠI LẠI để thử lại.")
        elif self.board.check_win_condition():
            self.timer.stop()
            self.game_over = True
            # Calculate time bonus
            rem = self.timer.get_remaining_time()
            bonus = self.scoring.add_time_bonus(rem, points_per_second=5)
            self.update_stats()
            messagebox.showinfo("CHIẾN THẮNG", f"Chúc mừng! Bạn đã hoàn thành xuất sắc bàn cờ Sudoku!\nĐiểm số: {self.scoring.get_score()} (Bonus thời gian: {bonus} điểm)\nNhấn CHƠI LẠI để chơi ván mới.")

    def clear_cell(self):
        # Chặn thao tác khi game đã kết thúc
        if self.game_over:
            return
        if not self.selected_cell:
            return
        r, c = self.selected_cell
        if self.board.is_fixed(r, c):
            return
            
        self.board.set_value(r, c, 0)
        self.cells[r][c].configure(text="")
        self.redraw_highlights()
        self.update_stats()

    def handle_key_press(self, event):
        # Keyboard numbers 1-9
        if event.char in "123456789":
            self.input_number(int(event.char))
        # Clear triggers
        elif event.keysym in ("BackSpace", "Delete", "0"):
            self.clear_cell()
        # Arrow key navigation
        elif event.keysym in ("Up", "Down", "Left", "Right"):
            if not self.selected_cell:
                self.select_cell(0, 0)
                return
            r, c = self.selected_cell
            if event.keysym == "Up":
                r = (r - 1) % 9
            elif event.keysym == "Down":
                r = (r + 1) % 9
            elif event.keysym == "Left":
                c = (c - 1) % 9
            elif event.keysym == "Right":
                c = (c + 1) % 9
            self.select_cell(r, c)

    def update_stats(self):
        self.score_label.configure(text=f"Điểm số: {self.scoring.get_score()}")
        self.error_label.configure(text=f"Số lỗi: {self.scoring.get_errors()} / 3")
        
        # Vấn đề 2: Chỉ tính tiến độ dựa trên ô điền ĐÚNG (khớp với lời giải)
        progress = self.board.get_correct_progress()
        self.progress_lbl.configure(text=f"{progress:.1f}%")
        self.update_progress_bar(progress)

    def update_progress_bar(self, progress):
        width = 240  # matches canvas width
        fill_width = int(width * (progress / 100.0))
        self.progress_canvas.coords(self.progress_bar, 0, 0, fill_width, 12)

    def update_timer_loop(self):
        # Update clock
        self.timer_label.configure(text=self.timer.get_formatted_time())
        
        # Vấn đề 1: Dừng vòng lặp nếu game đã kết thúc (game_over)
        if self.game_over:
            return
        
        # Check if countdown ended
        if self.timer.get_remaining_time() <= 0:
            self.timer.stop()
            self.game_over = True  # Khóa input, dừng vòng lặp
            self.timer_label.configure(text="00:00")
            messagebox.showwarning("HẾT GIỜ", f"Trận đấu đã kết thúc do hết thời gian!\nĐiểm số chung cuộc: {self.scoring.get_score()}\nNhấn CHƠI LẠI để thử lại.")
            return
            
        # Loop every 1 second (1000 ms)
        self.timer_loop_id = self.after(1000, self.update_timer_loop)

    def reset_game(self):
        # Hủy vòng lặp timer cũ nếu còn đang chạy
        if self.timer_loop_id is not None:
            self.after_cancel(self.timer_loop_id)
            self.timer_loop_id = None
        
        # Sinh đề bài mới ngỪu nhiên cho ván tiếp theo
        initial_grid, solution_grid = new_puzzle()
        self.board.set_grids(initial_grid, solution_grid)
        self.timer.start()
        self.scoring.reset()
        self.selected_cell = None
        self.game_over = False  # Mở khóa input cho ván mới
        
        # Clear grid labels text
        for r in range(9):
            for c in range(9):
                cell_val = self.board.get_value(r, c)
                is_fixed = self.board.is_fixed(r, c)
                self.cells[r][c].configure(text=str(cell_val) if cell_val != 0 else "")
                
        self.update_stats()
        self.redraw_highlights()
        
        # Khởi động lại vòng lặp timer cho ván mới
        self.update_timer_loop()

if __name__ == "__main__":
    app = SudokuDemoApp()
    app.mainloop()
