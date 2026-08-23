import time


class SudokuMatch:
    """Quản lý trận đấu Sudoku 2 người chơi."""

    def __init__(self, board, players, time_limit=180):
        self.board = [list(row) for row in board]
        self.players = list(players)
        self.time_limit = int(time_limit)
        self.turn = 0
        self.finished = False
        self.winner = None
        self.scores = {player: 0 for player in self.players}
        self.remaining_time = {player: self.time_limit for player in self.players}
        self.history = []
        self.last_turn_started = time.monotonic()

    @property
    def current_player(self):
        if not self.players:
            return None
        return self.players[self.turn % len(self.players)]

    def _other_player(self, player):
        for p in self.players:
            if p != player:
                return p
        return player

    def valid_move(self, row, col, value):
        if not (0 <= row < 9 and 0 <= col < 9):
            return False
        if value < 1 or value > 9:
            return False
        if self.board[row][col] != 0:
            return False

        for i in range(9):
            if self.board[row][i] == value:
                return False
            if self.board[i][col] == value:
                return False

        start_row = (row // 3) * 3
        start_col = (col // 3) * 3
        for r in range(start_row, start_row + 3):
            for c in range(start_col, start_col + 3):
                if self.board[r][c] == value:
                    return False
        return True

    def finish_if_complete(self, player=None):
        if not any(0 in row for row in self.board):
            self.finished = True
            self.winner = player if player is not None else self.current_player
            return self.winner
        return None

    def apply_move(self, player, row, col, value):
        if self.finished:
            return False
        if player != self.current_player:
            return False

        row = int(row)
        col = int(col)
        value = int(value)

        if not self.valid_move(row, col, value):
            return False

        self.board[row][col] = value
        self.scores[player] += 10
        self.history.append({
            "player": player,
            "row": row,
            "col": col,
            "value": value,
        })

        if self.finish_if_complete(player) is not None:
            self.last_turn_started = time.monotonic()
            return True

        self.turn = (self.turn + 1) % len(self.players)
        self.last_turn_started = time.monotonic()
        return True

    def tick_time(self, elapsed=1):
        if self.finished:
            return None

        current = self.current_player
        if current is None:
            return None

        self.remaining_time[current] = max(0, self.remaining_time.get(current, self.time_limit) - elapsed)

        if self.remaining_time[current] <= 0:
            self.finished = True
            self.winner = self._other_player(current)
            return self.winner

        return None

    def serialize_board(self):
        return "|".join(",".join(str(v) for v in row) for row in self.board)

    @staticmethod
    def deserialize_board(data):
        rows = []
        for row_data in data.split("|"):
            row = [int(v) for v in row_data.split(",")]
            rows.append(row)
        return rows
