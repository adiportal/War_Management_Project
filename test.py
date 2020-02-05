import linecache
from datetime import datetime
import datetime



file_name = 'FieldLog.log'

def file_len(fname):
    with open(fname) as f:
        for i, l in enumerate(f):
            pass
    return i + 1


num_of_lines = file_len('FieldLog.log')
print(num_of_lines)

file = open('FieldLog.log', 'r')

first_line = linecache.getline(file_name, 1)
last_line = linecache.getline(file_name, num_of_lines)
print(first_line)
print(last_line)

begin_time = first_line[0:19]
begin = datetime.datetime.strptime(begin_time, "%Y-%m-%d %H:%M:%S")
end_time = last_line[0:19]
end = datetime.datetime.strptime(end_time, "%Y-%m-%d %H:%M:%S")
print(begin)
print(end)
b = begin + datetime.timedelta(seconds=5)
print("b:", b)

# time = end - begin
# print("time:", time)
# print(time.seconds)
