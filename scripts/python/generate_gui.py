#!/usr/bin/env python
import os
import re
import argparse
import json

JSON_BUFFER = list()

def check_path(path):
    """
    Check path legality
    :param path: path to memory_liveness folder
    """
    file_list = os.listdir(path)
    memory_liveness = "memory_liveness.txt" in file_list
    kernel_list = "kernel_list.txt" in file_list
    memory_size_list = "memory_size_list.txt" in file_list
    operation_stream_info = "operation_stream_info.txt" in file_list
    topological_order = "topological_order.txt" in file_list
    liveness_csv = "memory_liveness.csv" in file_list
    callpath = "memory_liveness.csv.context" in file_list

    if not memory_liveness or not kernel_list or not memory_size_list or not operation_stream_info \
            or not topological_order or not liveness_csv or not callpath:
        print("An illegal Path!(Specify path to memory liveness folder)")
        exit()


######################################## Patterns ########################################
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


def check_reusable_objects(memory_access, path, pattern_result):
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

    return pattern_result


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

    pattern_result = {}  # {memory: [pattern1, pattern2, ...]
    memory_access = {}  # {memory: [first, last]}

    file2 = open(os.path.join(path, "memory_liveness.txt"))
    line = file2.readline()  # filter the first object created by tool
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

        temporary_inefficient_distance = 0
        early_inefficient_distance = 0
        late_inefficient_distance = 0
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
                        temporary_inefficient_distance = get_interval(access_id, last_id, kernel_list)
                        temporary_idle = True
                access_id = last_id
                if first_id == 0:
                    first_id = last_id

            elif int(nums[i + 1]) == 5:
                free_id = int(nums[i])

        if first_id == 0:
            patterns.append("whole-program idle")
        if free_id == 0:
            patterns.append("memory leak")
        if temporary_idle:
            patterns.append("temporary idle")
        if dead_write:
            patterns.append("dead write")
        if get_interval(alloc_id, first_id, kernel_list) >= int(early_threshold):
            early_inefficient_distance = get_interval(alloc_id, first_id, kernel_list)
            patterns.append("early allocation")
        if get_interval(last_id, free_id, kernel_list) >= int(late_threshold):
            if not last_id == 0:
                late_inefficient_distance = get_interval(last_id, free_id, kernel_list)
                patterns.append("late de-allocation")

        if not first_id == 0:
            memory_access[int(nums[0])] = [first_id, last_id]
        patterns.append([early_inefficient_distance, temporary_inefficient_distance, late_inefficient_distance])
        pattern_result[int(nums[0])] = patterns
        line = file2.readline()
    file2.close()

    return pattern_result, memory_access


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


def detect_patterns(path, threshold):
    kernel_list, kernel_count = get_kernel_list(path)
    pattern_result, memory_access = get_patterns(path, threshold, kernel_list, kernel_count)

    return pattern_result, memory_access


######################################## Call Path ########################################
def op_ctx_mapping(path):
    """
    Get the mapping of op_id and ctx_id
    """
    op_ctx = {} # {op_id: ctx_id}
    file = open(os.path.join(path, "memory_liveness.csv"))
    line = file.readline()
    while line:
        if "op_id" in line:
            nums = re.findall(r"\d+\.?\d*", line)
            op_ctx[int(nums[0])] = int(nums[1])
        line = file.readline()
    file.close()

    # print(op_ctx)
    return op_ctx


def process_call_path(path):
    """
    Get the call path of each ctx_id
    """
    call_path = {}  # {ctx_id: [line0, line1, ...]}
    code_lines = []
    ctx_id = 0

    file = open(os.path.join(path, "memory_liveness.csv.context"))
    line = file.readline()
    while line:
        if "count(s)" in line:
            num = re.findall(r"\d+\.?\d*", line)
            ctx_id = int(num[0])

            line = file.readline()
            while not("gpu_op_" in line or "cudart" in line or not line.strip()):
                code_lines.append(line.strip('\n'))
                line = file.readline()
        if ctx_id != 0:
            call_path[ctx_id] = code_lines
            code_lines = []
            ctx_id = 0
        line = file.readline()
    file.close()

    # print(call_path)
    return call_path


def get_call_path(path):
    return op_ctx_mapping(path), process_call_path(path)

