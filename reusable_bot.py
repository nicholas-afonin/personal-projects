import numpy as np
import random


class Layer:
    """a layer of nodes in the neural network"""
    def __init__(self, num_nodes, num_nodes_previous_layer):
        self.num_nodes = num_nodes
        self.nodes = np.array(num_nodes)
        self.weights = [np.random.rand(num_nodes_previous_layer)*2-1 for i in range(num_nodes)]
        self.biases = [random.random()*2-1 for i in range(num_nodes)]

    def calculate_nodes(self, previous_layer):
        """calculates the values of the nodes in the layer given the previous layer"""
        self.nodes = np.array(
            [activation_function(np.dot(previous_layer.nodes, self.weights[i]) + self.biases[i]) for i in
             range(self.num_nodes)])


class Bot:
    def __init__(self, network_structure):
        # Create a network excluding the first layer
        self.network_structure = network_structure
        self.layers = np.array(len(network_structure) - 1)
        self.layers = [Layer(network_structure[i], network_structure[i - 1]) for i in range(1, len(network_structure))]
        self.score = 0

    def calculate_output(self, input_layer):
        """calculates the output of the network given the input layer"""
        # ensures input layer is of the correct format
        input_layer_object = Layer(len(input_layer), 0)
        input_layer_object.nodes = np.array(input_layer)
        input_layer = input_layer_object

        for layer in self.layers:
            layer.calculate_nodes(input_layer)
            input_layer = layer

        return input_layer

    def breed_child(self, other_bot):
        child = Bot(self.network_structure)
        for layer in range(len(self.layers)):  # for layers in child
            for node in range(len(self.layers[layer].nodes)):  # for nodes in layer
                for weight in range(len(self.layers[layer].weights[node])):  # for weights in node
                    # randomly take weight from one of parents
                    if random.random() < 0.5:
                        child.layers[layer].weights[node][weight] = self.layers[layer].weights[node][weight]
                    else:
                        child.layers[layer].weights[node][weight] = other_bot.layers[layer].weights[node][weight]

                # randomly take bias from one of parents
                if random.random() < 0.5:
                    child.layers[layer].biases[node] = self.layers[layer].biases[node]
                else:
                    child.layers[layer].biases[node] = other_bot.layers[layer].biases[node]

        return child

    def mutate(self, mutation_rate=0.1, mutation_strength=0.5):
        """mutates weights and biases"""
        # 1 in every 10 biases and weights are mutated by adding a random number from a normal distribution
        # at least when the mutation rate is 0.1 (meaning 10% of parameters will mutate)
        for layer in self.layers:
            for node in range(layer.num_nodes):
                for weight in range(len(layer.weights[node])):
                    if random.random() < mutation_rate:
                        layer.weights[node][weight] += random.gauss(0, mutation_strength)
                if random.random() < mutation_rate:
                    layer.biases[node] += random.gauss(0, mutation_strength)


def activation_function(x, activation="sigmoid"):
    # Activation can either be "sigmoid" or "relu" at this time
    if activation == "sigmoid":
        if x >= 0:
            z = np.exp(-x)
            return 1 / (1 + z)
        else:
            z = np.exp(x)
            return z / (1 + z)

    if activation == "relu":
        return x * (x > 0)