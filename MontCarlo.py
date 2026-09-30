import numpy as np
import numpy.random as rng

n = 10000000
p = 0


for i in range (n):
    x = rng.rand()
    y = rng.rand()

    if x*x + y*y <=1:
        p = p + 1

print((4*p)/n)        
