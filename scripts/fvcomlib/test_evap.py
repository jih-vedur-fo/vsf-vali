import fvcomlibutil as u
import numpy as np

T2 = np.array([[1, 2, 3],[4,5,6],[7,8,9]])
WS_EN = np.copy(np.multiply(1.2,T2))
#T = 16
T0 = np.array([5,6,7])

wind = 14.0

X = u.calcEvapSimple(WS_EN,u.calcTempSea(T0,5,12),T2,0.8)


