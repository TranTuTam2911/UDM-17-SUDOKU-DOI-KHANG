import unittest
import time
from sudoku_logic import SudokuBoard, SudokuTimer, SudokuScoring

class TestSudokuBoard(unittest.TestCase):
    def setUp(self):
        # A simple, valid 9x9 Sudoku puzzle grid
        # 0 represents empty cells
        self.initial_grid = [
            [5, 3, 0, 0, 7, 0, 0, 0, 0],
            [6, 0, 0, 1, 9, 5, 0, 0, 0],
            [0, 9, 8, 0, 0, 0, 0, 6, 0],
            [8, 0, 0, 0, 6, 0, 0, 0, 3],
            [4, 0, 0, 8, 0, 3, 0, 0, 1],
            [7, 0, 0, 0, 2, 0, 0, 0, 6],
            [0, 6, 0, 0, 0, 0, 2, 8, 0],
            [0, 0, 0, 4, 1, 9, 0, 0, 5],
            [0, 0, 0, 0, 8, 0, 0, 7, 9]
        ]
        
        # The unique solution to the puzzle above
        self.solution_grid = [
            [5, 3, 4, 6, 7, 8, 9, 1, 2],
            [6, 7, 2, 1, 9, 5, 3, 4, 8],
            [1, 9, 8, 3, 4, 2, 5, 6, 7],
            [8, 5, 9, 7, 6, 1, 4, 2, 3],
            [4, 2, 6, 8, 5, 3, 7, 9, 1],
            [7, 1, 3, 9, 2, 4, 8, 5, 6],
            [9, 6, 5, 5, 3, 7, 2, 8, 4], # Wait, let's verify if row 6 has duplicate 5s?
            # Let's fix row 6: [9, 6, 5, 5, 3, 7, 2, 8, 4] is invalid.
            # Let's write a simpler, perfectly valid board representation to avoid test confusion.
            # Actually, let's just make a very basic 9x9 board structure with simple values, 
            # e.g. self.initial_grid has a few filled cells, and self.solution_grid is a fully valid completed board.
        ]
        
        # Let's use a standard mathematically valid solution grid:
        # Standard valid Latin square or valid Sudoku grid:
        # 1 2 3 | 4 5 6 | 7 8 9
        # 4 5 6 | 7 8 9 | 1 2 3
        # 7 8 9 | 1 2 3 | 4 5 6
        # ------+-------+------
        # 2 3 4 | 5 6 7 | 8 9 1
        # 5 6 7 | 8 9 1 | 2 3 4
        # 8 9 1 | 2 3 4 | 5 6 7
        # ------+-------+------
        # 3 4 5 | 6 7 8 | 9 1 2
        # 6 7 8 | 9 1 2 | 3 4 5
        # 9 1 2 | 3 4 5 | 6 7 8
        self.solution_grid = [
            [1, 2, 3, 4, 5, 6, 7, 8, 9],
            [4, 5, 6, 7, 8, 9, 1, 2, 3],
            [7, 8, 9, 1, 2, 3, 4, 5, 6],
            [2, 3, 4, 5, 6, 7, 8, 9, 1],
            [5, 6, 7, 8, 9, 1, 2, 3, 4],
            [8, 9, 1, 2, 3, 4, 5, 6, 7],
            [3, 4, 5, 6, 7, 8, 9, 1, 2],
            [6, 7, 8, 9, 1, 2, 3, 4, 5],
            [9, 1, 2, 3, 4, 5, 6, 7, 8]
        ]
        
        # Let's blank out some cells for initial_grid (e.g. set to 0)
        self.initial_grid = [
            [1, 0, 3, 4, 5, 6, 7, 8, 0],
            [0, 5, 6, 0, 8, 9, 1, 0, 3],
            [7, 8, 9, 1, 0, 3, 4, 5, 6],
            [2, 3, 0, 5, 6, 7, 0, 9, 1],
            [5, 6, 7, 8, 9, 1, 2, 3, 4],
            [8, 9, 1, 2, 3, 4, 5, 6, 7],
            [3, 4, 5, 6, 7, 8, 9, 1, 2],
            [6, 7, 8, 9, 1, 2, 3, 4, 5],
            [9, 1, 2, 3, 4, 5, 6, 7, 8]
        ]
        
        self.board = SudokuBoard(self.initial_grid, self.solution_grid)

    def test_initial_values(self):
        self.assertEqual(self.board.get_value(0, 0), 1)
        self.assertEqual(self.board.get_value(0, 1), 0)
        self.assertTrue(self.board.is_fixed(0, 0))
        self.assertFalse(self.board.is_fixed(0, 1))

    def test_set_value_validation(self):
        # Cannot edit a fixed cell
        with self.assertRaises(ValueError):
            self.board.set_value(0, 0, 9)
            
        # Can edit an empty cell
        is_correct = self.board.set_value(0, 1, 2)
        self.assertTrue(is_correct)
        self.assertEqual(self.board.get_value(0, 1), 2)
        
        # Can edit with an incorrect value
        is_correct = self.board.set_value(0, 1, 9)
        self.assertFalse(is_correct)
        self.assertEqual(self.board.get_value(0, 1), 9)

    def test_out_of_bounds_coordinates(self):
        with self.assertRaises(IndexError):
            self.board.get_value(9, 0)
        with self.assertRaises(IndexError):
            self.board.get_value(0, -1)

    def test_sudoku_rules(self):
        # Check rule validation for row, column, and box
        # Currently at (0, 1) we have 0.
        # Placing 1 should violate row rule (since 1 is at 0,0)
        self.assertFalse(self.board.is_valid_sudoku_rule(0, 1, 1))
        # Placing 2 should be valid (not present in row 0, col 1, or box 0)
        self.assertTrue(self.board.is_valid_sudoku_rule(0, 1, 2))
        # Placing 5 should violate column rule.
        self.assertFalse(self.board.is_valid_sudoku_rule(0, 1, 5))
        # Placing 7 at (0,1). Box 0 has 7 at (2,0). So it should violate box rule.
        self.assertFalse(self.board.is_valid_sudoku_rule(0, 1, 7))

    def test_win_condition(self):
        self.assertFalse(self.board.check_win_condition())
        
        self.board.set_value(0, 1, 2)
        self.board.set_value(0, 8, 9)
        self.board.set_value(1, 0, 4)
        self.board.set_value(1, 3, 7)
        self.board.set_value(1, 7, 2)
        self.board.set_value(2, 4, 2)
        self.board.set_value(3, 2, 4)
        self.board.set_value(3, 6, 8)
        
        self.assertTrue(self.board.check_win_condition())

    def test_progress(self):
        # 8 empty cells out of 81 = 73 filled cells initially.
        # 73 / 81 = 90.123%
        self.assertAlmostEqual(self.board.get_progress(), (73 / 81.0) * 100.0, places=4)
        self.board.set_value(0, 1, 2)
        # Now 74 filled.
        self.assertAlmostEqual(self.board.get_progress(), (74 / 81.0) * 100.0, places=4)


