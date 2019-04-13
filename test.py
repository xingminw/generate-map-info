import numpy as np


x1 = np.array([[4], [0]])
x2 = np.array([[0], [8]])

rx = np.array([[8, 12], [12, 40]])
rzx = np.array([[24, 80], [12, 40]])
opt = np.dot(rzx, np.linalg.inv(rx))
print("opt", opt)

z1 = np.array([[16], [8]])
rz = np.dot(z1, np.transpose(z1)) * 5 / 8
print(rz)

mse = np.dot(rzx, np.linalg.inv(rx))
mse = np.dot(mse, np.transpose(rzx))
mse = rz - mse
print(mse)

czx = np.array([[4, 30], [2, 15]])
cx = np.array([[4, 2], [2, 15]])
g_opt = np.dot(czx, np.linalg.inv(cx))
print(g_opt)


