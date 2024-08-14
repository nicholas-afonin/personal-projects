import pygame as py
import random
import numpy as np


class Piece:
    def __init__(self, position, window, shape_dict, colour_dict):
        self.shape = random.choice(list(shape_dict.keys()))
        self.shape_blueprint, self.margin, self.enlargement_diff, self.score, self.colour, self.perimeter = shape_dict[self.shape]
        self.position = position
        self.grid_positioning = position * 130  # uses the position (0, 1, 2) to place piece in correct spot
        self.state = 0  # 0 - not clicked, 1 - clicked, 2 - placed
        self.coordinates = (0, 0)  # the pixel coordinates of the shape on the screen
        self.window = window
        self.colour_dict = colour_dict
        self.shape_dict = shape_dict

    def draw(self, mouse_x, mouse_y, initial_x, initial_y):
        if self.state == 0:  # passive state -- not clicked
            x_adjustments = 50 + self.margin + self.grid_positioning  # selection area margin, shape margin, piece #
            y_adjustments = 550  # selection area margin

            for coord_x, coord_y in self.shape_blueprint:
                # draws each square in the shape -- width of square is 20 (19 to allow 1 pixel line between)
                py.draw.rect(self.window, py.Color(self.colour_dict[self.colour]), (x_adjustments + coord_x * 20, y_adjustments + coord_y * 20, 19, 19), width=0)

        elif self.state == 1:  # active state -- being dragged
            # calculates the mouse's change in position from its click to adjust shape by same amount
            x_mouse_change, y_mouse_change = mouse_x - initial_x, mouse_y - initial_y

            # selection area margin + shape margin + adjustment for piece # + mouse change + change when enlarged
            x_adjustments = 50 + self.margin + self.grid_positioning + x_mouse_change - self.enlargement_diff
            y_adjustments = 550 - 50 + y_mouse_change  # selection margin, piece visibility change, mouse change
            self.coordinates = (x_adjustments, y_adjustments)

            for coord_x, coord_y in self.shape_blueprint:
                # draws each square in the shape -- width of square is 40 (38 to allow 2 pixel line between)
                py.draw.rect(self.window, py.Color(self.colour_dict[self.colour]), (x_adjustments + coord_x * 40, y_adjustments + coord_y * 40, 38, 38), width=0)

    def reset(self):
        self.__init__(self.position, self.window, self.shape_dict, self.colour_dict)
        # re-initializes the piece when piece.reset() is called


class Text:
    def __init__(self, text, size, location, window, font='calibri'):  # location is (x, y)
        self.size = size
        self.location = location  # will correspond to the center of the "text box" where the text is drawn
        self.font = py.font.SysFont(font, size, bold=True)
        self.text = self.font.render(text, True, py.Color('white'))
        self.text_rect = self.text.get_rect()
        self.text_rect.center = self.location[0], self.location[1]
        self.window = window

    def draw(self):
        self.window.blit(self.text, self.text_rect)

    # updates actual text (ex. score_label.update("score: 5")) to make it now display "score: 5"
    def update(self, text):
        self.text = self.font.render(text, True, py.Color("white"))
        self.text_rect = self.text.get_rect()
        self.text_rect.center = self.location[0], self.location[1]


class Button:
    def __init__(self, text, size, location, window, font='calibri'):
        self.location = location
        self.font = py.font.SysFont(font, size, bold=True)
        self.text = self.font.render(text, True, py.Color('white'))
        self.text_rect = self.text.get_rect()
        self.text_rect.center = self.location[0], self.location[1]
        self.button_rect = py.Rect(self.location[0]-50, self.location[1]-20, 100, 40)
        self.button_rect.center = self.location[0], self.location[1]
        self.state = 0  # 0 = passive, 1 = hovering, 2 = actively being pressed
        self.window = window

    def draw(self):
        if self.state == 1:  # hovering over button - gray fill
            py.draw.rect(self.window, py.Color("gray"), self.button_rect, width=0)

        elif self.state == 2:  # button being pressed - white fill
            py.draw.rect(self.window, py.Color("white"), self.button_rect, width=0)

        # text and hollow box - always being drawn
        py.draw.rect(self.window, py.Color("white"), self.button_rect, width=2)
        self.window.blit(self.text, self.text_rect)

    # updates the state of the button based on where mouse is and if it's pressed down
    def update(self, mouse_pressed, mouse_x, mouse_y):
        mouse_on_rect = self.button_rect.collidepoint(mouse_x, mouse_y)  # true if mouse and rect collide
        if mouse_on_rect and mouse_pressed:
            self.state = 2
        elif mouse_on_rect:
            self.state = 1
        else:
            self.state = 0


def clear_lines(board):
    """
    checks the board and clears full lines.
    @param board: the game board to check
    @return updated board: board with any full lines cleared
    @return lines_cleared: number of lines that were cleared on the baord
    """
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

    # clears lines that are full - might be a faster way to do this not sure
    for y_coord in horizontal_clears:
        for x_coord in range(10):
            board[y_coord][x_coord] = 0
    for x_coord in vertical_clears:
        for y_coord in range(10):
            board[y_coord][x_coord] = 0

    lines_cleared = len(horizontal_clears) + len(vertical_clears)

    return board, lines_cleared


def place_piece(x_coord, y_coord, piece, board, place_value=1, return_value=1):
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

    return board, return_value
