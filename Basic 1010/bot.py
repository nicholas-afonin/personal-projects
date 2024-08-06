import numpy as np


class Bot:
    def __init__(self, depth=1):
        self.depth = depth

    def populate_move_array(self, board, pieces):
        move_array = np.zeros((3, 10, 10))
        for piece in range(3):
            for x_coord in range(10):
                for y_coord in range(10):
                    if pieces[piece].state == 2:
                        move_array[piece][x_coord][y_coord] = -1
                    else:
                        fake_board = np.copy(board)
                        move_array[piece][x_coord][y_coord] = try_move(fake_board, pieces[piece], [x_coord, y_coord])

        return move_array

    def make_move(self, board, pieces):
        """takes in game state and returns a piece and a square on the grid"""
        # try all possible moves and record in a big array
        fake_board = np.copy(board)
        fake_pieces = np.copy(pieces)
        move_array = self.populate_move_array(fake_board, fake_pieces)
        index = np.argmax(move_array)
        piece, x_coord, y_coord = index // 100, (index % 100) % 10, (index % 100) // 10

        return piece, x_coord, y_coord


def try_move(board, piece, square):
    """tests the result of placing a given piece (0-2) in a given square on the board and returns the score"""
    score = 0
    board, score = place_piece(square[0], square[1], piece, board)
    if score != 0:
        board, add = check_lines(board)
        score += add

    return score


def place_piece(x_coord, y_coord, piece, board):
    # pulls up every square in shape blueprint and adjusts it to be in its actual position on the grid
    for shape_coord_x, shape_coord_y in piece.shape_blueprint:
        shape_coord_x += x_coord
        shape_coord_y += y_coord

        # if position of these squares is out of bounds or unavailable, cancels the whole thing
        if not(0 <= shape_coord_x <= 9 and 0 <= shape_coord_y <= 9 and not board[shape_coord_x][shape_coord_y]):
            return board, 0

    # if not cancelled, switches all squares in blueprint to the correct colour (after adjusting in same way as above)
    for shape_coord_x, shape_coord_y in piece.shape_blueprint:
        shape_coord_x += x_coord
        shape_coord_y += y_coord
        board[shape_coord_x][shape_coord_y] = piece.colour

    return board, piece.score


def check_lines(board):
    """sees if lines need to be eliminated (full line gets bonked)"""
    # initializes lists for which lines are cleared. if none then these remain empty
    x_cleared = []
    y_cleared = []

    # Checks for full horizontal lines
    for line in range(10):
        cleared = True
        for square in range(10):
            if not board[line][square]:
                cleared = False
        if cleared:
            x_cleared.append(line)

    # Checks for full vertical lines
    for line in range(10):
        cleared = True
        for square in range(10):
            if not board[square][line]:
                cleared = False
        if cleared:
            y_cleared.append(line)

    # actually clears the lines that were confirmed clear when checked (x) and adjusts score
    for line in x_cleared:
        for square in range(10):
            board[line][square] = False
        return board, 10

    # actually clears vertical lines and adjusts score
    for line in y_cleared:
        for square in range(10):
            board[square][line] = False
        return board, 10

    return board, 0
