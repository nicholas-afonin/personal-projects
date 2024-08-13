import pygame as py
import numpy as np
import random
import time
import game_objects as go
import bot as bot_file

py.init()

"""--------------------------------------- TO-DO ---------------------------------------
- Settings and theme selection (also check if shapes have consistent colours or no)
- Game over screen
- Make bot button work slightly better
- Option to close window when game is over
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


def draw_grid():
    grid_scale = 100  # any value from 0 to 100
    grid_width = grid_scale * 0.01 * (0.8 * WINDOW_WIDTH)
    grid_margins = (WINDOW_WIDTH - grid_width) / 2

    # DRAWS GRID --> get rid of all the bullshit and just use numbers lol, make the code work first
    for line in range(9):
        py.draw.line(WINDOW, py.Color("gray"), (grid_margins + grid_width/10 + line*(grid_width/10), grid_margins*2), (grid_margins + grid_width/10 + line*(grid_width/10), (grid_margins*2)+grid_width-1))
    for line in range(9):
        py.draw.line(WINDOW, py.Color("gray"), (grid_margins, grid_margins*2 + grid_width/10 + line * grid_width/10), (grid_width + grid_margins, grid_margins*2 + grid_width/10 + line * grid_width/10))
    py.draw.rect(WINDOW, py.Color("white"), (grid_margins, grid_margins*2, grid_width, grid_width), width=2)


def fill_squares():
    """draws squares in grid with appropriate colours based on SQUARE_GRID"""
    for y_coord in range(10):
        for x_coord in range(10):
            if BOARD[y_coord][x_coord] != 0:
                py.draw.rect(WINDOW, py.Color(COLOUR_DICT[int(BOARD[y_coord][x_coord])]), (52 + x_coord * 40, 102 + y_coord * 40, 37, 37), width=0)


def visuals():
    """refreshes all visuals on the screen"""
    WINDOW.fill(py.Color("black"))

    fill_squares()
    draw_grid()
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
    if PIECES[CLICKED_PIECE_INDEX].state != 2 and CLICKED_PIECE_INDEX != -1:  # if the piece is not yet placed

        # converts piece's pixel coordinates (position_on_grid) to grid coordinates (x_coord, y_coord)
        position_on_grid = PIECES[CLICKED_PIECE_INDEX].coordinates
        x_coord = (position_on_grid[0] + 19 - 50) // 40
        y_coord = (position_on_grid[1] + 19 - 100) // 40

        # if both coordinates are actually in the grid, then trigger place_piece() function
        if 0 <= x_coord <= 9 and 0 <= y_coord <= 9:
            PIECES[CLICKED_PIECE_INDEX].state = place_piece(x_coord, y_coord)

            # Checks if the player completed a horizontal or vertical line and eliminates it if so
            check_lines()

        # If it is not in the grid, just snap back to og spot
        else:
            PIECES[CLICKED_PIECE_INDEX].state = 0


def place_piece(x_coord, y_coord, bot=False):  # bot argument is true when bot is testing positions
    global SCORE
    # pulls up every square in shape blueprint and adjusts it to be in its actual position on the grid
    for shape_coord_x, shape_coord_y in PIECES[CLICKED_PIECE_INDEX].shape_blueprint:
        shape_coord_x += x_coord
        shape_coord_y += y_coord

        # if position of these squares is out of bounds or unavailable, cancels the whole thing
        if not(0 <= shape_coord_x <= 9 and 0 <= shape_coord_y <= 9 and not BOARD[shape_coord_y][shape_coord_x]):
            return 0  # returns state = 0, so piece snaps back to passive position

    # figure out what this is about later
    if not bot:
        # if not cancelled, switches all squares in blueprint to the correct colour (after adjusting in same way as above)
        for shape_coord_x, shape_coord_y in PIECES[CLICKED_PIECE_INDEX].shape_blueprint:
            shape_coord_x += x_coord
            shape_coord_y += y_coord
            BOARD[shape_coord_y][shape_coord_x] = PIECES[CLICKED_PIECE_INDEX].colour

        SCORE += PIECES[CLICKED_PIECE_INDEX].score  # Updates game score

    return 2  # returns state = 2, so piece is now considered placed


def check_lines():
    """sees if lines need to be eliminated (full line gets bonked)"""
    global SCORE

    # initializes lists for which lines are cleared. if none then these remain empty
    horizontal_clears = []
    vertical_clears = []

    # Checks for full horizontal lines
    for y_coord in range(10):
        if 0 not in BOARD[y_coord]:
            horizontal_clears.append(y_coord)

    # Checks for full vertical lines
    swapped_axes = np.swapaxes(BOARD, 0, 1)
    for x_coord in range(10):
        if 0 not in swapped_axes[x_coord]:
            vertical_clears.append(x_coord)

    # actually clears the lines that were confirmed clear when checked (x) and adjusts score
    for y_coord in horizontal_clears:
        for x_coord in range(10):
            BOARD[y_coord][x_coord] = 0
            visuals()
            time.sleep(0.01)

    # actually clears vertical lines and adjusts score
    for x_coord in vertical_clears:
        for y_coord in range(10):
            BOARD[y_coord][x_coord] = 0
            visuals()
            time.sleep(0.01)

    lines_cleared = len(vertical_clears) + len(horizontal_clears)

    SCORE += 5 * (lines_cleared**2 + lines_cleared)
    # updates score label --> conveniently placed after pieces placed and after line clears
    SCORE_LABEL.update("Score: " + str(SCORE))


def reset_pieces(piece_list, force=False):
    """resets all pieces if all are placed. Can be forced to reset if game is restarted."""

    empty = True  # automatically assumes that the slot for a given piece is empty
    for z in range(3):  # checks each piece
        if piece_list[z].state != 2:  # if slot is not empty (state == 2), then changes empty variable to false
            empty = False

    if empty or force:  # if all 3 slots are empty, or if forced, calls piece.reset() for all three pieces
        for z in range(3):
            piece_list[z].reset()
        # check_fair_pieces()  # function to ensure that new pieces are fair (won't cause game to end)
        # currently disabled because it's not a feature in the actual game. It's some bullshit.


def check_fair_pieces():
    """checks if the new pieces are fair (won't cause game to instantly end)"""
    unfair = check_game_over()  # uses game over function to see if any pieces can be placed
    if unfair:  # if no pieces can be placed, then a random piece is reset
        PIECES[random.randint(0, 2)].reset()
        check_fair_pieces()  # use recursion to check if new arrangement is fair and so on


def check_game_over():
    """returns true if game is over / no pieces can be placed. Returns false if a piece can be placed."""
    # pulls up every shape that is not placed and checks it against every possible spot
    for i in range(3):
        if PIECES[i].state != 2:
            for a in range(10):
                for b in range(10):

                    works = True
                    # pulls up every square in shape blueprint and adjusts to position
                    for shape_coord_x, shape_coord_y in PIECES[i].shape_blueprint:
                        shape_coord_x += a
                        shape_coord_y += b

                        # if a square in the shape can't be placed, then it is considered to not work
                        if not (0 <= shape_coord_x <= 9 and 0 <= shape_coord_y <= 9 and not BOARD[shape_coord_y][shape_coord_x]):
                            works = False
                            break
                    # if any one possibility works then it returns that the game has not ended
                    if works:
                        return False
    # if all shapes and positions are tested and none work, returns that the game is over
    return True


# option 1 = immediately resets game (good for bot), option 2 = game over screen that needs restart_button to be pressed
def handle_game_over(option=1):
    """handles what happens when the game ends, based on needs."""
    if option == 1:
        reset_game(PIECES)


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
    reset_pieces(piece_list, force=True)
    check_high_score()


def run_bot(mybot):
    """argument is the bot class that you want to use. It must have the associated function mybot.make_move"""
    global CLICKED_PIECE_INDEX
    CLICKED_PIECE_INDEX, x_coord, y_coord = mybot.make_move(BOARD, PIECES)  # gets move from bot

    if 0 <= CLICKED_PIECE_INDEX <= 2 and PIECES[CLICKED_PIECE_INDEX].state != 2:
        PIECES[CLICKED_PIECE_INDEX].state = 1
        state = place_piece(x_coord, y_coord)
        PIECES[CLICKED_PIECE_INDEX].state = state
        if state == 2:
            check_lines()

    else:
        CLICKED_PIECE_INDEX = -1  # if no piece was clicked, then index is -1


def main(bot_selection=False, rounds=1):
    global GAME_MODE, MOUSE_X, MOUSE_Y
    reset_button_pressed = False
    mouse_pressed = False
    check_high_score()
    py.display.set_caption(WINDOW_TITLE)

    running = True
    count = 0
    all_scores = []
    while running and count < rounds:
        # print(f'\rRound: {count}', end='', flush=True)

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
        reset_pieces(PIECES)

        # Checks if game is over (whether through reset or other). If so, handles game over.
        game_over = check_game_over()

        if not running or game_over or reset_button_pressed:
            all_scores.append(SCORE)
            count += 1
            # print(SCORE)
            check_high_score(reset_score=True)

            if reset_button_pressed:
                reset_button_pressed = False
                reset_game(PIECES)
            elif game_over:
                handle_game_over()
            else:
                running = False

        # Draws all visuals
        visuals()
        RESTART_BUTTON.update(mouse_pressed, MOUSE_X, MOUSE_Y)
        BOT_BUTTON.update(mouse_pressed, MOUSE_X, MOUSE_Y)
        time.sleep(0.5)

    median = np.median(np.array(all_scores))
    return median, max(all_scores), min(all_scores)


def try_configuration(weights, rounds):
    bot = bot_file.Bot(1, weights)  # create bot object
    median, max_score, min_score = main(bot, rounds=rounds)  # need to pass a bot object to main, nothing else

    # bot.output_time_breakdown()

    return median, max_score, min_score, weights


def generate_all_permutations():
    import itertools

    # Define the possible values each element can take
    possible_values = [i * 0.5 for i in range(3)]  # [0.0, 0.2, 0.4, 0.6, 0.8, 1.0]
    print(possible_values)

    # Generate all possible combinations with repetition for the given length of the list
    combinations = list(itertools.product(possible_values, repeat=5))

    # Convert combinations to a set to filter out duplicates, if any
    unique_combinations = set(combinations)

    # Convert back to list if needed
    unique_combinations_list = list(unique_combinations)

    print(len(unique_combinations_list), "combinations testing")
    return unique_combinations_list


def explore_around(configuration, increments, num_increments):  # num increments above and below original values
    import itertools
    adjustments = [i * increments - num_increments * increments for i in range(num_increments * 2 + 1)]
    print("Testing the following configuration:", configuration)
    print("Testing the following adjustments:", adjustments)
    combinations_of_increments = list(itertools.product(adjustments, repeat=len(configuration)))
    unique_combinations = set(combinations_of_increments)

    new_configurations = [np.add(configuration, unique_combination) for unique_combination in unique_combinations]

    count = 0
    for config in new_configurations:
        for num in config:
            if num < 0:
                new_configurations = np.delete(new_configurations, count, axis=0)
                count -= 1
                break
        count += 1

    return new_configurations


if __name__ == "__main__":
    RESULTS_LIST = []
    rounds = 200
    configs_to_try = [[0.8, 0.5, 0.7]]

    print("Testing", len(configs_to_try), "configurations")
    count = 0
    for weights in configs_to_try:
        count += 1
        print(f'\rWorking on configuration: {count}', end='', flush=True)
        RESULTS_LIST.append(try_configuration(weights, rounds))

    with open("poopoo", 'w') as f:
        f.write(str(RESULTS_LIST))
    f.close()  # closes file

    py.quit()