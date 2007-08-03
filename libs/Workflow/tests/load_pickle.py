from test import *
import pprint, pickle
pkl_file = open('data.pkl', 'rb')
one = pickle.load(pkl_file)
#pprint.pprint(one)
#data2 = pickle.load(pkl_file)
#pprint.pprint(data2)
pkl_file.close()

print one._name
print one._child._name
