import numpy as np
import reusable_bot as bot
import game_old as game
import time


class GameBot:
    def __init__(self, network_shape, shape_dict):
        self.bot = bot.Bot(network_shape)
        self.score = 0
        self.shape_dict = shape_dict

    def make_move(self, game_board, pieces):
        """takes in game state and returns a piece and a square on the grid"""
        first_layer = create_first_layer(game_board, pieces, self.shape_dict)
        output_layer = self.bot.calculate_output(first_layer)
        piece, x_coord, y_coord = create_last_layer(output_layer, pieces, self.shape_dict)

        return piece, x_coord, y_coord


class BotTrainer:
    def __init__(self, network_shape, num_bots, evolution_cycles):
        self.bots = [GameBot(network_shape, game.SHAPE_DICT) for i in range(num_bots)]
        self.num_bots = num_bots
        self.evolution_cycles = evolution_cycles

    def run_bots(self):
        """runs all bots through game and updates their scores (once they die)"""
        for i in range(100):
            self.bots[i].score = game.main(self.bots[i])

    def select_parents(self, num_parents):
        """selects the best bots to be parents"""
        # for now just choose the 5 highest scores,
        # but there can be more complex fitness functions and selection methods
        self.bots.sort(key=lambda x: x.score, reverse=True)
        return self.bots[:num_parents]

    def breed_children(self, parents):
        """combine parameters from pairs of parents to create children - various potential methods"""
        num_children = self.num_bots - len(parents)
        children = []

        for i in range(num_children):
            options = [i for i in range(len(parents))]
            parents_to_breed = np.random.choice(options, 2, replace=False)
            # create a child with same network structure as parents
            child_gamebot = GameBot(parents[0].bot.network_structure, game.SHAPE_DICT)
            # breed to create child, specifically of the form of a GameBot.bot object
            child_gamebot.bot = parents[parents_to_breed[0]].bot.breed_child(parents[parents_to_breed[1]].bot)
            children.append(child_gamebot)

        return parents + children

    def mutate(self):
        """mutates weights and biases of all bots"""
        for child in self.bots:
            child.bot.mutate()

    def run_evolution(self):
        """runs the evolution cycle"""
        for i in range(self.evolution_cycles):
            self.run_bots()
            parents = self.select_parents(19)
            new_family = self.breed_children(parents)
            self.bots = new_family
            self.mutate()

            print([i.score for i in parents])


def create_first_layer(game_board, pieces, shape_dict):
    """creates the first layer of the network"""
    first_layer = []
    for row in game_board:
        for square in row:
            first_layer.append(square)

    # different ways to do this next part. I prioritize the game just knowing which pieces it CAN place.
    # how many are already placed is irrelevant for now.
    temp_list = [0 for i in range(19)]
    for piece in pieces:
        if piece.state == 0:  # might need to be != 2 for some random reason who knows
            temp_list[(list(shape_dict.keys())).index(piece.shape)] = 1
    first_layer += temp_list

    return np.array(first_layer)


def create_last_layer(output_layer, pieces, shape_dict):
    """
    :return: piece, square  # square from 0-100, piece from 0-3
    """
    square = np.argmax(output_layer.nodes[0:100])

    piece_index = np.argmax(output_layer.nodes[100:])
    piece_code = list(shape_dict.keys())[piece_index]
    specific_piece = -1
    for piece in pieces:
        if piece.shape == piece_code:
            specific_piece = pieces.index(piece)
            break

    return specific_piece, square // 10, square % 10


if __name__ == "__main__":
    bot_trainer = BotTrainer([119, 100, 100, 100, 119], 200, 100)
    bot_trainer.run_evolution()