#!/usr/bin/env python
"""
Show elapsed time for each app.
Take the log file generated from measure*.sh as an input.
"""

import sys
import re

apps = ["BICG ori", "BICG opt", "GRAMSCHM ori", "GRAMSCHM opt"]

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
    if "Elapsed time" in line:
        nums = re.findall(r"\d+\.?\d*", line)
        if len(nums) == 1:
            time_sum += float(nums[0])
        elif len(nums) == 2:
            time_sum += (float(nums[0]) * 60 + float(nums[1]))
        iteration += 1
    line = file.readline()

time_map = dict()
for item in elapsed_time_list:
    time_map[item[0]] = item[1]

# for k in time_map.keys():
#     print(k, time_map[k])

print("GRAMSCHM ori elapsed time {} ms".format(time_map["GRAMSCHM ori"]))
print("GRAMSCHM opt elapsed time {} ms".format(time_map["GRAMSCHM opt"]))
print("GRAMSCHM speedup: {:.2f}X".format(time_map["GRAMSCHM ori"]/time_map["GRAMSCHM opt"]))
print("----------------------------------------")

print("BICG ori elapsed time {} ms".format(time_map["BICG ori"]))
print("BICG opt elapsed time {} ms".format(time_map["BICG opt"]))
print("BICG speedup: {:.2f}X".format(time_map["BICG ori"]/time_map["BICG opt"]))
print("----------------------------------------")