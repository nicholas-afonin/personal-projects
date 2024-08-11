import numpy as np
import time


class Bot:
    def __init__(self, depth=1, weight_distribution=(1, 0.5, 0.5, 1, 1)):
        self.depth = depth

        # line-clearing, black-blobs, piece-blobs, snugness, room for 3x3s
        self.weight_distribution = weight_distribution

        self.line_score = 0
        self.blob_score = 0
        self.snugness_score = 0
        self.room_score = 0

        self.processing_times = [0, 0, 0, 0, 0]
        # attempt, blob, snugness, room, overall

        self.moves_done = 0

        self.direness = 64

    def output_time_breakdown(self):
        # print(self.processing_times)
        total = self.processing_times[4]
        print("Attempt:", round(100 * self.processing_times[0] / total, 1), "%")
        print("Blobs:", round(100 * self.processing_times[1] / total, 1), "%")
        print("Snugness:", round(100 * self.processing_times[2] / total, 1), "%")
        print("Room:", round(100 * self.processing_times[3] / total, 1), "%")
        print("Unaccounted:", round(100*(1-sum(self.processing_times[0:4])/total), 1), "%")
        print("Time per move:", round(total / self.moves_done / 10**5, 2), "milliseconds")

    def calculate_possible_moves(self, board, pieces):
        move_array = np.zeros((len(pieces), 10, 10))
        for piece in range(len(pieces)):
            if pieces[piece].state != 2:
                for x_coord in range(10):
                    for y_coord in range(10):
                        start = time.time_ns()
                        # ----- TRIES MOVE
                        fake_board = np.copy(board)
                        fake_board, added_score = self.try_move(fake_board, pieces[piece], [x_coord, y_coord])

                        try_time = time.time_ns() - start

                        if added_score > 0:
                            start = time.time_ns()
                            # ----- BLOBS
                            # original_blob_heuristic = self.blob_heuristic(board)
                            # new_blob_heuristic = self.blob_heuristic(np.copy(fake_board))
                            # self.blob_score = (2 + original_blob_heuristic - new_blob_heuristic)*0.5
                            self.blob_score = 0

                            blob_time = time.time_ns() - start

                            start = time.time_ns()
                            # ----- SNUGNESS
                            snugness_board = np.copy(board)
                            snugness_board, garbage = place_piece(x_coord, y_coord, pieces[piece], snugness_board, place_value=2)
                            self.snugness_score = snug_fit_heuristic(snugness_board, pieces[piece], x_coord, y_coord) * self.weight_distribution[3]

                            snugness_time = time.time_ns() - start

                            start = time.time_ns()
                            # ----- EXTRA ROOM
                            original_room_heuristic = is_room_heuristic(board)
                            new_room_heuristic = is_room_heuristic(fake_board)

                            self.room_score = self.weight_distribution[4] * (21 + new_room_heuristic - original_room_heuristic)/21
                            # the worst possible move you could make is placing a 5-long piece and blocking off
                            # 21 potential 3x3 spaces. this way this score can never be negative.
                            # it is normalized so if nothing changes it is a score of 1

                            room_time = time.time_ns() - start

                            move_array[piece][y_coord][x_coord] += (self.blob_score + self.snugness_score +
                                                                    self.room_score + added_score)
                            # print([self.line_score, self.blob_score, round(self.snugness_score, 2), round(self.room_score, 2)])

                            time_breakdown = [try_time, blob_time, snugness_time, room_time, 0]

                            self.processing_times = np.add(self.processing_times, time_breakdown)
                        else:
                            self.processing_times = np.add(self.processing_times, [try_time, 0, 0, 0, 0])

                        if len(pieces) > 4-self.depth and added_score > 0:
                            fake_pieces = np.copy(pieces)
                            fake_pieces = np.delete(fake_pieces, piece)
                            move_array[piece][y_coord][x_coord] += np.max(self.calculate_possible_moves(fake_board, fake_pieces))

        return move_array

    def make_move(self, board, pieces):
        """takes in game state and returns a piece and a square on the grid"""
        # copy the board and pieces to not accidentally modify them
        # NOT A DEEP COPY. modifying piece objects within fake pieces modifies the original pieces.
        fake_board = np.copy(board)
        fake_pieces = np.copy(pieces)

        fake_board = np.where(fake_board > 0, 1, 0)  # Ensure all values are 1 on the board

        self.direness = is_room_heuristic(fake_board)
        board_fullness = sum(fake_board.flatten()) / 100

        metric = board_fullness

        if metric < 0.15:
            self.depth = 1
        elif metric < 0.5:
            self.depth = 2
        else:
            self.depth = 3

        # try all possible moves and record in a big array
        start = time.time_ns()
        move_array = self.calculate_possible_moves(fake_board, fake_pieces)
        self.processing_times = np.add(self.processing_times, [0, 0, 0, 0, time.time_ns()-start])

        best_move = select_best_move(move_array)

        self.moves_done += 1

        return best_move

    def blob_heuristic(self, board):
        """returns a value indicating how many piece blobs and black blobs are on the grid (weights applied)"""
        fake_board = np.copy(board)
        fake_board_reverse = np.invert(np.array(fake_board, dtype=bool))
        fake_board_reverse = np.array(fake_board_reverse, dtype=int)
        # down the line it might be faster to change how the blob counter works

        piece_blobs = blob_counter(fake_board)
        black_blobs = blob_counter(fake_board_reverse)

        return piece_blobs * self.weight_distribution[2] + black_blobs * self.weight_distribution[1]

    def try_move(self, board, piece, square):
        """tests the result of placing a given piece (0-2) in a given square on the board and returns the score"""
        board, score = place_piece(square[0], square[1], piece, board)
        if score != 0:
            board, lines_cleared = check_lines(board)
            self.line_score = lines_cleared * self.weight_distribution[0]
            score += self.line_score

        return board, score


