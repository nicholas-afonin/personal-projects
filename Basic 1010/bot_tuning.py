import bot as bot_file
import numpy as np


"""
The following functions can be used to test and refine the bot's weighting
(the amount that it values different factors in making decisions)
"""


def try_configuration(weights, rounds, main_function):
    """Given a set of weights, generate a bot with those weights and have it play n rounds"""
    bot = bot_file.Bot(1, weights)  # create bot object
    median, max_score, min_score = main_function(bot, rounds=rounds)  # need to pass a bot object to main, nothing else

    return median, max_score, min_score, weights


def generate_all_permutations(possible_values, length):
    """Generate all possible permutations of weights with given parameters
    @param: possible_values: the possible values held by each number in the set
    @param: length: the length of the set, or number of weights
    """
    import itertools

    # Define the possible values each element can take
    print(possible_values)

    # Generate all possible combinations with repetition for the given length of the list
    combinations = list(itertools.product(possible_values, repeat=length))

    # Convert combinations to a set to filter out duplicates, if any
    unique_combinations = set(combinations)

    # Convert back to list if needed
    unique_combinations_list = list(unique_combinations)

    print(len(unique_combinations_list), "combinations testing")
    return unique_combinations_list


def explore_around(configuration, increments, num_increments):  # num increments above and below original values
    """Takes a weight configuration and returns a list of slightly different configurations
    to try (according to the provided arguments)
    """
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
