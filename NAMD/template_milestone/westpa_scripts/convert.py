import numpy as np

endpoint1 = ENDPOINT_1
endpoint2 = ENDPOINT_2

l = np.loadtxt('parent.dat')

r = l[len(l)-1]

#print("{:.2f}".format(r)) #needed for OpenMM (does not include zero frame by default)

l = []

l = np.loadtxt('distance.dat')

for i in range(len(l)):
    if r > endpoint1 and r < endpoint2:
        r = l[i]
    print("{:.2f}".format(r))