######################################## GUI ########################################
def parse_timeline_map(path, n_digits):
    """
    Read and parse the memory_liveness.txt, store the timeline info into operation_dict
    :param path: path to memory_liveness folder
    :return: operation_dict: map of liveness info
             sub_time: the op_id offset for better display (used for naming)
             init_time: start time in GUI (used for timing)
    """
    operation_dict = {}
    file = open(os.path.join(path, "memory_liveness.txt"))
    line = file.readline()
    truncation = pow(10, n_digits)
    nums = re.findall(r"\d+\.?\d*", line)
    sub_time = int(int(nums[0]) / truncation) * truncation
    init_time = int(nums[0]) - 3
    line = file.readline()
    while line:
        nums = re.findall(r"\d+\.?\d*", line)
        length = len(nums)
        temp = []
        for i in range(1, len(nums), 2):
            temp.append(int(nums[i]) - init_time)
            temp.append(int(nums[i + 1]))
            temp.append(int(nums[i]) - sub_time)
        # print(temp)
        operation_dict[int(nums[0]) - sub_time] = temp
        line = file.readline()
    file.close()
    # print(operation_dict)
    return operation_dict, sub_time, init_time


def op_stream_mapping(path):
    op2stream = dict()  # op_id : stream_id
    stream2op = dict()  # stream: op_ids
    streams = set()  # stream_id

    file = open(os.path.join(path, "operation_stream_info.txt"))
    line = file.readline()
    while line:
        nums = re.findall(r"\d+\.?\d*", line)
        op2stream[int(nums[0])] = int(nums[len(nums) - 1])
        streams.add(int(nums[len(nums) - 1]))
        if int(nums[len(nums) - 1]) not in stream2op.keys():
            stream2op[int(nums[len(nums) - 1])] = list()
            stream2op[int(nums[len(nums) - 1])].append(int(nums[0]))
        else:
            stream2op[int(nums[len(nums) - 1])].append(int(nums[0]))
        line = file.readline()
    file.close()

    return op2stream, stream2op, streams


