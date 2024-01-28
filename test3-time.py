
import time
import numpy as np

from matplotlib import pyplot as plt

def main(frequency):
    time_last = time.time()
    x = 0
    x_end = 3
    sleep_meas = 0
    time.sleep(1 / (frequency))
    time.sleep(1 / (frequency))
    time.sleep(1 / (frequency))
    sleep_meas = time.time() - time_last
    print(f"{frequency}: {1/(sleep_meas/x_end)}")
    return 1/(sleep_meas/x_end)

f = np.geomspace(10, 5000, 1000)

#f = [1, 10, 200, 300]

f_meas = []
for freq in f:
    f_meas.append(main(freq))

fig, ax = plt.subplots()
ax.plot(f, f_meas)
ax.set_xlabel("commanded frequency")
ax.set_ylabel("measured frequency")

plt.savefig("test3-time.png")
plt.show()
