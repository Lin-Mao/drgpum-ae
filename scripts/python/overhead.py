#!/usr/bin/env python
import re
import os
import argparse
from typing import Any

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.pyplot import MultipleLocator  # adjust y-axis scale


def parse_file(path: str, apps: dict, filename: str) -> dict:
    file = open(os.path.join(path, filename))

    line = file.readline()
    time_list = dict()
    while line:
        app = [a for a in apps.keys() if a in line]
        nums = re.findall(r"\d+\.?\d*", line)
        time_list[apps[app[0]]] = float(nums[len(nums) - 2])
        line = file.readline()
    file.close()
    return time_list


def process_data(result_path: str, apps: dict) -> dict:
    baseline = parse_file(result_path, apps, "baseline.log")
    liveness = parse_file(result_path, apps, "object_level.log")
    heatmap = parse_file(result_path, apps, "intra_object.log")

    overhead = dict()

    for i in apps.values():
        object_level_overhead = round(float(liveness[i] / baseline[i]), 3)
        intra_object_overhead = round(float(heatmap[i] / baseline[i]), 3)
        overhead[i] = (object_level_overhead, intra_object_overhead)

    return overhead


def draw_figure(output_path: str, overhead: dict) -> Any:
    labels = list()
    object_level = list()
    intra_object = list()

    for i in overhead.keys():
        labels.append(i)
        object_level.append(overhead[i][0])
        intra_object.append(overhead[i][1])

    fig, ax = plt.subplots(figsize=(15, 4))
    width = 0.2
    x = np.arange(len(labels))
    ax.bar(x - width / 2, object_level, width, edgecolor='dimgray', hatch="...", label="Object-level")
    ax.bar(x - width / 2, intra_object, width, bottom=object_level, edgecolor='dimgray', hatch='///',
           label="Intra-object")

    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=35, ha='right', fontsize=12)
    ax.set_ylabel("Slowdown Factor", fontsize=14)
    ax.legend(prop={'size': 12})
    ax.vlines([10.5], 0, 10, linestyles='dashed', colors='red')

    # y_major_locator = MultipleLocator(10)
    # ax.yaxis.set_major_locator(y_major_locator)
    # plt.xticks(rotation=45)
    # plt.margins(0.35)
    plt.subplots_adjust(bottom=0.35)
    plt.show()
    pdf = PdfPages(os.path.join(output_path, "overhead.pdf"))
    pdf.savefig(fig)
    pdf.close()


def geometric_mean(data: list) -> float:
    product = 1
    for i in data:
        product *= i
    return round(pow(product, 1 / len(data)), 5)


def get_overhead_result(overhead: dict) -> tuple:
    liveness_overhead = list()
    heatmap_overhead = list()
    for oh in overhead.values():
        liveness_overhead.append(oh[0])
        heatmap_overhead.append(oh[1])
    liveness_median = np.median(liveness_overhead)
    liveness_mean = geometric_mean(liveness_overhead)
    heatmap_median = np.median(heatmap_overhead)
    heatmap_mean = geometric_mean(heatmap_overhead)

    return liveness_median, liveness_mean, heatmap_median, heatmap_mean


def main(path, output_path):
    apps = {"darknet": "Darknet",
            # "laghos": "Laghos",
            "miniMDock": "MiniMDock",
            "XSBench": "XSBench",
            "huffman": "Rodinia/huffman",
            "dwt2d": "Rodinia/dwt2d",
            "2MM": "Polybench/2MM",
            "3MM": "Polybench/3MM",
            "GRAMSCHM": "Polybench/\nGramSchmidt",
            "BICG": "Polybench/BICG",
            "PyTorch": "PyTorch",
            "simpleMultiCopy": "simpleMultiCopy"
            }

    overhead = process_data(path, apps, )
    print(overhead)

    result = get_overhead_result(overhead)

    overhead["Geomean"] = (result[1], result[3])
    overhead["Median"] = (result[0], result[2])

    draw_figure(output_path, overhead)

    print("Object-level median overhead:\t%.2f" % round(result[0], 2))
    print("Object-level geo-mean overhead:\t%.2f" % round(result[1], 2))
    print("Intra-object median overhead:\t%.2f" % round(result[2], 2))
    print("Intra-object geo-mean overhead:\t%.2f" % round(result[3], 2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Report Patterns")
    parser.add_argument('-p', '--path', type=str, required=True, help="Path")
    parser.add_argument('-o', '--output_path', type=str, required=True, help="Output Path")
    args = parser.parse_args()
    path = args.path
    output_path = args.output_path

    main(path, output_path)