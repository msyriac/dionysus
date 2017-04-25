'''Tests whether the random place selection is working as expected
'''

from __future__ import print_function
from main import location_decision
import numpy as np

# get places and weights
places_weights = np.genfromtxt("listOfPlaces.csv", delimiter=",",
                               names=True, dtype=['U128', float])
my_places = places_weights['name']
weights = places_weights['weight']

N = 10000

counts = {}


for i in xrange(N):
    decision = location_decision(my_places,weights)
    try:
        counts[decision] += 1
    except KeyError:
        counts[decision] = 0

    
weights /= np.sum(weights)
for place in counts.keys():
    counts[place] /= float(N)
    print(place,'{:.3f}'.format(counts[place]),'{:.3f}'.format(weights[my_places.tolist().index(place)]))