def place_piece(x_coord, y_coord, piece, board, place_value=1):
    # pulls up every square in shape blueprint and adjusts it to be in its actual position on the grid
    for shape_coord_x, shape_coord_y in piece.shape_blueprint:
        shape_coord_x += x_coord
        shape_coord_y += y_coord

        # if position of these squares is out of bounds or unavailable, cancels the whole thing
        if not (0 <= shape_coord_x <= 9 and 0 <= shape_coord_y <= 9 and not board[shape_coord_y][shape_coord_x]):
            return board, 0

    # if all squares are in bounds and valid, updates the board
    for shape_coord_x, shape_coord_y in piece.shape_blueprint:
        shape_coord_x += x_coord
        shape_coord_y += y_coord
        board[shape_coord_y][shape_coord_x] = place_value

    return board, 1
    # instead of 1 could be piece score, but I don't see any inherent value to that


def check_lines(board):
    """sees if lines need to be eliminated (full line gets bonked)"""
    # initializes lists for which lines are cleared. if none then these remain empty
    horizontal_clears = []
    vertical_clears = []

    # Checks for full horizontal lines
    for y_coord in range(10):
        if 0 not in board[y_coord]:
            horizontal_clears.append(y_coord)

    # Checks for full vertical lines
    swapped_axes = np.swapaxes(board, 0, 1)
    for x_coord in range(10):
        if 0 not in swapped_axes[x_coord]:
            vertical_clears.append(x_coord)

    # clears lines that are full
    for y_coord in horizontal_clears:
        board[y_coord][0:10] = 0
    for x_coord in vertical_clears:
        board[0:10][x_coord] = 0

    lines_cleared = len(horizontal_clears) + len(vertical_clears)

    return board, 0.5*(lines_cleared**2 + lines_cleared)


def blob_counter(board):
    """I stole this from chatgpt. Seems to work"""
    visited = [[False for _ in range(len(board[0]))] for _ in range(len(board))]
    blobs = 0

    for i in range(len(board)):
        for j in range(len(board[0])):
            if board[i][j] == 1 and not visited[i][j]:
                # New blob found
                flood_fill(board, i, j, visited)
                blobs += 1

    return blobs


def flood_fill(grid, x, y, visited):
    """I stole this from chatgpt. Seems to work"""
    # Check if x, y is out of bounds or already visited or empty
    if x < 0 or x >= len(grid) or y < 0 or y >= len(grid[0]) or visited[x][y] or grid[x][y] == 0:
        return

    # Mark the cell as visited
    visited[x][y] = True

    # Recursively fill adjacent cells
    flood_fill(grid, x + 1, y, visited)
    flood_fill(grid, x - 1, y, visited)
    flood_fill(grid, x, y + 1, visited)
    flood_fill(grid, x, y - 1, visited)


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
