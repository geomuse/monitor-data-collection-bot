'''
a , b = 1 , 2 
print(a ,b)

from itertools import zip_longest

a = [1,2]
b = [1]
df = list(zip_longest(a,b,fillvalue=None))
print(df)
'''

'''
li = [1,23,4,5,6]

for i in li : 
    print(i)
    if i > 2 : 
        continue
    else:
        print('ok')
'''

'''
a , b = [1,'2.',3,4,5,6] , [2,3,4,5,5,6] 
li = []
for x , y in zip(a,b):
    li.append((x,y))

for ip , port in li :
    # ip , port
    # if ip + port > 7 :
    #     print(ip,port)
    try :
        ip = ip.replace('.','s')
        # print(ip)
    except Exception as e:
        print(f'error : {e}') 
        continue
    print("it's work.")   
'''

li = [1]

if not li :
    print('empty.')
else : 
    print('data.')