class TestSudokuTimer(unittest.TestCase):
    def test_stopwatch_mode(self):
        timer = SudokuTimer(mode="stopwatch")
        self.assertFalse(timer.is_running)
        self.assertEqual(timer.get_elapsed_time(), 0)
        self.assertEqual(timer.get_formatted_time(), "00:00")
        
        timer.start()
        self.assertTrue(timer.is_running)
        time.sleep(0.1)
        self.assertGreater(timer.get_elapsed_time(), 0.05)
        
        timer.pause()
        self.assertFalse(timer.is_running)
        elapsed_at_pause = timer.get_elapsed_time()
        time.sleep(0.1)
        # Should remain the same after pause
        self.assertEqual(timer.get_elapsed_time(), elapsed_at_pause)
        
        # Resume
        timer.resume()
        self.assertTrue(timer.is_running)
        time.sleep(0.1)
        self.assertGreater(timer.get_elapsed_time(), elapsed_at_pause + 0.05)
        
        # Stop
        timer.stop()
        self.assertFalse(timer.is_running)

    def test_timer_penalties(self):
        timer = SudokuTimer(mode="stopwatch")
        timer.start()
        timer.add_penalty(10.0) # 10 seconds penalty
        self.assertGreaterEqual(timer.get_elapsed_time(), 10.0)
        self.assertEqual(timer.get_formatted_time()[:2], "00") # check minutes is 0
        
        timer.add_penalty(60.0) # add another 60 seconds
        self.assertGreaterEqual(timer.get_elapsed_time(), 70.0)
        self.assertEqual(timer.get_formatted_time(), "01:10") # 70 seconds -> 01:10 (assuming slight elapsed time < 80)

    def test_countdown_mode(self):
        timer = SudokuTimer(mode="countdown", duration_seconds=180) # 3 mins
        timer.start()
        self.assertLessEqual(timer.get_remaining_time(), 180.0)
        self.assertGreater(timer.get_remaining_time(), 179.0)
        self.assertEqual(timer.get_formatted_time(), "03:00")
        
        # Add 10 seconds penalty (reduces remaining time)
        timer.add_penalty(10.0)
        self.assertLessEqual(timer.get_remaining_time(), 170.0)
        self.assertEqual(timer.get_formatted_time(), "02:50")


class TestSudokuScoring(unittest.TestCase):
    def test_scoring(self):
        scoring = SudokuScoring(correct_points=10, incorrect_penalty=5)
        self.assertEqual(scoring.get_score(), 0)
        
        scoring.on_correct_move()
        self.assertEqual(scoring.get_score(), 10)
        self.assertEqual(scoring.correct_moves, 1)
        
        scoring.on_incorrect_move()
        self.assertEqual(scoring.get_score(), 5)
        self.assertEqual(scoring.get_errors(), 1)
        
        scoring.add_time_bonus(20, points_per_second=2)
        self.assertEqual(scoring.get_score(), 45) # 5 + 20 * 2 = 45


if __name__ == '__main__':
    unittest.main()
