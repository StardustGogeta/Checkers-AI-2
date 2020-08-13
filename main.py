import copy, random

RANDOMIZE = True
SEARCH_DEPTH = 3

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
            return -self.evaluate(W, turn)
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
def get_optimal_move(board, color = W, depth = SEARCH_DEPTH, alpha = None, beta = None):
    best_move = None
    alpha = -10**5 # Lower bound for acceptable scores
    beta = 10**5 # Upper bound for possible scores
    best_move, score = alphabeta_max(alpha, beta, color, board, depth, depth)
    color_name = {W: "white", B: "black"}[color]
    print(f"Best move for {color_name} is {best_move}\t\twith score of {score}")
    if not best_move and (moves := board.get_moves(color)):
        # Take the first available move if all lead to a loss
        return moves[0]
    return best_move

# Return player's best move and the evaluated score associated with it
# Uses alpha-beta decision tree pruning technique
def alphabeta_max(alpha, beta, color, board, depth = SEARCH_DEPTH, orig_depth = SEARCH_DEPTH):
    if not depth: # At depth of zero, simply return the board evaluation
        return board.evaluate(color, color)
    best_move = None
    toplevel = depth == orig_depth
    for move in board.get_moves(color, randomize = RANDOMIZE):
        # Make a new board with the hypothetical move
        test_board = board.copy()
        test_board.make_move(move)
        # Find the best score that the opponent could not prevent in this hypothetical
        score = alphabeta_min(alpha, beta, color, test_board, depth - 1, orig_depth)
        # If the best unpreventable score in this hypothetical is not the worst unpreventable score of all
        # hypotheticals, the opponent will avert it
        # Returns the lowest known unpreventable score of all hypotheticals
        if score >= beta:
            # print("beta cut", score, move)
            if toplevel: # Prevent breaking when the game is close to over
                return alphabeta_max(alpha, beta, color, board, depth - 1, depth - 1)
            return beta
        # If the move allows you to guarantee a higher score than you could before, then this is the new optimal move
        # Returns player's best move and the associated score
        if score > alpha:
            best_move, alpha = move, score
    if toplevel: # We are only interested in the move itself if we are at the top level of searching
        return best_move, alpha
    return alpha

# Alpha-beta pruning - auxiliary function
# Finds the best score that the opponent of `color` could not prevent
def alphabeta_min(alpha, beta, color, board, depth, orig_depth):
    if not depth: # No time for the opponent to prevent anything
        return board.evaluate(color, color)
    # Try to find the opponent's counterplay
    opp_color = W if color == B else B
    for move in board.get_moves(opp_color, randomize = RANDOMIZE):
        # Try the opponent's potential move
        test_board = board.copy()
        test_board.make_move(move)
        # Find the best score that the player can guarantee in this scenario
        score = alphabeta_max(alpha, beta, color, test_board, depth - 1, orig_depth)
        # If the player's best response to the opponent's counterplay provides less than the minimum acceptable score, it is not a viable path
        if score <= alpha:
            # print("alpha cut", score, move)
            return alpha
        # If the player's best response to the opponent's counterplay is worse than all other potential opponent moves, then this is the opponent's new best move
        # Returns the new highest unpreventable score
        if score < beta:
            beta = score
    return beta

def human_move_to_pairs(x):
    # Convert a4b5 to ((4, 0), (3, 1)) for example
    # The output is of the form ((y1, x1), (y2, x2))
    x1 = ord(x[0]) - ord('a')
    x2 = ord(x[2]) - ord('a')
    y1 = 8 - int(x[1])
    y2 = 8 - int(x[3])
    return ((y1, x1), (y2, x2))

def play_move(move, board, human_colors, color):
    if human_colors[color]: # Human player
        print(board)
        move = None
        while not move:
            try:
                move = [human_move_to_pairs(x) for x in input("Enter move (comma-separated steps): ").split(',')]
            except KeyboardInterrupt:
                exit()
            except:
                print("Please try again.")
        board.make_move(move)
    else: # Computer player
        board.make_move(move)
        print(board, '\n')
        #input("Press enter to continue...")

if __name__ == "__main__":
    print("Moves are entered as \"a4b5,b5c6\", etc.")
    b = Board()
    color = W
    human_colors = {W : False, B : False}
    while move := get_optimal_move(b, color, SEARCH_DEPTH):
        play_move(move, b, human_colors, color)
        color = B if color == W else W

    print("\n---------GAME OVER----------\n")
