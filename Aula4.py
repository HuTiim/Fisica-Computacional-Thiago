import numpy as np


x = np.linspace(0,2*np.pi,1000)
y = np.sin(x)


matriz = np.array([x,y]).T

np.savetxt("arquivo.dat" , matriz, delimiter = "\t", header= "X                         Y")

np.save("arquivo.npy" , matriz)

np.savez("arquivo.npz", Thiago = x, Lucas = y)