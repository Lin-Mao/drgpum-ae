#!/usr/bin/env python
"""
Usage: python show_liveness_patterns.py -h to see details
"""

import os
import re
import sys
import argparse


def check_path(path):
    """
    Check path legality
    :param path: path to memory_liveness folder
    """
    file_list = os.listdir(path)
    memory_liveness = "memory_liveness.txt" in file_list
    kernel_list = "kernel_list.txt" in file_list
    memory_size_list = "memory_size_list.txt" in file_list
    if not memory_liveness or not kernel_list or not memory_size_list:
        print("An illegal Path!(Specify path to memory liveness folder)")
        exit()


def lower_bound(nums, target):
    low, high = 0, len(nums) - 1
    pos = len(nums)
    while low < high:
        mid = int((low + high) / 2)
        if nums[mid] < target:
            low = mid + 1
        else:  # >=
            high = mid
            # pos = high
    if nums[low] >= target:
        pos = low
    return pos


def upper_bound(nums, target):
    low, high = 0, len(nums) - 1
    pos = len(nums)
    while low < high:
        mid = int((low + high) / 2)
        if nums[mid] <= target:
            low = mid + 1
        else:  # >
            high = mid
            pos = high
    if nums[low] > target:
        pos = low
    return pos


def get_interval(prev_kernel, next_kernel, kernel_list):
    """
    Get the number of kernels between two kernel instances
    """
    prev_index = upper_bound(kernel_list, prev_kernel)
    next_index = lower_bound(kernel_list, next_kernel)
    return next_index - prev_index


def check_reusable_objects(memory_access, path, pattern_result, app_patterns):
    """
    Check the memory reusability. Only the same size memories will be considered.
    """
    file = open(os.path.join(path, "memory_size_list.txt"))
    line = file.readline()
    same_size_memories = {}  # {size: [(first_id, memory_id), (last_id, memory_id), ...]
    memories = {}       # {size: { memory_id: 2, ...}, ...}
    while line:
        nums = re.findall(r"\d+\.?\d*", line)
        if int(nums[0]) in memory_access:
            if not int(nums[1]) in same_size_memories:
                same_size_memories[int(nums[1])] = [(memory_access[int(nums[0])][0], int(nums[0])),
                                                    (memory_access[int(nums[0])][1], int(nums[0]))]
                memories[int(nums[1])] = {int(nums[0]): 2}
            else:
                same_size_memories[int(nums[1])].append((memory_access[int(nums[0])][0], int(nums[0])))
                same_size_memories[int(nums[1])].append((memory_access[int(nums[0])][1], int(nums[0])))
                memories[int(nums[1])][int(nums[0])] = 2

        line = file.readline()
    file.close()
    # print(same_size_memories)
    # print(memories)

    for i in same_size_memories:
        same_size_memories[i].sort()

        finished_memories = list(memories[i].keys())  # both first_id and last_id are in the stack
        for j in range(len(same_size_memories[i])):
            kernel = same_size_memories[i].pop()    # [first_id (or last_id), memory_id]
            memories[i][kernel[1]] -= 1
            if kernel[1] in finished_memories:
                finished_memories.remove(kernel[1])

            if memories[i][kernel[1]] == 0:
                if finished_memories:
                    pattern_result[kernel[1]].append("reusable")
                    app_patterns[5] += 1

    return pattern_result, app_patterns


