#!/usr/bin/env python
import os
import re
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
    operation_stream_info = "operation_stream_info.txt" in file_list
    topological_order = "topological_order.txt" in file_list

    if not memory_liveness or not kernel_list or not memory_size_list or not operation_stream_info \
            or not topological_order:
        print("An illegal Path!(Specify path to memory liveness folder)")
        exit()


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


def write_apis(file, streams, stream2op, op2type, op2index, op2timestamp):
    for s in streams:
        for op in stream2op[s]:
            if op2type[op] == 0:
                string = "{\"pid\":0,\"tid\":" + str(s) + ",\"ts\":" + str(op2timestamp[op]) + ",\"ph\":\"X\"," \
                         "\"cat\":\"A\",\"name\":\"ALLOC(" + str(s) + ", " + str(op2index[op]) + ")\",\"dur\":1},"
            elif op2type[op] == 1:
                string = "{\"pid\":0,\"tid\":" + str(s) + ",\"ts\":" + str(op2timestamp[op]) + ",\"ph\":\"X\"," \
                         "\"cat\":\"S\",\"name\":\"SET(" + str(s) + ", " + str(op2index[op]) + ")\",\"dur\":1},"
            elif op2type[op] == 2:
                string = "{\"pid\":0,\"tid\":" + str(s) + ",\"ts\":" + str(op2timestamp[op]) + ",\"ph\":\"X\"," \
                         "\"cat\":\"CT\",\"name\":\"CPYT(" + str(s) + ", " + str(op2index[op]) + ")\",\"dur\":1},"
            elif op2type[op] == 3:
                string = "{\"pid\":0,\"tid\":" + str(s) + ",\"ts\":" + str(op2timestamp[op]) + ",\"ph\":\"X\"," \
                         "\"cat\":\"CF\",\"name\":\"CPYF(" + str(s) + ", " + str(op2index[op]) + ")\",\"dur\":1},"
            elif op2type[op] == 4:
                string = "{\"pid\":0,\"tid\":" + str(s) + ",\"ts\":" + str(op2timestamp[op]) + ",\"ph\":\"X\"," \
                         "\"cat\":\"K\",\"name\":\"KERL(" + str(s) + ", " + str(op2index[op]) + ")\",\"dur\":1},"
            elif op2type[op] == 5:
                string = "{\"pid\":0,\"tid\":" + str(s) + ",\"ts\":" + str(op2timestamp[op]) + ",\"ph\":\"X\"," \
                         "\"cat\":\"F\",\"name\":\"FREE(" + str(s) + ", " + str(op2index[op]) + ")\",\"dur\":1},"
            file.write(string + "\n")
        meta_str = "{\"pid\":0,\"tid\":" + str(s) + ",\"ts\":0,\"ph\":\"M\",\"cat\":\"__metadata\",\"name\":\"" \
                   "thread_name\",\"args\":{\"name\":\"Stream\"}},"
        file.write(meta_str + "\n")
    meta_str = "{\"pid\":0,\"tid\":0,\"ts\":0,\"ph\":\"M\",\"cat\":\"__metadata\",\"name\":\"" \
               "process_name\",\"args\":{\"name\":\"GPU Streams\"}},"
    file.write(meta_str + "\n")


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


