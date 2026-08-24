if __name__ == "__main__":
    sample_initial = [
        [5, 3, 0, 0, 7, 0, 0, 0, 0], [6, 0, 0, 1, 9, 5, 0, 0, 0], [0, 9, 8, 0, 0, 0, 0, 6, 0],
        [8, 0, 0, 0, 6, 0, 0, 0, 3], [4, 0, 0, 8, 0, 3, 0, 0, 1], [7, 0, 0, 0, 2, 0, 0, 0, 6],
        [0, 6, 0, 0, 0, 0, 2, 8, 0], [0, 0, 0, 4, 1, 9, 0, 0, 5], [0, 0, 0, 0, 8, 0, 0, 7, 9]
    ]
    sample_solution = [
        [5, 3, 4, 6, 7, 8, 9, 1, 2], [6, 7, 2, 1, 9, 5, 3, 4, 8], [1, 9, 8, 3, 4, 2, 5, 6, 7],
        [8, 5, 9, 7, 6, 1, 4, 2, 3], [4, 2, 6, 8, 5, 3, 7, 9, 1], [7, 1, 3, 9, 2, 4, 8, 5, 6],
        [9, 6, 1, 5, 3, 7, 2, 8, 4], [2, 8, 7, 4, 1, 9, 6, 3, 5], [3, 4, 5, 2, 8, 6, 1, 7, 9]
    ]

    print("=== KẾT QUẢ TEST LOGIC SUDOKU ===")
    board = SudokuBoard(sample_initial, sample_solution)
    res = board.set_value(0, 2, 4)
    print(f"Nhập số 4 vào ô (0, 2): Kết quả={res}, Giá trị ô={board.get_value(0, 2)}")

    timer = SudokuTimer(mode="countdown", duration_seconds=60)
    timer.start()
    timer.add_penalty(10)
    print(f"Thời gian đếm ngược sau phạt: {timer.get_formatted_time()}")

    scoring = SudokuScoring()
    scoring.on_correct_move()
    print(f"Điểm số hiện tại: {scoring.get_score()}")