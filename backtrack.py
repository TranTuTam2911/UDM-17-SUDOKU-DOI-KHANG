import random
import copy


def valid(board, r, c, n):
    if n in board[r]:
        return False
    if any(board[i][c] == n for i in range(9)):
        return False

    br, bc = r // 3 * 3, c // 3 * 3
    return all(board[i][j] != n
               for i in range(br, br + 3)
               for j in range(bc, bc + 3))


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
