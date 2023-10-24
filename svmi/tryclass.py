
# class rectangle:
#     def __init__(self,widths,height):
#         self.width = widths
#         self.height = height
#
# rectangle = rectangle(20,80)
# print(rectangle.width,rectangle.height)
# Python module to execute
# import filetwo

# params = ['a','b','x']
# values = ['1','2','3']
#
# for i in range(len(params)):
#     print(i)
#     try:
#         exec(params[i]+"=%s"%(values[i]))
#         print('everything goes well')
#     except(NameError, SyntaxError):
# 	    exec(params[i]+"='%s'"%(values[i].strip()))
#         # print('something goes wrong')
#
#
# print(params)
# print(params[0]+"=%s"%(values[0]), end='\n')
# print(params[0]+"='%s'"%(values[0].strip()))
import numpy as np
from math import gcd


xdata = []
ydata = []
output = np.array([[[0,1.,2.,3.,4.,5.],[0.,1.,2.,3.,4.,5.],\
                    [0.,1.,2.,3.,4.,5.],[0.,1.,2.,3.,4.,5.],\
                    [0.,1.,2.,3.,4.,5.],[0.,1.,2.,3.,4.,5.]],\
                   [[6.,7.,8.,9.,10.,11.],[6.,7.,8.,9.,10.,11.],\
                    [6.,7.,8.,9.,10.,11.],[6.,7.,8.,9.,10.,11.],\
                    [6.,7.,8.,9.,10.,11.],[6.,7.,8.,9.,10.,11.]],\
                   [[6.,7.,8.,9.,10.,11.],[6.,7.,8.,9.,10.,11.],\
                    [6.,7.,8.,9.,10.,11.],[6.,7.,8.,9.,10.,11.],\
                    [6.,7.,8.,9.,10.,11.],[6.,7.,8.,9.,10.,11.]]])

output = [[1,2,3,4,5],[1,2,3,4,5],[1,2,3,4,5],[1,2,3,4,5],[1,2,3,4,5],\
          [6,7,8,9,10],[6,7,8,9,10],[6,7,8,9,10],[6,7,8,9,10],[6,7,8,9,10]]
# print(np.shape(output))

a = np.array([1,2,3,4,5,6])
# for i in range(len(output[0])):
#     y = []
#     xdata.append(float(output[1][i]))
#     for j in range(len(output[0][i])):
#         y.append(float(output[0][i][j]) + 2 * j)
#     ydata.append(y)

def lcm(a):
	'''
			find lowest common multiple of items in a list
	'''
	lcm = a[0]
	for i in a[1:]:
        # print(i)
		lcm = lcm*i/gcd(lcm, i)
	return lcm
#
print(gcd(1,3))

# for i in range(10):
#     print(i)

def indexlist(lists, element):
	'''
	creates a list of indices with a certain value from given list
	'''
	indices= [i for i, x in enumerate(lists) if x == element]
	return indices

# print(indexlist(output,[6,7,8,9,10]))