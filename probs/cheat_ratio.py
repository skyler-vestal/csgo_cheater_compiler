import pandas as pandas
from matplotlib import pyplot as plt 
from scipy.stats import binom

plt.style.use('fivethirtyeight')

NUM_PLAYERS = 10
MAX = 400
DIVS = 1000

probs = []
rates = [x/DIVS for x in range(0, MAX)]

for rate in rates:
    probs.append(1 - binom.pmf(0, NUM_PLAYERS, rate))

plt.plot(rates, probs)

plt.title('Probability of a Pure Match')
plt.xlabel('% of Players Cheating')
plt.ylabel('% of Matches Pure')

plt.show()