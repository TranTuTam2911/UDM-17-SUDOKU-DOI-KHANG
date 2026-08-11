import random
import copy


def valid(board, r, c, n):/ kiem tra hop le
    if n in board[r]:/ kiem tra so n da xuat hien trong hang r 
        return False / neu co n tra ve false
    if any(board[i][c] == n for i in range(9)): / kiem tra xem so n da xuat hien o dong i thuoc cot c
        return False

    br, bc = r // 3 * 3, c // 3 * 3 / xac dinh toa do hang dau tien va cot dau tien cua o 3x3 chua vi tri
    return all(board[i][j] != n / tra ve true neu n chua xuat hien
               for i in range(br, br + 3)
               for j in range(bc, bc + 3))


def backtracking(board): / thuat quay lui
    for r in range(9): / duyet qua tung hang r
        for c in range(9): / duyet qua tung cot c
            if board[r][c] == 0: / neu trong =0
                nums = list(range(1, 10)) / tao danh sach
                random.shuffle(nums) / ngau nhien thu tu cac so

                for n in nums: / thu lan luot n trong danh sach da tron
                    if valid(board, r, c, n): / kiem tra dien n vao r,c hop le 
                        board[r][c] = n / tam gan n
                        if backtracking(board): / tiep tuc giai 
                            return True
                        board[r][c] = 0 / neu that bai

                return False
    return True
