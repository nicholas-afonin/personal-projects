import pygame as py
import numpy as np
import random
import time
import functions_and_objects as go
import bot as bot_file

py.init()

"""--------------------------------------- TO-DO ---------------------------------------
- Settings and theme selection (also check if shapes have consistent colours or no)
- Game over screen
- Make bot button work slightly better
- Option to close window when game is over
- Make ability to test different bots side by side
- Fix probability of receiving pieces so there isn't a difference between non-rotateable pieces and rotateable pieces
- Create a version of the bot that switches between a filling and a clearing mode so it plays more efficiently
"""

"""--------------------------------------- GLOBAL VARIABLES ---------------------------------------"""

# WINDOW CONFIGURATION  -----------------------------------------------------------------------------
WINDOW_HEIGHT = 800  # probably don't change these :)
WINDOW_WIDTH = 500
WINDOW = py.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))  # object for actual window game is in
WINDOW_TITLE = "Nick's 1010"

# SHAPE AND COLOUR PROPERTIES -----------------------------------------------------------------------------
COLOUR_DICT = {
    1: (255, 92, 64),
    2: (230, 207, 80),
    3: (173, 230, 80),
    4: (84, 196, 86),
    5: (98, 217, 175),
    6: (98, 197, 217),
    7: (114, 116, 237),
    8: (169, 126, 230),
    9: (201, 126, 230),
    10: (230, 126, 225)}

# [0] = shape, [1] = margin, [2] = change in position when clicked, [3] = score when placed, [4] = colour number
# [5] = perimeter
SHAPE_DICT = {
    's': [[(0, 0)], 55, 10, 1, 1, 4],
    'dx': [[(0, 0), (1, 0)], 45, 20, 2, 2, 6],
    'dy': [[(0, 0), (0, 1)], 55, 10, 2, 2, 6],
    'sq': [[(0, 0), (1, 0), (0, 1), (1, 1)], 45, 20, 4, 3, 8],
    'v1': [[(0, 0), (0, 1), (1, 1)], 45, 20, 3, 4, 8],
    'v2': [[(0, 0), (1, 0), (0, 1)], 45, 20, 3, 4, 8],
    'v3': [[(0, 0), (1, 0), (1, 1)], 45, 20, 3, 4, 8],
    'v4': [[(1, 0), (0, 1), (1, 1)], 45, 20, 3, 4, 8],
    'tx': [[(1, 0), (0, 1), (1, 1)], 35, 30, 3, 5, 10],
    'ty': [[(1, 0), (0, 1), (1, 1)], 55, 10, 3, 5, 10],
    'bv1': [[(0, 0), (1, 0), (2, 0), (0, 1), (0, 2)], 35, 30, 5, 6, 12],
    'bv2': [[(0, 0), (1, 0), (2, 0), (2, 1), (2, 2)], 35, 30, 5, 6, 12],
    'bv3': [[(2, 0), (2, 1), (0, 2), (1, 2), (2, 2)], 35, 30, 5, 6, 12],
    'bv4': [[(0, 0), (0, 1), (0, 2), (1, 2), (2, 2)], 35, 30, 5, 6, 12],
    'frx': [[(0, 0), (1, 0), (2, 0), (3, 0)], 25, 40, 4, 7, 10],
    'fry': [[(0, 0), (0, 1), (0, 2), (0, 3)], 55, 10, 4, 7, 10],
    'fvx': [[(0, 0), (1, 0), (2, 0), (3, 0), (4, 0)], 15, 50, 5, 8, 12],
    'fvy': [[(0, 0), (0, 1), (0, 2), (0, 3), (0, 4)], 55, 10, 5, 8, 12],
    'bsq': [[(0, 0), (1, 0), (2, 0), (0, 1), (1, 1), (2, 1), (0, 2), (1, 2), (2, 2)], 35, 30, 9, 9, 12]}


# STATE VARIABLES AND SUCH -----------------------------------------------------------------------------
CLICKED_PIECE_INDEX = 0  # allows us to know which piece we're actively dealing with
SCORE = 0
MOUSE_X, MOUSE_Y = py.mouse.get_pos()
INITIAL_X, INITIAL_Y = 0, 0  # corresponds to mouse's coordinates when it's first clicked (allows to drag pieces)
BOARD = np.zeros((10, 10), dtype=int)  # 0 if empty, any other number indicates a colour
GAME_MODE = "player"

