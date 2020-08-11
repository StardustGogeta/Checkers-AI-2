import copy, random

# These are constant values for storing and handling board data
W = 1
B = 2
W_KING = 11
B_KING = 12

class Board:
    # The board is encoded as 0 for empty spaces, 1 for white, 2 for black
    # For kings, 11 for white king and 12 for black king
    # Note that white goes bottom to top, black goes top to bottom

    start_board = [
        [0, B, 0, B, 0, B, 0, B],
        [B, 0, B, 0, B, 0, B, 0],
        [0, B, 0, B, 0, B, 0, B],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [W, 0, W, 0, W, 0, W, 0],
        [0, W, 0, W, 0, W, 0, W],
        [W, 0, W, 0, W, 0, W, 0]
    ]

    def __init__(self, arr = start_board):
        self.arr = arr

    # Counts all pieces of a certain color
    def piece_value(self, color = W, king_val = 5):
        if color == W:
            return sum(row.count(W) + row.count(W_KING) * king_val for row in self.arr)
        else:
            return sum(row.count(B) + row.count(B_KING) * king_val for row in self.arr)

    # Counts how many more pieces one color has over the other
    def net_piece_value(self, color = W, king_val = 5):
        return self.piece_value(color, king_val) - self.piece_value(B if color == W else W, king_val)

    # Returns a list of lists of pairs of coordinate pairs
    # Coordinate pair = Position
    # Pair of coordinate pairs = Step
    # List of pairs of pairs = Move
    # List of lists of pairs of pairs = List of moves
    # This allows for complex king move sequences to be described
    # ex) [[((6, 1), (5, 2))], [((5, 0), (4, 1))]]
    def get_moves(self, color = W, *, randomize = False):
        ret = []
        pieces_to_find = [W, W_KING] if color == W else [B, B_KING]
        for y, row in enumerate(self.arr):
            for x, piece in enumerate(row):
                if piece in pieces_to_find:
                    ret.extend(self.get_piece_moves(y, x, piece))
        if randomize:
            random.shuffle(ret)
        return ret

    # Returns a list of lists of pairs of coordinate pairs for a single piece on the board
    def get_piece_moves(self, y, x, piece = None, must_jump = False, prev_captures = []):
        # must_jump is used to ensure that a piece only jumps after it jumps at least once
        # prev_moves is used to make sure that a king does not capture the same piece twice in one turn
        # TODO: Further reduce code duplication in move generation
        # TODO: Allow option for making jumping mandatory whenever possible - requires not adding partial move if there exist further moves, etc.
        if piece is None:
            piece = self.arr[y][x]
        pos = (y, x)
        opp = [B, B_KING] if piece in [W, W_KING] else [W, W_KING] # Opponent pieces
        ret = []
        if piece in [W, W_KING, B_KING]:
            # White moves from bottom to top of array
            if not must_jump:
                # No jump
                if x > 0 and y > 0 and not self.arr[y-1][x-1]:
                    ret.append([(pos, (y-1, x-1))])
                if x < 7 and y > 0 and not self.arr[y-1][x+1]:
                    ret.append([(pos, (y-1, x+1))])
            if x > 1 and y > 1 and self.arr[y-1][x-1] in opp and (y-1, x-1) not in prev_captures and not self.arr[y-2][x-2]:
                partial_move = [(pos, (y-2, x-2))]
                ret.append(partial_move)
                for move in self.get_piece_moves(y-2, x-2, piece, True, prev_captures + [(y-1, x-1)]):
                    full_move = partial_move + move
                    ret.append(full_move)
            if x < 6 and y > 1 and self.arr[y-1][x+1] in opp and (y-1, x+1) not in prev_captures and not self.arr[y-2][x+2]:
                partial_move = [(pos, (y-2, x+2))]
                ret.append(partial_move)
                for move in self.get_piece_moves(y-2, x+2, piece, True, prev_captures + [(y-1, x+1)]):
                    full_move = partial_move + move
                    ret.append(full_move)
        if piece in [B, W_KING, B_KING]:
            # Black moves from top to bottom of array
            if not must_jump:
                # No jump
                if x > 0 and y < 7 and not self.arr[y+1][x-1]:
                    ret.append([(pos, (y+1, x-1))])
                if x < 7 and y < 7 and not self.arr[y+1][x+1]:
                    ret.append([(pos, (y+1, x+1))])
            if x > 1 and y < 6 and self.arr[y+1][x-1] in opp and (y+1, x-1) not in prev_captures and not self.arr[y+2][x-2]:
                partial_move = [(pos, (y+2, x-2))]
                ret.append(partial_move)
                for move in self.get_piece_moves(y+2, x-2, piece, True, prev_captures + [(y+1, x-1)]):
                    full_move = partial_move + move
                    ret.append(full_move)
            if x < 6 and y < 6 and self.arr[y+1][x+1] in opp and (y+1, x+1) not in prev_captures and not self.arr[y+2][x+2]:
                partial_move = [(pos, (y+2, x+2))]
                ret.append(partial_move)
                for move in self.get_piece_moves(y+2, x+2, piece, True, prev_captures + [(y+1, x+1)]):
                    full_move = partial_move + move
                    ret.append(full_move)
        return ret

    # Play a move on the board
    # Moves are lists of pairs of positions to move between
    def make_move(self, move):
        for pos1, pos2 in move:
            if abs(pos1[0] - pos2[0]) == 2:
                # Jump move
                mid = ((pos1[0] + pos2[0]) // 2, (pos1[1] + pos2[1]) // 2)
                self.arr[mid[0]][mid[1]] = 0
            self.arr[pos2[0]][pos2[1]] = self.arr[pos1[0]][pos1[1]]
            self.arr[pos1[0]][pos1[1]] = 0
        # Auto-convert any pieces on the last row to kings
        self.arr[0] = [W_KING if x == W else x for x in self.arr[0]]
        self.arr[7] = [B_KING if x == B else x for x in self.arr[7]]

    # Convert a row from numbers to characters
    def __stringify_row(self, row):
        conv = {W: "w", B: "b", W_KING: "W", B_KING: "B", 0: "_"}
        return [conv[x] for x in row]

    # Pretty-print the current board
    def __str__(self):
        # return '\n'.join(str(self.__stringify_row(row)) for row in self.arr)
        return '\n'.join(' '.join(self.__stringify_row(row)) for row in self.arr)

    # Produce and return a deep copy of the board
    def copy(self):
        return Board(copy.deepcopy(self.arr))

    # Return a static evaluation of the board position based on piece count and position
    def evaluate(self, color = W, turn = W, king_val = 5):
        if color != W:
            # Black's score is just the opposite of white's
            return -self.evaluate(W)
        # def row_end_val(row):
            # conv = {W: 1, B: -1, W_KING: W * king_val, B_KING: B * king_val, 0: 0}
            # print("ROW:", row, self.arr)
            # return conv[row[0]] + conv[row[7]]
        # edge_piece_val = sum(row_end_val(row) for row in self.arr)
        available_moves = self.get_moves(turn)
        # If a player can't move, they lose
        if not available_moves:
            return -1000 if turn == color else 1000
        return self.net_piece_value()# + edge_piece_val

# Return the optimal move for a certain color in a given position
def get_optimal_move(board, color = W, depth = 3, alpha = None, beta = None):
    best_move = None
    alpha = -10**5 # Lower bound for acceptable scores
    beta = 10**5 # Upper bound for possible scores
    best_move, score = alphabeta_max(alpha, beta, color, board)
    print(f"Best move is {best_move}\t\twith score of {score}")
    return best_move

# Return best move and the evaluated score associated with it
# Uses alpha-beta decision tree pruning technique
def alphabeta_max(alpha, beta, color, board, depth = 3):
    if not depth:
        return [None, board.evaluate(color, color)]
    best_move = None
    for move in board.get_moves(color, randomize = True):
        test_board = board.copy()
        test_board.make_move(move)
        beta_move, score = alphabeta_min(alpha, beta, color, test_board, depth - 1)
        if score >= beta:
            # print("beta cut", score, move)
            return beta_move, beta
        if score > alpha:
            best_move, alpha = move, score
    return best_move, alpha

# Alpha-beta pruning - auxiliary function
def alphabeta_min(alpha, beta, color, board, depth = 3):
    if not depth:
        return [None, board.evaluate(color, color)]
    best_move = None
    for move in board.get_moves(B if color == W else W, randomize = True):
        test_board = board.copy()
        test_board.make_move(move)
        alpha_move, score = alphabeta_max(alpha, beta, color, test_board, depth - 1)
        if score <= alpha:
            # print("alpha cut", score, move)
            return alpha_move, alpha
        if score < beta:
            best_move, beta = move, score
    return best_move, beta

if __name__ == "__main__":
    b = Board()
    # print(b)
    # m = b.get_moves()
    # print("MOVES", m, m[2])
    # b.make_move(m[2])
    # print(b)
    color = W
    while move := get_optimal_move(b, color):
        color = B if color == W else W
        b.make_move(move)
        print(b, '\n')
        input()

    print("\n---------GAME OVER----------\n")
