#THIS CODE IS ONLY FOR FIRST MILSTONE. build.py WILL REPLACE convert.py WITH THIS FILE FOR FIRST MILESTONE

import numpy as np

endpoint = XX

l = np.loadtxt('parent.dat')

r = l[len(l)-1]

print("{:.2f}".format(r)) #needed for OpenMM (does not include zero frame by default)

l = []

l = np.loadtxt('distance.dat')

for i in range(len(l)):
    if r < endpoint:
        r = l[i]
    print("{:.2f}".format(r))