SCORE_LABEL = go.Text("Score: 0", 30, (100, 60), WINDOW)
HIGH_SCORE_LABEL = go.Text("High Score: 0", 30, (350, 60), WINDOW)
RESTART_BUTTON = go.Button("restart", 20, (130, 720), WINDOW)
BOT_BUTTON = go.Button("enable bot", 20, (320, 720), WINDOW)
PIECES = [go.Piece(i, WINDOW, SHAPE_DICT, COLOUR_DICT) for i in range(3)]  # Defines 3 piece objects

DATA_FILE = "Data.txt"


"""---------------------------------------FUNCTIONS---------------------------------------"""
def visuals():
    """refreshes all visuals on the screen"""
    WINDOW.fill(py.Color("black"))

    go.fill_squares(BOARD, COLOUR_DICT, WINDOW)
    go.draw_grid(WINDOW, WINDOW_WIDTH)
    SCORE_LABEL.draw()
    HIGH_SCORE_LABEL.draw()
    RESTART_BUTTON.draw()
    if GAME_MODE == "player":
        BOT_BUTTON.draw()
    for unplaced_piece in PIECES:
        unplaced_piece.draw(MOUSE_X, MOUSE_Y, INITIAL_X, INITIAL_Y)

    py.display.flip()


def mouse_clicked():
    global CLICKED_PIECE_INDEX, INITIAL_X, INITIAL_Y

    INITIAL_X, INITIAL_Y = MOUSE_X, MOUSE_Y  # logs location where mouse was first pressed
    CLICKED_PIECE_INDEX = (MOUSE_X - 50) // 130  # determines which piece was clicked (if any were)
    # changes the piece's state to being clicked if mouse is in correct range
    if 0 <= CLICKED_PIECE_INDEX <= 2 and 500 <= MOUSE_Y <= 700 and PIECES[CLICKED_PIECE_INDEX].state != 2:
        PIECES[CLICKED_PIECE_INDEX].state = 1
    else:
        CLICKED_PIECE_INDEX = -1  # if no piece was clicked, then index is -1

    # considers restart button clicked if it was being hovered over
    if RESTART_BUTTON.state != 0:
        return True
    if BOT_BUTTON.state != 0:
        global GAME_MODE
        GAME_MODE = "bot"

    # returns true for button_pressed and returns the state of the reset button
    return False


def mouse_released():
    global BOARD, SCORE
    piece = PIECES[CLICKED_PIECE_INDEX]
    if piece.state != 2 and CLICKED_PIECE_INDEX != -1:  # if the piece is not yet placed

        # converts piece's pixel coordinates (position_on_grid) to grid coordinates (x_coord, y_coord)
        position_on_grid = piece.coordinates
        x_coord = (position_on_grid[0] + 19 - 50) // 40
        y_coord = (position_on_grid[1] + 19 - 100) // 40

        # if both coordinates are actually in the grid, then trigger place_piece() function
        if 0 <= x_coord <= 9 and 0 <= y_coord <= 9:
            BOARD, piece.state = go.place_piece(x_coord, y_coord, piece, BOARD, piece.colour, 2)

            if piece.state == 2:
                SCORE += piece.score

            # Checks if the player completed a horizontal or vertical line and eliminates it if so
            BOARD, lines_cleared = go.clear_lines(BOARD)
            SCORE += 0.5 * (lines_cleared**2 + lines_cleared)
            SCORE_LABEL.update("Score: " + str(int(SCORE)))

        # If it is not in the grid, just snap back to og spot
        else:
            piece.state = 0


# option 1 = immediately resets game (good for bot), option 2 = game over screen that needs restart_button to be pressed
def handle_game_over(pieces, option=1):
    """handles what happens when the game ends, based on needs."""
    if option == 1:
        reset_game(pieces)


