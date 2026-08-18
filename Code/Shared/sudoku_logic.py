import time

class SudokuBoard:
    """
    Quản lý trạng thái lưới Sudoku 9x9, các quy tắc kiểm tra tính hợp lệ, tính đúng đắn của nước đi và theo dõi tiến độ.
    """
    def __init__(self, initial_grid=None, solution_grid=None):
        self.initial_grid = [[0]*9 for _ in range(9)]
        self.current_grid = [[0]*9 for _ in range(9)]
        self.solution_grid = [[0]*9 for _ in range(9)]
        
        if initial_grid:
            self.set_grids(initial_grid, solution_grid)

    def set_grids(self, initial_grid, solution_grid=None):
        """
        Thiết lập các lưới. Sao chép initial_grid sang current_grid.
        
        :param initial_grid: Danh sách các số nguyên kích thước 9x9, trong đó 0 là ô trống.
        :param solution_grid: Danh sách các số nguyên kích thước 9x9, đại diện cho lời giải hoàn chỉnh của câu đố.
        """
        if len(initial_grid) != 9 or any(len(row) != 9 for row in initial_grid):
            raise ValueError("Lưới ban đầu phải là ma trận 9x9")
            
        self.initial_grid = [list(row) for row in initial_grid]
        self.current_grid = [list(row) for row in initial_grid]
        
        if solution_grid:
            if len(solution_grid) != 9 or any(len(row) != 9 for row in solution_grid):
                raise ValueError("Lưới giải phải là ma trận 9x9")
            self.solution_grid = [list(row) for row in solution_grid]
        else:
            # Nếu không cung cấp lưới giải, ta mặc định để trống-Module khác sẽ giải Sudoku sau.
            self.solution_grid = [[0]*9 for _ in range(9)]

    def get_value(self, row, col):
        """
        Lấy giá trị của ô tại (row, col).
        """
        self._validate_coordinates(row, col)
        return self.current_grid[row][col]

    def is_fixed(self, row, col):
        """
        Trả về True nếu ô tại vị trí (row, col) là một phần của câu đố ban đầu (cố định).
        """
        self._validate_coordinates(row, col)
        return self.initial_grid[row][col] != 0

    def is_valid_sudoku_rule(self, row, col, value):
        """
        Kiểm tra nếu việc đặt `value` tại `(row, col)` tuân thủ quy tắc Sudoku.
        Giá trị ô là 0 được coi là hợp lệ (xóa).
        
        :param row: Chỉ số hàng (0-8)
        :param col: Chỉ số cột (0-8)
        :param value: Giá trị cần đặt (0-9)
        :return: True nếu hợp lệ, False nếu không hợp lệ
        """
        self._validate_coordinates(row, col)
        if not (0 <= value <= 9):
            return False
            
        if value == 0:
            return True

        # Kiểm tra hàng
        for c in range(9):
            if c != col and self.current_grid[row][c] == value:
                return False

        # Kiểm tra cột
        for r in range(9):
            if r != row and self.current_grid[r][col] == value:
                return False

        # Kiểm tra ô 3x3
        start_row, start_col = 3 * (row // 3), 3 * (col // 3)
        for r in range(start_row, start_row + 3):
            for c in range(start_col, start_col + 3):
                if (r != row or c != col) and self.current_grid[r][c] == value:
                    return False

        return True

    def is_correct_value(self, row, col, value):
        """
        So sánh `value` tại `(row, col)` với ô khớp trong `solution_grid`.
        Lưu ý: Kiểm tra xem có khớp với giải pháp duy nhất không.
        """
        self._validate_coordinates(row, col)
        return self.solution_grid[row][col] == value

    def set_value(self, row, col, value):
        """
        Đặt giá trị vào `current_grid` sau khi xác nhận.
        
        :param row: Chỉ số hàng (0-8)
        :param col: Chỉ số cột (0-8)
        :param value: Giá trị cần đặt (0-9)
        :return: bool: True nếu giá trị nhập vào đúng (khớp với giải pháp), False nếu không
        :raises ValueError: nếu ô bị cố định hoặc tọa độ/giá trị nằm ngoài giới hạn.
        """
        self._validate_coordinates(row, col)
        if self.is_fixed(row, col):
            raise ValueError(f"Không thể chỉnh sửa ô cố định tại ({row}, {col})")
            
        if not (0 <= value <= 9):
            raise ValueError("Giá trị phải từ 0 đến 9")

        self.current_grid[row][col] = value
        
        if value == 0:
            return False
            
        return self.is_correct_value(row, col, value)

    def check_win_condition(self):
        """
        Kiểm tra xem toàn bộ bảng đã được giải đúng chưa.
        """
        for r in range(9):
            for c in range(9):
                # Tất cả các ô phải khớp với giải pháp
                if self.current_grid[r][c] != self.solution_grid[r][c]:
                    return False
        return True

    def get_progress(self):
        """
        Trả về tỷ lệ phần trăm các ô đã điền trên bảng (từ 0.0 đến 100.0).
        """
        filled = sum(1 for r in range(9) for c in range(9) if self.current_grid[r][c] != 0)
        return (filled / 81.0) * 100.0

    def get_correct_progress(self):
        """
        Trả về tỷ lệ phần trăm các ô khớp với giải pháp (từ 0.0 đến 100.0).
        """
        correct = sum(1 for r in range(9) for c in range(9) if self.current_grid[r][c] == self.solution_grid[r][c])
        return (correct / 81.0) * 100.0

    def _validate_coordinates(self, row, col):
        if not (0 <= row < 9) or not (0 <= col < 9):
            raise IndexError(f"Tọa độ ô ngoài giới hạn: ({row}, {col})")


class SudokuTimer:
    """
    Đồng hồ hỗ trợ start, pause, resume, phạt, đếm ngược và định dạng MM:SS.
    """
    def __init__(self, mode="stopwatch", duration_seconds=0):
        """
        :param mode: "stopwatch" (đếm lên) hoặc "countdown" (đếm ngược)
        :param duration_seconds: Thời gian bắt đầu cho chế độ đếm ngược (tính bằng giây)
        """
        self.mode = mode.lower()
        self.duration_seconds = duration_seconds
        
        self.start_time = None
        self.accumulated_time = 0.0
        self.penalty_seconds = 0.0
        self.is_running = False

    def start(self):
        """
        Bắt đầu hoặc reset và bắt đầu hẹn giờ.
        """
        self.start_time = time.time()
        self.accumulated_time = 0.0
        self.penalty_seconds = 0.0
        self.is_running = True

    def pause(self):
        """
        Tạm dừng hẹn giờ, tích lũy thời gian trôi qua.
        """
        if self.is_running:
            self.accumulated_time += time.time() - self.start_time
            self.is_running = False

    def resume(self):
        """
        Tiếp tục hẹn giờ đã tạm dừng.
        """
        if not self.is_running:
            self.start_time = time.time()
            self.is_running = True

    def stop(self):
        """
        Dừng hẹn giờ.
        """
        if self.is_running:
            self.accumulated_time += time.time() - self.start_time
            self.is_running = False

    def add_penalty(self, seconds):
        """
        Thêm giây phạt.
        Trong chế độ stopwatch: tăng thời gian đã trôi qua (cộng giây phạt).
        Trong chế độ countdown: giảm thời gian còn lại (cộng giây phạt vào bộ tích lũy phạt, được trừ đi).
        """
        self.penalty_seconds += seconds

    def get_elapsed_time(self):
        """
        Trả về tổng thời gian đã trôi qua tính bằng giây.
        """
        elapsed = self.accumulated_time
        if self.is_running:
            elapsed += time.time() - self.start_time
            
        if self.mode == "stopwatch":
            elapsed += self.penalty_seconds
        else:
            # Trong chế độ đếm ngược, hình phạt làm giảm thời gian còn lại, tương đương với tăng thời gian đã trôi qua
            elapsed += self.penalty_seconds
            
        return elapsed

    def get_remaining_time(self):
        """
        Trả về thời gian còn lại tính bằng giây (chỉ áp dụng cho chế độ đếm ngược).
        """
        if self.mode != "countdown":
            return 0.0
        remaining = self.duration_seconds - self.get_elapsed_time()
        return max(0.0, remaining)

    def get_formatted_time(self):
        """
        Trả về thời gian định dạng MM:SS.
        """
        if self.mode == "countdown":
            import math
            total_seconds = math.ceil(self.get_remaining_time())
        else:
            total_seconds = int(self.get_elapsed_time())

        minutes = total_seconds // 60
        seconds = total_seconds % 60
        return f"{minutes:02d}:{seconds:02d}"


class SudokuScoring:
    """
    Quản lý việc theo dõi điểm số, hình phạt, lỗi và thưởng thời gian.
    """
    def __init__(self, correct_points=10, incorrect_penalty=5):
        self.correct_points = correct_points
        self.incorrect_penalty = incorrect_penalty
        self.score = 0
        self.errors = 0
        self.correct_moves = 0

    def reset(self):
        self.score = 0
        self.errors = 0
        self.correct_moves = 0

    def on_correct_move(self):
        """
        Được kích hoạt khi người chơi nhập một số đúng.
        """
        self.score += self.correct_points
        self.correct_moves += 1
        return self.score

    def on_incorrect_move(self):
        """
        Được kích hoạt khi người chơi nhập một số sai.
        """
        self.score -= self.incorrect_penalty
        self.errors += 1
        return self.score

    def add_time_bonus(self, remaining_seconds, points_per_second=5):
        """
        Áp dụng tiền thưởng khi hoàn thành bảng sớm.
        """
        bonus = int(remaining_seconds) * points_per_second
        self.score += max(0, bonus)
        return bonus

    def get_score(self):
        return self.score

    def get_errors(self):
        return self.errors
