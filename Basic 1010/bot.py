import numpy as np
import functions_and_objects as go


class Bot:
    def __init__(self, weight_distribution=(0.8, 0.5, 0.7)):
        # How many moves ahead the bot looks. This is dynamically adjusted during play.
        self.depth = 1

        # line-clearing, snugness, room for 3x3s
        self.weight_distribution = weight_distribution

        # the scores associated with placing a piece in a spot. Higher means better.
        self.line_score = 0
        self.snugness_score = 0
        self.room_score = 0

    def calculate_possible_moves(self, board, pieces):
        # Initialize a board
        move_array = np.zeros((len(pieces), 10, 10))
        original_room_heuristic = is_room_heuristic(board)

        for piece in range(len(pieces)):
            if pieces[piece].state != 2:
                for x_coord in range(10):
                    for y_coord in range(10):
                        # ----- TRIES MOVE
                        fake_board = np.copy(board)
                        fake_board, added_score = self.try_move(fake_board, pieces[piece], [x_coord, y_coord])

                        if added_score > 0:
                            # ----- SNUGNESS
                            snugness_board = np.copy(board)
                            snugness_board, garbage = go.place_piece(x_coord, y_coord, pieces[piece], snugness_board, place_value=2)
                            self.snugness_score = snug_fit_heuristic(snugness_board, pieces[piece], x_coord, y_coord) * self.weight_distribution[1]

                            # ----- EXTRA ROOM
                            # the worst possible move you could make is placing a 5-long piece and blocking off
                            # 21 potential 3x3 spaces. this way this score can never be negative.
                            # it is normalized so if nothing changes it is a score of 1
                            new_room_heuristic = is_room_heuristic(fake_board)
                            self.room_score = self.weight_distribution[2] * (21 + new_room_heuristic - original_room_heuristic)/21

                            # add all rewards
                            move_array[piece][y_coord][x_coord] += self.snugness_score + self.room_score + added_score

                        if len(pieces) > 4-self.depth and added_score > 0:
                            # piece was placed and the bot has not reached full depth, check 1 layer deeper
                            fake_pieces = np.copy(pieces)
                            fake_pieces = np.delete(fake_pieces, piece)
                            move_array[piece][y_coord][x_coord] += np.max(self.calculate_possible_moves(fake_board, fake_pieces))

        return move_array

    def make_move(self, board, pieces):
        """takes in game state and returns a piece and a square on the grid"""
        # copy the board and pieces to not accidentally modify them
        # NOT A DEEP COPY. modifying piece objects within fake pieces modifies the original pieces.
        fake_pieces = np.copy(pieces)
        fake_board = np.where(np.copy(board) > 0, 1, 0)  # Ensure all values are 1 on the board

        # Determine which depth the program should use given the situation
        direness = is_room_heuristic(fake_board)
        board_fullness = sum(fake_board.flatten()) / 100
        metric = board_fullness

        if metric < 0.25:
            self.depth = 1
        elif metric < 0.5:
            self.depth = 2
        else:
            self.depth = 3

        # try all possible moves and record in a big array
        move_array = self.calculate_possible_moves(fake_board, fake_pieces)
        best_move = select_best_move(move_array)

        return best_move

    def try_move(self, board, piece, square):
        """tests the result of placing a given piece (0-2) in a given square on the board and returns the score"""
        board, score = go.place_piece(square[0], square[1], piece, board)
        if score != 0:
            board, lines_cleared = go.clear_lines(board)
            self.line_score = lines_cleared * self.weight_distribution[0]
            score += self.line_score

        return board, score


def select_best_move(move_array):
    index = np.argmax(move_array)
    piece, x_coord, y_coord = index // 100, (index % 100) % 10, (index % 100) // 10  # extracts from flattened array

    return piece, x_coord, y_coord


def snug_fit_heuristic(board, piece, x_coord, y_coord):
    snugness = 0  # the number of neighbour pieces or board borders

    for piece_x_coord, piece_y_coord in piece.shape_blueprint:
        piece_x_coord += x_coord
        piece_y_coord += y_coord

        # consider changing how it values bordering pieces vs the edge of the map

        neighbour_squares = []
        if piece_y_coord - 1 >= 0:
            neighbour_squares.append(board[piece_y_coord - 1][piece_x_coord])
        else:
            neighbour_squares.append(1)
        if piece_y_coord + 1 <= 9:
            neighbour_squares.append(board[piece_y_coord + 1][piece_x_coord])
        else:
            neighbour_squares.append(1)
        if piece_x_coord - 1 >= 0:
            neighbour_squares.append(board[piece_y_coord][piece_x_coord - 1])
        else:
            neighbour_squares.append(1)
        if piece_x_coord + 1 <= 9:
            neighbour_squares.append(board[piece_y_coord][piece_x_coord + 1])
        else:
            neighbour_squares.append(1)

        neighbour_squares = [square for square in neighbour_squares if square != 2]

        snugness += sum(neighbour_squares)

    return snugness/piece.perimeter  # normalizes it so if its completely surrounded it returns 1


# CONSIDER MAKING THIS TEST THE NUMBER OF SLOTS FOR ANY PIECE NOT JUST 3x3s
def is_room_heuristic(board):
    """returns the number of 3x3 slots that exist on the board"""
    slot_count = 0

    for y_coord in range(8):
        x_adjustment = 0
        for x_coord in range(8):
            x_coord += x_adjustment
            if x_coord > 7:
                break

            works = True
            # checks that every square in the 3x3 can be placed on the board
            for shape_coord_x, shape_coord_y in [(2, 2), (1, 1), (0, 0), (2, 0), (0, 2), (2, 1), (1, 2), (1, 0), (0, 1)]:
                shape_coord_x += x_coord
                shape_coord_y += y_coord

                # if a square in the shape is taken, it can't be placed
                if board[shape_coord_y][shape_coord_x]:
                    works = False
                    x_adjustment = shape_coord_x
                    break

            # if it can be placed increment slot_count by 1
            if works:
                slot_count += 1

    return slot_count
