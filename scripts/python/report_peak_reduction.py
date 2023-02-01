import re
import os
import argparse



def main(path):
    apps = [
        "darknet",
        # "laghos",
        "miniMDock",
        "XSBench",
        "Huffman",
        "Dwt2d",
        "2MM",
        "3MM",
        "GRAMSCHM",
        "BICG",
        "Pytorch",
        "simpleMultiCopy"
    ]

    filename = os.path.join(path, "memory_reduction.txt")
    file = open(filename)
    line = file.readline()
    prev_app = ""
    prev_size = 0
    while line:
        words = line.split(" ")
        nums = re.findall(r"\d+\.?\d*", line)
        print(line.strip())        
        if words[0] == prev_app:
            reduction = (prev_size - int(nums[len(nums)-1])) / prev_size
            print(words[0], "memory peak reduction: {:.2f}".format(reduction))
            print("----------------------------------------")

        prev_app = words[0]
        prev_size = int(nums[len(nums)-1])
        line = file.readline()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Report Patterns")
    parser.add_argument('-p', '--path', type=str, required=True, help="Path")
    args = parser.parse_args()
    path = args.path

    main(path)