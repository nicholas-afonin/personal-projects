import json
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.ticker import PercentFormatter

# Get data from file interpreting it as a json. treat it as dictionary to extract game results
files = [file for file in open('Game_data')]
data = [json.loads(open('Game_data/' + file, 'r').read()) for file in files]
history = [+ a['history'] for a in data]
game_results = [+ float(game['gameResult']) for game in history]

# Print the results
print(game_results)

plt.hist(game_results, weights=np.ones(len(game_results)) /  len(game_results), range=(1, 2), bins=5, ec='black')
plt.gca().yaxis.set_major_formatter(PercentFormatter(1))
# plt.hist(game_results, color='lightgreen', ec='black', bins=10, range=(1, 10))

plt.show()
