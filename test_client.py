from Entities import Soldier, BTW, Packet, InitMessage
import sys
import pickle

min_float = sys.float_info.min
max_float = sys.float_info.max

a = Soldier(1, (min_float, min_float), 100)
b = Soldier(1, (max_float, max_float), 100)
c = BTW(1, (min_float, min_float), 100)
d = BTW(1, (max_float, max_float), 100)

m1 = InitMessage(a)
m2 = InitMessage(b)
p1 = Packet(1,2,1,4,m1)
p2 = Packet(1,2,1,4,m2)

pickle1 = pickle.dumps(p1)
pickle2 = pickle.dumps(p2)

print(sys.getsizeof(pickle1), sys.getsizeof(pickle2), sys.getsizeof(c), sys.getsizeof(d))