def get_patterns(path, threshold, kernel_list, kernel_count):
    """
    Get the liveness patterns except reusable objects
    """
    [early_threshold, late_threshold, temporary_threshold] = threshold

    if early_threshold < 1:
        early_threshold = early_threshold * kernel_count
    if late_threshold < 1:
        early_threshold = early_threshold * kernel_count
    if temporary_threshold < 1:
        temporary_threshold = temporary_threshold * kernel_count
    # print(int(early_threshold), int(late_threshold), int(temporary_threshold))

    # Store pattern categories {pattern1: count, ...}
    # 1: early, 2: late, 3: temp, 4: whole, 5: reusable, 6: dead, 7: leak
    app_patterns = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0}
    pattern_result = {}  # {memory: [pattern1, pattern2, ...]
    memory_access = {}  # {memory: [first, last]}

    file2 = open(os.path.join(path, "memory_liveness.txt"))
    line = file2.readline()  # filter the first object created by tool
    line = file2.readline()
    while line:
        nums = re.findall(r"\d+\.?\d*", line)
        patterns = []
        initial_op_flag = False
        dead_write = False
        temporary_idle = False
        alloc_id = 0
        first_id = 0
        access_id = 0
        last_id = 0
        free_id = 0

        for i in range(1, len(nums), 2):
            if int(nums[i + 1]) == 0:
                alloc_id = int(nums[i])

            elif int(nums[i + 1]) == 1 or int(nums[i + 1]) == 2 or int(nums[i + 1]) == 3:
                if initial_op_flag:
                    dead_write = True
                initial_op_flag = True

            elif int(nums[i + 1]) == 4:
                initial_op_flag = False
                last_id = int(nums[i])
                if access_id != 0:
                    if get_interval(access_id, last_id, kernel_list) >= int(temporary_threshold):
                        temporary_idle = True
                access_id = last_id
                if first_id == 0:
                    first_id = last_id

            elif int(nums[i + 1]) == 5:
                free_id = int(nums[i])

        if first_id == 0:
            patterns.append("whole-program idle")
            app_patterns[4] += 1
        if free_id == 0:
            patterns.append("memory leak")
            app_patterns[7] += 1
        if temporary_idle:
            patterns.append("temporary idle")
            app_patterns[3] += 1
        if dead_write:
            patterns.append("dead write")
            app_patterns[6] += 1
        if get_interval(alloc_id, first_id, kernel_list) >= int(early_threshold):
            patterns.append("early allocation")
            app_patterns[1] += 1
        if get_interval(last_id, free_id, kernel_list) >= int(late_threshold):
            if not last_id == 0:
                patterns.append("late de-allocation")
                app_patterns[2] += 1

        if not first_id == 0:
            memory_access[int(nums[0])] = [first_id, last_id]
        pattern_result[int(nums[0])] = patterns
        line = file2.readline()
    file2.close()

    return app_patterns, pattern_result, memory_access


def get_kernel_list(path):
    """
    Get the whole kernel list
    """
    kernel_list = []  # [kernel1, kernel2, ...]
    kernel_count = 0

    file1 = open(os.path.join(path, "kernel_list.txt"))
    line = file1.readline()
    while line:
        nums = re.findall(r"\d+\.?\d*", line)
        kernel_list.append(int(nums[0]))
        kernel_count += 1
        line = file1.readline()
    file1.close()

    return kernel_list, kernel_count


def get_memory_list(path):
    """
    Get the whole memory list sorted in size. (In descending order.)
    """
    memory_size_list = []
    file3 = open(os.path.join(path, "memory_size_list.txt"))
    line = file3.readline()
    while line:
        nums = re.findall(r"\d+\.?\d*", line)
        memory_size_list.append(int(nums[0]))
        line = file3.readline()
    file3.close()

    return memory_size_list


