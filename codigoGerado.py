def main():
    a = 5
    b = 0
    for i in range(20, 10, -1):
        a = a + i
    while a > 0:
        a = a - 1
    if a < 2:
        a = 200
    elif a <= 50:
        a = 45000
    elif a != b:
        a = - 1
    else:
        a = 96
    return a
def main2():
    c = True
    d = True
    if c == True and d == False:
        return True
    else:
        return False
def main3(a=1, b=2):
    return a + b