
import time
import asyncio
import numpy as np

from matplotlib import pyplot as plt

async def main(frequency):
    time_last = time.time()
    x_end = 3
    sleep_meas = 0
    await asyncio.sleep(1 / (frequency))
    await asyncio.sleep(1 / (frequency))
    await asyncio.sleep(1 / (frequency))
    sleep_meas = time.time() - time_last
    print(f"{frequency}: {1/(sleep_meas/x_end)}")
    return 1/(sleep_meas/x_end)

f = np.geomspace(10, 5000, 1000)

f_meas = []
for freq in f:
    f_meas.append(asyncio.run(main(freq)))

fig, ax = plt.subplots()
ax.plot(f, f_meas)
ax.set_xlabel("commanded frequency")
ax.set_ylabel("measured frequency")

plt.savefig("test3.png")
plt.show()