def op_index_mapping(path, streams, op2stream):
    op2index = dict()   # op_id : intra_stream_index
    op2type = dict() # op_id : op_type

    intra_stream_index = dict()
    streams_index = {0: 0, 1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
    for s in streams:
        intra_stream_index[s] = streams_index

    file = open(os.path.join(path, "memory_liveness.csv"))
    line = file.readline()
    while line:
        nums = re.findall(r"\d+\.?\d*", line)
        if len(nums) != 2:
            line = file.readline()
            continue
        stream_id = op2stream[int(nums[0])]
        if "ALLOC" in line:
            op2type[int(nums[0])] = 0
            intra_stream_index[stream_id][0] += 1
            op2index[int(nums[0])] = intra_stream_index[stream_id][0]
        elif "SET" in line:
            op2type[int(nums[0])] = 1
            intra_stream_index[stream_id][1] += 1
            op2index[int(nums[0])] = intra_stream_index[stream_id][1]
        elif "COPYT" in line:
            op2type[int(nums[0])] = 2
            intra_stream_index[stream_id][2] += 1
            op2index[int(nums[0])] = intra_stream_index[stream_id][2]
        elif "COPYF" in line:
            op2type[int(nums[0])] = 3
            intra_stream_index[stream_id][3] += 1
            op2index[int(nums[0])] = intra_stream_index[stream_id][3]
        elif "ACCESS" in line:
            op2type[int(nums[0])] = 4
            intra_stream_index[stream_id][4] += 1
            op2index[int(nums[0])] = intra_stream_index[stream_id][4]
        elif "FREE" in line:
            op2type[int(nums[0])] = 5
            intra_stream_index[stream_id][5] += 1
            op2index[int(nums[0])] = intra_stream_index[stream_id][5]
        line = file.readline()
    file.close()

    return op2index, op2type


def op_time_mapping(path):
    op2timestamp = dict()   # op_id : timestamp

    file = open(os.path.join(path, "topological_order.txt"))
    line = file.readline()
    while line:
        nums = re.findall(r"\d+\.?\d*", line)
        if len(nums) == 2:
            op2timestamp[int(nums[0])] = int(nums[1])
        line = file.readline()
    file.close()

    return op2timestamp


def process_apis(streams, stream2op, op2type, op2index, op2timestamp):
    for s in streams:
        for op in stream2op[s]:
            if op2type[op] == 0:
                JSON_BUFFER.append({
                    "pid": 0, "tid": s,
                    "ts": op2timestamp[op],
                    "ph": "X", "cat": "A",
                    "name": "ALLOC(" + str(s) + ", " + str(op2index[op]) + ")",
                    "dur": 1
                })
            elif op2type[op] == 1:
                JSON_BUFFER.append({
                    "pid": 0,
                    "tid": s,
                    "ts": op2timestamp[op],
                    "ph": "X",
                    "cat": "S",
                    "name": "SET(" + str(s) + ", " + str(op2index[op]) + ")",
                    "dur": 1
                })
            elif op2type[op] == 2:
                JSON_BUFFER.append({
                    "pid": 0,
                    "tid": s,
                    "ts": op2timestamp[op],
                    "ph": "X",
                    "cat": "CT",
                    "name": "CPYT(" + str(s) + ", " + str(op2index[op]) + ")",
                    "dur": 1
                })
            elif op2type[op] == 3:
                JSON_BUFFER.append({
                    "pid": 0,
                    "tid": s,
                    "ts": op2timestamp[op],
                    "ph": "X",
                    "cat": "CF",
                    "name": "CPYF(" + str(s) + ", " + str(op2index[op]) + ")",
                    "dur": 1
                })
            elif op2type[op] == 4:
                JSON_BUFFER.append({
                    "pid": 0,
                    "tid": s,
                    "ts": op2timestamp[op],
                    "ph": "X",
                    "cat": "K",
                    "name": "KERL(" + str(s) + ", " + str(op2index[op]) + ")",
                    "dur": 1
                })
            elif op2type[op] == 5:
                JSON_BUFFER.append({
                    "pid": 0,
                    "tid": s,
                    "ts": op2timestamp[op],
                    "ph": "X",
                    "cat": "F",
                    "name": "FREE(" + str(s) + ", " + str(op2index[op]) + ")",
                    "dur": 1
                })
        JSON_BUFFER.append({
            "pid": 0,
            "tid": s,
            "ts": 0,
            "ph": "X",
            "cat": "M",
            "name": "thread_name",
            "args": {"name": "Stream"}
        })

    JSON_BUFFER.append({
        "pid": 0,
        "tid": 0,
        "ts": 0,
        "ph": "M",
        "cat": "__metadata",
        "name": "process_name",
        "args": {"name": "GPU Streams"}}
    )


def get_obj_size_order(path):
    obj_dict = dict()   # op_id : size

    file = open(os.path.join(path, "memory_size_list.txt"))
    line = file.readline()
    while line:
        nums = re.findall(r"\d+\.?\d*", line)
        obj_dict[int(nums[0])] = int(nums[1])
        line = file.readline()
    file.close()

    return obj_dict


def parse_obj_timeline(path):
    obj2ops = dict()     # op : [op, op, ...]
    file = open(os.path.join(path, "memory_liveness.txt"))
    line = file.readline()
    while line:
        nums = re.findall(r"\d+\.?\d*", line)
        temp = list()
        for i in range(1, len(nums), 2):
            temp.append(int(nums[i]))
        obj2ops[int(nums[0])] = temp
        line = file.readline()
    file.close()

    return obj2ops


def process_objs(obj_dict, obj2ops, op2stream, op2index, op2type, op2timestamp, op2idles,
                 pattern_result, memory_access, op_ctx, call_path):
    index = 1
    for obj in obj_dict.keys():
        for op in obj2ops[obj]:
            if op2type[op] == 0:
                args_dict = {"ID": op}
                suggestion_count = 0
                distance_count = 0
                if len(pattern_result[op]) > 1:
                    inefficiency_distance = pattern_result[op][-1]
                    patterns = [i for i in pattern_result[op][0:len(pattern_result[op])-1]]
                    args_dict["Inefficiency pattern"] = ", ".join(patterns)
                    if inefficiency_distance[0] > 0:
                        args_dict["Inefficiency distance" + str(distance_count)] = inefficiency_distance[0]
                        args_dict["Optimization suggestion" + str(suggestion_count)] = "Allocate just before KERL("\
                        "" + str(op2stream[memory_access[op][0]]) + ", " + str(op2index[memory_access[op][0]]) + ")"
                        suggestion_count += 1
                        distance_count += 1
                    if inefficiency_distance[2] > 0:
                        args_dict["Inefficiency distance" + str(distance_count)] = inefficiency_distance[2]
                        args_dict["Optimization suggestion" + str(suggestion_count)] = "Allocate just after KERL("\
                        "" + str(op2stream[memory_access[op][1]]) + ", " + str(op2index[memory_access[op][1]]) + ")"
                        suggestion_count += 1
                        distance_count += 1
                    if "whole-program idle" in patterns:
                        args_dict["Optimization suggestion" + str(suggestion_count)] = "Eliminate this object"
                        suggestion_count += 1
                        distance_count += 1
                    if "memory leak" in patterns and not "whole-program idle" in patterns:
                        args_dict["Optimization suggestion" + str(suggestion_count)] = "Add a free operation after KERL("\
                        "" + str(op2stream[memory_access[op][1]]) + ", " + str(op2index[memory_access[op][1]]) + ")"
                        suggestion_count += 1
                        distance_count += 1

                callpath = call_path[op_ctx[op]]
                callpath_count = 0
                for cp in callpath:
                    if "\t" in cp:
                        args_dict["Call path" + str(callpath_count)] = cp.replace("\t", "   ")
                    else:
                        args_dict["Call path" + str(callpath_count)] = cp
                    callpath_count += 1
                    
                JSON_BUFFER.append({
                    "pid": 1,
                    "tid": index,
                    "ts": op2timestamp[op],
                    "ph": "X",
                    "cat": "A",
                    "name": "ALLOC(" + str(op2stream[op]) + ", " + str(op2index[op]) + ")",
                    "dur": 1,
                    "args": args_dict
                })
            elif op2type[op] == 1:
                args_dict = {"ID": op}
                callpath = call_path[op_ctx[op]]
                callpath_count = 0
                for cp in callpath:
                    if "\t" in cp:
                        args_dict["Call path" + str(callpath_count)] = cp.replace("\t", "   ")
                    else:
                        args_dict["Call path" + str(callpath_count)] = cp
                    callpath_count += 1

                JSON_BUFFER.append({
                    "pid": 1,
                    "tid": index,
                    "ts": op2timestamp[op],
                    "ph": "X",
                    "cat": "S",
                    "name": "SET(" + str(op2stream[op]) + ", " + str(op2index[op]) + ")",
                    "dur": 1,
                    "args": args_dict
                })
            elif op2type[op] == 2:
                args_dict = {"ID": op}
                callpath = call_path[op_ctx[op]]
                callpath_count = 0
                for cp in callpath:
                    if "\t" in cp:
                        args_dict["Call path" + str(callpath_count)] = cp.replace("\t", "   ")
                    else:
                        args_dict["Call path" + str(callpath_count)] = cp
                    callpath_count += 1

                JSON_BUFFER.append({
                    "pid": 1,
                    "tid": index,
                    "ts": op2timestamp[op],
                    "ph": "X",
                    "cat": "CT",
                    "name": "CPYT(" + str(op2stream[op]) + ", " + str(op2index[op]) + ")",
                    "dur": 1,
                    "args": args_dict
                })
            elif op2type[op] == 3:
                args_dict = {"ID": op}
                callpath = call_path[op_ctx[op]]
                callpath_count = 0
                for cp in callpath:
                    if "\t" in cp:
                        args_dict["Call path" + str(callpath_count)] = cp.replace("\t", "   ")
                    else:
                        args_dict["Call path" + str(callpath_count)] = cp
                    callpath_count += 1

                JSON_BUFFER.append({
                    "pid": 1,
                    "tid": index,
                    "ts": op2timestamp[op],
                    "ph": "X",
                    "cat": "CF",
                    "name": "CPYF(" + str(op2stream[op]) + ", " + str(op2index[op]) + ")",
                    "dur": 1,
                    "args": args_dict
                })
            elif op2type[op] == 4:
                args_dict = {"ID": op}
                callpath = call_path[op_ctx[op]]
                callpath_count = 0
                for cp in callpath:
                    if "\t" in cp:
                        args_dict["Call path" + str(callpath_count)] = cp.replace("\t", "   ")
                    else:
                        args_dict["Call path" + str(callpath_count)] = cp
                    callpath_count += 1

                JSON_BUFFER.append({
                    "pid": 1,
                    "tid": index,
                    "ts": op2timestamp[op],
                    "ph": "X",
                    "cat": "K",
                    "name": "KERL(" + str(op2stream[op]) + ", " + str(op2index[op]) + ")",
                    "dur": 1,
                    "args": args_dict
                })
            elif op2type[op] == 5:
                args_dict = {"ID": op}
                callpath = call_path[op_ctx[op]]
                callpath_count = 0
                for cp in callpath:
                    if "\t" in cp:
                        args_dict["Call path" + str(callpath_count)] = cp.replace("\t", "   ")
                    else:
                        args_dict["Call path" + str(callpath_count)] = cp
                    callpath_count += 1

                JSON_BUFFER.append({
                    "pid": 1,
                    "tid": index,
                    "ts": op2timestamp[op],
                    "ph": "X",
                    "cat": "F",
                    "name": "FREE(" + str(op2stream[op]) + ", " + str(op2index[op]) + ")",
                    "dur": 1,
                    "args": args_dict
                })
        process_idles(op2idles, obj, index)
        JSON_BUFFER.append({
            "pid": 1,
            "tid": index,
            "ts": 0,
            "ph": "M",
            "cat": "__metadata",
            "name": "thread_name",
            "args": {"name": "Object (" + str(obj_dict[obj]) + " B)"}
        })
        index += 1
    JSON_BUFFER.append({
        "pid": 1,
        "tid": 0,
        "ts": 0,
        "ph": "M",
        "cat": "__metadata",
        "name": "process_name",
        "args": {"name": "Objects"}}
    )


def get_idle_intervals(obj2ops, op2timestamp):
    op2idles = dict()

    for obj in obj2ops.keys():
        idleness = list()
        for op in obj2ops[obj]:
            idleness.append(op2timestamp[op])
        op2idles[obj] = idleness

    return op2idles


def process_idles(op2idles, op, index):
    for t in range(len(op2idles[op]) - 1):
        gap = op2idles[op][t + 1] - op2idles[op][t]
        if gap > 1:
            JSON_BUFFER.append({
                "pid": 1,
                "tid": index,
                "ts": op2idles[op][t] + 1,
                "ph": "X",
                "cat": "IDLE",
                "name": "IDLE",
                "dur": gap - 1
            })


def main(path, num_of_objs, filename, call_path, output_path, threshold):
    check_path(path)

    op2stream, stream2op, streams = op_stream_mapping(path)

    op2index, op2type = op_index_mapping(path, streams, op2stream)

    op2timestamp = op_time_mapping(path)

    obj_dict = get_obj_size_order(path)

    obj2ops = parse_obj_timeline(path)

    op2idles = get_idle_intervals(obj2ops, op2timestamp)

    pattern_result, memory_access = detect_patterns(path, threshold)

    op_ctx, call_path = get_call_path(path)

    process_apis(streams, stream2op, op2type, op2index, op2timestamp)

    process_objs(obj_dict, obj2ops, op2stream, op2index, op2type, op2timestamp, op2idles,
                 pattern_result, memory_access, op_ctx, call_path)

    # print(len(JSON_BUFFER))
    with open(filename, 'w') as outfile:
        json.dump(JSON_BUFFER, outfile, indent=4)



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate GUI")
    parser.add_argument('-p', '--path', type=str, required=True, help="Path")
    parser.add_argument('-o', '--output_path', type=str, required=True, help="Output Path")
    parser.add_argument('-e', type=int, required=False, default=1, help="")
    parser.add_argument('-l', type=int, required=False, default=1, help="")
    parser.add_argument('-t', type=float, required=False, default=1, help="")
    args = parser.parse_args()
    path = args.path
    output_path = args.output_path

    num_of_memories = 0
    nums_of_digits = 6
    file_name = "liveness.json"
    call_path_flag = False
    threshold = [args.e, args.l, args.t]
    main(path, num_of_memories, file_name, call_path_flag, output_path, threshold)
