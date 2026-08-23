import random

def valid(board, r, c, n):
    if n in board[r]:
        return False

    if any(board[i][c] == n for i in range(9)):
        return False

    br = r // 3 * 3
    bc = c // 3 * 3

    for i in range(br, br + 3):
        for j in range(bc, bc + 3):
            if board[i][j] == n:
                return False

    return True


def backtracking(board):
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


def generate_sudoku(difficulty):
    board = [[0 for _ in range(9)] for _ in range(9)]

    backtracking(board)

    if difficulty == "de":
        remove = 35
    elif difficulty == "vua":
        remove = 45
    elif difficulty == "kho":
        remove = 55
    else:
        remove = 45

    positions = []

    for r in range(9):
        for c in range(9):
            positions.append((r, c))

    random.shuffle(positions)

    for r, c in positions[:remove]:
        board[r][c] = 0

    return board


def print_board(board):
    for r in range(9):
        if r == 3 or r == 6:
            print("------+-------+------")

        for c in range(9):
            if c == 3 or c == 6:
                print("|", end=" ")

            if board[r][c] == 0:
                print(".", end=" ")
            else:
                print(board[r][c], end=" ")

        print()


if __name__ == "__main__":
    print("Game Sudoku - Backtracking")
    print("1. De")
    print("2. Vua")
    print("3. Kho")

    choice = input("Chon muc do (1/2/3): ")

    if choice == "1":
        difficulty = "de"
        difficulty_name = "De"
    elif choice == "2":
        difficulty = "vua"
        difficulty_name = "Vua"
    elif choice == "3":
        difficulty = "kho"
        difficulty_name = "Kho"
    else:
        print("Lua chon khong hop le, tu dong chon muc Vua.")
        difficulty = "vua"
        difficulty_name = "Vua"

    sudoku = generate_sudoku(difficulty)

    print("\nDe Sudoku - Muc do:", difficulty_name)
    print_board(sudoku)

    solution = [row[:] for row in sudoku]

    backtracking(solution)

    print("\nLoi giai:")
    print_board(solution)
