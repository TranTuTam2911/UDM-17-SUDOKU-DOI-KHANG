import random


def valid(board, r, c, n):
    """Kiểm tra xem số n có thể đặt vào ô (r, c) không."""
    if n in board[r]:
        return False
    if any(board[i][c] == n for i in range(9)):
        return False

    br, bc = r // 3 * 3, c // 3 * 3
    for i in range(br, br + 3):
        for j in range(bc, bc + 3):
            if board[i][j] == n:
                return False
    return True


def backtracking(board):
    """Giải board Sudoku bằng thuật toán quay lui."""
    for r in range(9):
        for c in range(9):
            if board[r][c] == 0:
                nums = list(range(1, 10))
                random.shuffle(nums)

                for n in nums:
                    if valid(board, r, c, n):
                        board[r][c] = n
                        if backtracking(board):
                            return True
                        board[r][c] = 0

                return False
    return True


def generate_full_board():
    """Tạo một bảng Sudoku hoàn chỉnh."""
    board = [[0 for _ in range(9)] for _ in range(9)]
    backtracking(board)
    return board


def generate_puzzle(empties=40):
    """Tạo một board Sudoku có ô trống để người chơi điền."""
    board = generate_full_board()
    puzzle = [row[:] for row in board]
    positions = [(r, c) for r in range(9) for c in range(9)]
    random.shuffle(positions)

    for r, c in positions[:empties]:
        puzzle[r][c] = 0

    return puzzle