def get_high_score():
    """gets high score from data.txt file"""
    try:
        with open(DATA_FILE, 'r') as f:
            high_score = f.read()
        f.close()
        return int(high_score)
    except FileNotFoundError:
        with open(DATA_FILE, 'w') as f:
            f.write("0")
        f.close()
        return 0


def check_high_score(reset_score=True):
    """checks if high score needs to be updated and updates it if necessary"""
    global SCORE
    high_score = get_high_score()

    if high_score < SCORE:
        with open(DATA_FILE, 'w') as f:
            f.write(str(SCORE))
        f.close()  # closes file

    if reset_score:
        SCORE = 0  # resets score

    SCORE_LABEL.update("Score: " + str(SCORE))  # impatiently updates score_label to be 0 so that it's not lagging
    HIGH_SCORE_LABEL.update("High Score: " + str(high_score))  # updates high score label to show new high score


def reset_game(piece_list):
    global BOARD
    BOARD = np.zeros((10, 10), dtype=int)
    go.reset_pieces(piece_list, force=True)
    check_high_score()


def run_bot(mybot):
    """argument is the bot class that you want to use. It must have the associated function mybot.make_move"""
    global CLICKED_PIECE_INDEX, BOARD, SCORE
    CLICKED_PIECE_INDEX, x_coord, y_coord = mybot.make_move(BOARD, PIECES)  # gets move from bot

    piece = PIECES[CLICKED_PIECE_INDEX]

    # if the piece is valid, try to place it
    if 0 <= CLICKED_PIECE_INDEX <= 2 and piece.state != 2:
        BOARD, piece.state = go.place_piece(x_coord, y_coord, piece, BOARD, place_value=piece.colour, return_value=2)

        if piece.state == 2:
            SCORE += piece.score

        # if successfully placed, check to see if it cleared any lines
        if piece.state == 2:
            BOARD, lines_cleared = go.clear_lines(BOARD)
            SCORE += 0.5 * (lines_cleared ** 2 + lines_cleared)
            SCORE_LABEL.update("Score: " + str(int(SCORE)))

    else:
        print("invalid move: piece already placed or nonexistent")
        CLICKED_PIECE_INDEX = -1  # if no piece was clicked, then index is -1


def main(bot_selection=False, rounds=1):
    global GAME_MODE, MOUSE_X, MOUSE_Y
    reset_button_pressed = False
    mouse_pressed = False
    check_high_score()
    py.display.set_caption(WINDOW_TITLE)

    running = True
    round_count = 0
    all_scores = []
    while running and round_count < rounds:
        MOUSE_X, MOUSE_Y = py.mouse.get_pos()

        for event in py.event.get():
            if event.type == py.QUIT:
                running = False
            if event.type == py.MOUSEBUTTONDOWN:
                GAME_MODE = "player"
                mouse_pressed = True
                reset_button_pressed = mouse_clicked()

            if event.type == py.MOUSEBUTTONUP:
                mouse_pressed = False
                mouse_released()

        # Runs the bot
        if GAME_MODE == "bot":
            # time.sleep(0.01)  # delay so you can watch the bot
            run_bot(bot_selection)

        # Checks if there are pieces still left. Resets and adds new ones if no.
        go.reset_pieces(PIECES)

        # Checks if game is over (whether through reset or other). If so, handles game over.
        game_over = go.check_game_over(PIECES, BOARD)

        if not running or game_over or reset_button_pressed:
            all_scores.append(SCORE)
            round_count += 1
            print(SCORE)
            check_high_score(reset_score=True)

            if reset_button_pressed:
                reset_button_pressed = False
                reset_game(PIECES)
            elif game_over:
                handle_game_over(PIECES)
            else:
                running = False

        # Draws all visuals
        visuals()
        RESTART_BUTTON.update(mouse_pressed, MOUSE_X, MOUSE_Y)
        BOT_BUTTON.update(mouse_pressed, MOUSE_X, MOUSE_Y)

    return np.median(np.array(all_scores)), max(all_scores), min(all_scores)


if __name__ == "__main__":
    bot = bot_file.Bot()  # create bot object
    median, max_score, min_score = main(bot, 100)  # need to pass a bot object to main, nothing else

    py.quit()
