import time
import os
dir_old = 'D:/python/vinted/etykiety'
dir = 'D:/python/vinted/etykiety/nowe'
printed = 0
for f in os.listdir(dir):
    filePath = os.path.join(dir, f)
    # os.startfile(filePath, "print")
    time.sleep(4)
    os.remove(os.path.join(dir, f))
    os.remove(os.path.join(dir_old, f))
    printed += 1

print()
print("-------------------------------------------")
print(f"Wydrukowano etykiet: {printed}")
print("-------------------------------------------")
print()
input('Naciśnij >ENTER< by wyjść')
