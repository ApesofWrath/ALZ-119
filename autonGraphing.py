import matplotlib.pyplot as plt
import numpy as np

with open(r"C:\Users\school\Desktop\autonPoints.txt", 'r') as f: # change adress to "ftp://roborio-668-frc.local/home/lvuser/test.txt"
    data = f.read()

lines = data.splitlines()
groups = []
cg = []
heading = []
leftPos = []
rightPos = []
leftVel = []
rightVel = []

for ln, x in enumerate(lines):
    if ln > 2:
        cg.append(x)
        if (ln - 2) % 6 == 0:
            heading.append(-1 * float(cg[1]))
            leftPos.append(-1 * float(cg[2]))
            rightPos.append(-1 * float(cg[3]))
            leftVel.append(-1 * float(cg[4]))
            rightVel.append(-1 * float(cg[5]))
            cg = []

# heading
plt.subplot(511)
plt.plot(heading)
plt.xlabel('time')
plt.ylabel('heading')
plt.title('heading')

# left postion
plt.subplot(512)
plt.plot(leftPos)
plt.xlabel('time')
plt.ylabel('left position')
plt.title('left position')

# right position
plt.subplot(513)
plt.plot(rightPos)
plt.xlabel('time')
plt.ylabel('right position')
plt.title('right position')

# left velocity
plt.subplot(514)
plt.plot(leftVel)
plt.xlabel('time')
plt.ylabel('left velocity')
plt.title('left velocity')

# right velocity
plt.subplot(515)
plt.plot(rightVel)
plt.xlabel('time')
plt.ylabel('right velocity')
plt.title('right velocity')

plt.show()
