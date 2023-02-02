#!/usr/bin/env python
"""
Show elapsed time for each app.
Take the log file generated from measure*.sh as an input.
"""

import sys
import re

apps = ["darknet", "laghos", "miniMDock", "XSBench", "huffman", \
        "dwt2d", "2MM", "3MM", "GRAMSCHM", "BICG"]

# The output.log file from overhead.sh's output
file = open(sys.argv[1])

line = file.readline()

app = ""
time_sum = 0.0
iteration = 0

elapsed_time_list = list()

while line:
    if "install-" in line:
        continue
    flag = [i for i in apps if i in line]
    if flag or "END" in line:
        if time_sum != 0:
            elapsed_time_list.append((app[0], round(time_sum / iteration, 4), iteration))
        time_sum = 0.0
        iteration = 0
        app = flag
    if "real" in line:
        nums = re.findall(r"\d+\.?\d*", line)
        if len(nums) == 1:
            time_sum += float(nums[0])
        elif len(nums) == 2:
            time_sum += (float(nums[0]) * 60 + float(nums[1]))
        iteration += 1
    line = file.readline()

for item in elapsed_time_list:
    print("App: %s\t elapsed time: %f s\t iterations: %d"%(item[0], item[1], item[2]))