def write_objs(file, obj_dict, obj2ops, op2stream, op2index, op2type, op2timestamp, op2idles):
    index = 1
    for obj in obj_dict.keys():
        for op in obj2ops[obj]:
            if op2type[op] == 0:
                string = "{\"pid\":1,\"tid\":" + str(index) + ",\"ts\":" + str(op2timestamp[op]) + ",\"ph\":\"X\"," \
                         "\"cat\":\"A\",\"name\":\"ALLOC(" + str(op2stream[op]) + ", " + str(op2index[op]) + ")\"," \
                         "\"dur\":1,\"args\":{\"ID\":" + str(op) + "}},"
            elif op2type[op] == 1:
                string = "{\"pid\":1,\"tid\":" + str(index) + ",\"ts\":" + str(op2timestamp[op]) + ",\"ph\":\"X\"," \
                         "\"cat\":\"S\",\"name\":\"SET(" + str(op2stream[op]) + ", " + str(op2index[op]) + ")\"," \
                         "\"dur\":1,\"args\":{\"ID\":" + str(op) + "}},"
            elif op2type[op] == 2:
                string = "{\"pid\":1,\"tid\":" + str(index) + ",\"ts\":" + str(op2timestamp[op]) + ",\"ph\":\"X\"," \
                         "\"cat\":\"CT\",\"name\":\"CPYT(" + str(op2stream[op]) + ", " + str(op2index[op]) + ")\"," \
                         "\"dur\":1,\"args\":{\"ID\":" + str(op) + "}},"
            elif op2type[op] == 3:
                string = "{\"pid\":1,\"tid\":" + str(index) + ",\"ts\":" + str(op2timestamp[op]) + ",\"ph\":\"X\"," \
                         "\"cat\":\"CF\",\"name\":\"CPYF(" + str(op2stream[op]) + ", " + str(op2index[op]) + ")\"," \
                         "\"dur\":1,\"args\":{\"ID\":" + str(op) + "}},"
            elif op2type[op] == 4:
                string = "{\"pid\":1,\"tid\":" + str(index) + ",\"ts\":" + str(op2timestamp[op]) + ",\"ph\":\"X\"," \
                         "\"cat\":\"K\",\"name\":\"KERL(" + str(op2stream[op]) + ", " + str(op2index[op]) + ")\"," \
                         "\"dur\":1,\"args\":{\"ID\":" + str(op) + "}},"
            elif op2type[op] == 5:
                string = "{\"pid\":1,\"tid\":" + str(index) + ",\"ts\":" + str(op2timestamp[op]) + ",\"ph\":\"X\"," \
                         "\"cat\":\"F\",\"name\":\"FREE(" + str(op2stream[op]) + ", " + str(op2index[op]) + ")\"," \
                         "\"dur\":1,\"args\":{\"ID\":" + str(op) + "}},"
            file.write(string + "\n")
        write_idles(file, op2idles, obj, index)
        meta_str = "{\"pid\":1,\"tid\":" + str(index) + ",\"ts\":0,\"ph\":\"M\",\"cat\":\"__metadata\",\"name\":\"" \
                   "thread_name\",\"args\":{\"name\":\"Object (" + str(obj_dict[obj]) + "B)\"}},"
        file.write(meta_str + "\n")
        index += 1
    meta_str = "{\"pid\":1,\"tid\":0,\"ts\":0,\"ph\":\"M\",\"cat\":\"__metadata\",\"name\":\"" \
               "process_name\",\"args\":{\"name\":\"Objects\"}},"
    file.write(meta_str + "\n")


def get_idle_intervals(obj2ops, op2timestamp):
    op2idles = dict()

    for obj in obj2ops.keys():
        idleness = list()
        for op in obj2ops[obj]:
            idleness.append(op2timestamp[op])
        op2idles[obj] = idleness

    return op2idles


def write_idles(file, op2idles, op, index):
    for t in range(len(op2idles[op]) - 1):
        gap = op2idles[op][t + 1] - op2idles[op][t]
        if gap > 1:
            idle_str = "{\"pid\":1,\"tid\":" + str(index) + ",\"ts\":" + str(op2idles[op][t] + 1) + ",\"ph\":\"X\"," \
                       "\"cat\":\"IDLE\",\"name\":\"" + "IDLE\",\"dur\":" + str(gap - 1) + "},"
            file.write(idle_str + "\n")


def main(path, num_of_objs, filename, call_path, output_path):
    check_path(path)

    op2stream, stream2op, streams = op_stream_mapping(path)

    op2index, op2type = op_index_mapping(path, streams, op2stream)

    op2timestamp = op_time_mapping(path)

    obj_dict = get_obj_size_order(path)

    obj2ops = parse_obj_timeline(path)

    op2idles = get_idle_intervals(obj2ops, op2timestamp)

    file = open(os.path.join(output_path, filename), "w")
    file.write("[")
    write_apis(file, streams, stream2op, op2type, op2index, op2timestamp)
    write_objs(file, obj_dict, obj2ops, op2stream, op2index, op2type, op2timestamp, op2idles)
    file.write("]")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate GUI")
    parser.add_argument('-p', '--path', type=str, required=True, help="Path")
    parser.add_argument('-o', '--output_path', type=str, required=True, help="Output Path")
    args = parser.parse_args()
    path = args.path
    output_path = args.output_path

    num_of_memories = 0
    nums_of_digits = 6
    file_name = "liveness.json"
    call_path_flag = False
    main(path, num_of_memories, file_name, call_path_flag, output_path)
