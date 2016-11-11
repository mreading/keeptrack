import os
f = open('reqs.txt', 'r')
for line in f.readlines():
    os.system("pip install " + line)
f.close()
