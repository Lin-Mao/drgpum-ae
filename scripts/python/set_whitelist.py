#!/usr/bin/env python
"""
Get mangled name and set whitelist for each kernel.
Select the kernel that accessees the most memory.
"""

import os
import sys
import re


def get_app_profiling_folder(app: str) -> str:
    if app == "darknet" or app == "miniMDock":
        profiling_folder = app + "_ori"
    # elif app == "laghos":
    #     profiling_folder = app + "_ori/Laghos"
    elif app == "XSBench":
        profiling_folder = app + "_ori/cuda"
    elif app == "huffman" or app == "dwt2d":
        profiling_folder = os.path.join("rodinia_ori", app)
    elif app == "2MM" or app == "3MM" or app == "GRAMSCHM" or app == "BICG":
        profiling_folder = os.path.join("polybench_ori", app)
    elif app == "simpleMultiCopy":
        profiling_folder = "simpleMultiCopy_ori/Samples/0_Introduction/simpleMultiCopy"
    
    return profiling_folder


def set_whitelist(profiling_path: str, mangled_name: str):
    whitelist = open(os.path.join(profiling_path, "whitelist"), "w")
    whitelist.write(mangled_name + "\n")
    whitelist.close


def get_mangled_name(app_path: str, app: str) -> str:
    kernel_op_id = ""
    mangled_name = ""

    profiling_folder = get_app_profiling_folder(app)
    csv_file_path = os.path.join(profiling_folder, "gvprof-measurements/memory_liveness/memory_liveness.csv")
    log_file_path = os.path.join(profiling_folder, "gvprof.log")

    csv_file = open(os.path.join(app_path, csv_file_path))

    line = csv_file.readline()
    # The first line should be the target.
    if "memory_peak_kernel" in line:
        nums = re.findall(r"\d+\.?\d*", line)
        kernel_op_id = nums[0]
    csv_file.close()

    log_file = open(os.path.join(app_path, log_file_path))
    line = log_file.readline()

    while line:
        if kernel_op_id in line and "Sanitizer-> Launch kernel" in line:
            line = line.split()
            mangled_name = line[3]
            break
        line = log_file.readline()
    log_file.close()

    set_whitelist(os.path.join(app_path, profiling_folder), mangled_name)

    return mangled_name


def main(argv: list):
    apps = ["darknet", "miniMDock", "XSBench", "huffman", \
        "dwt2d", "2MM", "3MM", "GRAMSCHM", "BICG", "simpleMultiCopy"]

    app_path = argv[1]
    
    mangled_name_list = list()

    for app in apps:
        mangled_name = get_mangled_name(app_path, app)
        mangled_name_list.append((app, mangled_name))

    for item in mangled_name_list:
        print("App: %s\t Mangled name: %s"%(item[0], item[1]))
        

if __name__ == "__main__":
    main(sys.argv)