def write_patterns(path, app_patterns, memory_size_list, pattern_result, kernel_count):
    """
    Write kernel to file and output to terminal
    """
    file4 = open(os.path.join(path, "liveness_patterns.txt"), "w")

    print("Launch %lu kernel(s)"%(kernel_count))
    file4.write("Launch %lu kernel(s)\n"%(kernel_count))

    for i in app_patterns:
        if i == 1 and app_patterns[i] != 0:
            print("early allocation:    " + str(app_patterns[i]) + " object(s)")
            file4.write("early allocation: " + str(app_patterns[i]) + " object(s)\n")
        elif i == 2 and app_patterns[i] != 0:
            print("late de-allocation:  " + str(app_patterns[i]) + " object(s)")
            file4.write("late de-allocation: " + str(app_patterns[i]) + " object(s)\n")
        elif i == 3 and app_patterns[i] != 0:
            print("temporary idle:      " + str(app_patterns[i]) + " object(s)")
            file4.write("temporary idle: " + str(app_patterns[i]) + " object(s)\n")
        elif i == 4 and app_patterns[i] != 0:
            print("whole-program idle:  " + str(app_patterns[i]) + " object(s)")
            file4.write("whole-program idle: " + str(app_patterns[i]) + " object(s)\n")
        elif i == 5 and app_patterns[i] != 0:
            print("reusable:            " + str(app_patterns[i]) + " object(s)")
            file4.write("reusable: " + str(app_patterns[i]) + " object(s)\n")
        elif i == 6 and app_patterns[i] != 0:
            print("dead write:          " + str(app_patterns[i]) + " object(s)")
            file4.write("dead write: " + str(app_patterns[i]) + " object(s)\n")
        elif i == 7 and app_patterns[i] != 0:
            print("memory leak:         " + str(app_patterns[i]) + " object(s)")
            file4.write("memory leak: " + str(app_patterns[i]) + " object(s)\n")
    print()
    file4.write("\n")

    for i in memory_size_list:
        if i in pattern_result:
            print("{}: ".format(i))
            print(pattern_result[i])
            file4.write(str(i) + ": ")
            for j in pattern_result[i]:
                file4.write("\"" + j + "\", ")
            file4.write("\n")
    file4.close()


def report_patterns(app_patterns, memory_size_list, pattern_result, kernel_count):
    """
    Write kernel to file and output to terminal
    """

    print("Launch %lu kernel(s)"%(kernel_count))

    for i in app_patterns:
        if i == 1 and app_patterns[i] != 0:
            print("early allocation:    " + str(app_patterns[i]) + " object(s)")
        elif i == 2 and app_patterns[i] != 0:
            print("late de-allocation:  " + str(app_patterns[i]) + " object(s)")
        elif i == 3 and app_patterns[i] != 0:
            print("temporary idle:      " + str(app_patterns[i]) + " object(s)")
        elif i == 4 and app_patterns[i] != 0:
            print("whole-program idle:  " + str(app_patterns[i]) + " object(s)")
        elif i == 5 and app_patterns[i] != 0:
            print("reusable:            " + str(app_patterns[i]) + " object(s)")
        elif i == 6 and app_patterns[i] != 0:
            print("dead write:          " + str(app_patterns[i]) + " object(s)")
        elif i == 7 and app_patterns[i] != 0:
            print("memory leak:         " + str(app_patterns[i]) + " object(s)")

    # for i in memory_size_list:
    #     if i in pattern_result:
    #         print("{}: {}".format(i, pattern_result[i]))



def main(path, threshold):
    check_path(path)

    kernel_list, kernel_count = get_kernel_list(path)

    app_patterns, pattern_result, memory_access = get_patterns(path, threshold, kernel_list, kernel_count)

    pattern_result, app_patterns = check_reusable_objects(memory_access, path, pattern_result, app_patterns)

    memory_size_list = get_memory_list(path)

    report_patterns(app_patterns, memory_size_list, pattern_result, kernel_count)


if __name__ == "__main__":
    des = "Pattern Evaluation Automata: Report memory liveness patterns."
    parser = argparse.ArgumentParser(description=des)

    e_str = "Specify early allocated kernel intervals threshold (Default = 3). \
            If this value less than 1, then threshold = value * total_kernel_counts."
    parser.add_argument('-e', type=int, required=False, default=1, help=e_str)
    l_str = "Specify late de-allocated kernel intervals threshold (Default = 3). \
            If this value less than 1, then threshold = value * total_kernel_counts."
    parser.add_argument('-l', type=int, required=False, default=1, help=l_str)
    t_str = "Specify temporary idle kernel intervals threshold (Default = 3). \
            If this value less than 1, then threshold = value * total_kernel_counts."
    parser.add_argument('-t', type=float, required=False, default=1, help=l_str)
    p_str = "Specify path to memory_liveness (Required)"
    parser.add_argument('-p', '--path', type=str, required=True, help=p_str)

    args = parser.parse_args()

    threshold = [args.e, args.l, args.t]
    liveness_path = args.path

    main(liveness_path, threshold)