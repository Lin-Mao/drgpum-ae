# DrGPUM Artifact Evaluation

**No need to clone this repository, just follow the instruction step by step.**


**Public Archived Address: https://doi.org/10.5281/zenodo.7588406**

**Open-source repository: https://github.com/Lin-Mao/DrGPUM**

## Setup Artifact Outside Docker

* Download packages

```shell
# download link
pip install gdown
gdown https://drive.google.com/uc?id=1HgeS4rbGX4oik16UhqhGIwjUkUOq_3kC
gdown https://drive.google.com/uc?id=1dRqtDBegC4KTfZdOCUWuSKuJufgz2VpG
```

* If 7za if not available in the system
```shell
apt install -y p7zip-full
# or spack install p7zip
```

* Decompress packages
```shell
7za x docker_drgpum_home.7z
7za x drgpum_ae_image.tar.7z
```

* Setup and launch docker

```shell
docker load -i drgpum_ae_image.tar
docker run --rm --runtime=nvidia -it -v `pwd`/docker_drgpum_home:/root  drgpum_ae
```

## Reproduce Results in Docker

* Setup environment [~4hrs]

  ```shell
  cd root/
  # [gpu_arch]=80 if you are using A100
  # [gpu_arch]=86 if you are using RTX 3090
  ./scripts/install.sh [gpu_arch]
  ```

* Reproduce memory peak reduction in Table 4 and inefficiency pattern detection in Table 1 (1 hour)

  ```shell
  cd /root
  ./scripts/tables.sh
  cat ./results/memory_peak.txt
  cat ./results/pattens.txt
  ```

* Reproduce overhead in Figure 6 (4 hour). It will generate an `overhead.pdf` file under `/root/results/`.

  ```shell
  cd /root
  ./scripts/overhead.sh
  ```

* Reproduce DrGPUM GUI in Figure 7 (5 minutes). It will generate an `liveness.json` file under`/root/results/`. DrGPUM is built atop an existing web-based graphical interface, Perfetto. To view DrGPUM GUI on Perfetto (https://ui.perfetto.dev/). Click `[Open trace file]` in the left panel of Perfetto, then upload the `liveness.json`.

  ```shell
  cd /root
  ./scripts/generate_gui.sh
  ```

We expect the reproduced results for Table 1, Table 4, Figure 6, and Figure 7 to match the results in the paper. Table 1 shows the inefficiency patterns of different applications. Table 4 shows the memory peak reductions of applications. Figure 6 shows the profiling overhead of DrGPUM and Figure 7 shows the DrGPUM GUI example of SimpleMultiCopy.

## An example of evaluation process

The following content is an example of evaluation copied from the terminal in an as-is way (On RTX 3090).

```shell
# $ represents command prompt
$ cd /root
$ ./scripts/install 86

................ Lots of compilation info output ................

$ ./scripts/tables.sh
##########################################################################
##         Program   start  at  Sat Feb 11 14:39:23 EST 2023            ##
##         Estimated to end at  Sat Feb 11 15:39:23 EST 2023            ##
##                  May vary from machine to machine.                   ##
##########################################################################
------------------------------ profiling ---------------------------------
--------------------------- Darknet analyzing ----------------------------
--------------------------- miniMDock analyzing --------------------------
--------------------------- XSBench analyzing ----------------------------
--------------------------- huffman analyzing ----------------------------
--------------------------- dwt2d analyzing ------------------------------
--------------------------- 2MM analyzing --------------------------------
--------------------------- 3MM analyzing --------------------------------
--------------------------- GRAMSCHM analyzing ---------------------------
--------------------------- BICG analyzing -------------------------------
---------------------------- Pytorch analyzing ---------------------------
----------------------- simpleMultiCopy analyzing ------------------------
--------------------------- analyzing patterns ---------------------------
-------------------- reporting memory preak reduction --------------------
--------------------------- analyzing speedup ----------------------------
---------------------------------- done ----------------------------------

$ cat ./results/memory_peak.txt
Darknet ori current_memory_peak: 1235348452 B
Darknet opt current_memory_peak: 214054024 B
Darknet memory peak reduction: 0.83
----------------------------------------
miniMDock ori current_memory_peak: 1627441144 B
miniMDock opt current_memory_peak: 578941944 B
miniMDock memory peak reduction: 0.64
----------------------------------------
XSBench ori current_memory_peak: 2248949 B
XSBench opt current_memory_peak: 822969 B
XSBench memory peak reduction: 0.63
----------------------------------------
Huffman ori current_memory_peak: 6301704 B
Huffman opt current_memory_peak: 2107392 B
Huffman memory peak reduction: 0.67
----------------------------------------
Dwt2d ori current_memory_peak: 1142784 B
Dwt2d opt current_memory_peak: 589824 B
Dwt2d memory peak reduction: 0.48
----------------------------------------
2MM ori current_memory_peak: 83886080 B
2MM opt current_memory_peak: 50331648 B
2MM memory peak reduction: 0.40
----------------------------------------
3MM ori current_memory_peak: 7340032 B
3MM opt current_memory_peak: 3145728 B
3MM memory peak reduction: 0.57
----------------------------------------
GRAMSCHM ori current_memory_peak: 50331648 B
GRAMSCHM opt current_memory_peak: 33562624 B
GRAMSCHM memory peak reduction: 0.33
----------------------------------------
Pytorch ori current_submemory_peak: 52198912 B
Pytorch opt current_submemory_peak: 51399168 B
Pytorch memory peak reduction: 0.02
----------------------------------------
simpleMultiCopy ori current_memory_peak: 2147483648 B
simpleMultiCopy opt current_memory_peak: 1073741824 B
simpleMultiCopy memory peak reduction: 0.50
----------------------------------------
GRAMSCHM ori elapsed time 2017.2586 ms
GRAMSCHM opt elapsed time 1423.7474 ms
GRAMSCHM speedup: 1.42X
----------------------------------------
BICG ori elapsed time 1926.9072 ms
BICG opt elapsed time 890.054 ms
BICG speedup: 2.16X
----------------------------------------

$ cat ./results/pattens.txt
-------- darknet --------
early allocation pattern:        431 object(s)
late de-allocation pattern:      429 object(s)
temporary idle pattern:          150 object(s)
unused allocation pattern:       375 object(s)
redundant allocation pattern:    372 object(s)
dead write pattern:              327 object(s)
memory leak pattern:             4 object(s)
-------- miniMDock --------
early allocation pattern:        4 object(s)
late de-allocation pattern:      11 object(s)
temporary idle pattern:          12 object(s)
unused allocation pattern:       6 object(s)
-------- XSBench --------
memory leak pattern:             7 object(s)
-------- Huffman --------
early allocation pattern:        3 object(s)
late de-allocation pattern:      5 object(s)
temporary idle pattern:          5 object(s)
unused allocation pattern:       3 object(s)
redundant allocation pattern:    3 object(s)
-------- Dwt2d --------
early allocation pattern:        3 object(s)
late de-allocation pattern:      4 object(s)
temporary idle pattern:          2 object(s)
unused allocation pattern:       1 object(s)
redundant allocation pattern:    2 object(s)
dead write pattern:              2 object(s)
-------- 2MM --------
early allocation pattern:        2 object(s)
late de-allocation pattern:      2 object(s)
redundant allocation pattern:    4 object(s)
-------- 3MM --------
early allocation pattern:        4 object(s)
late de-allocation pattern:      4 object(s)
temporary idle pattern:          1 object(s)
redundant allocation pattern:    6 object(s)
-------- GRAMSCHM --------
early allocation pattern:        1 object(s)
late de-allocation pattern:      3 object(s)
temporary idle pattern:          1 object(s)
-------- BICG --------
early allocation pattern:        2 object(s)
late de-allocation pattern:      2 object(s)
redundant allocation pattern:    3 object(s)
-------- Pytorch --------
early allocation pattern:        1 object(s)
temporary idle pattern:          2 object(s)
unused allocation pattern:       4 object(s)
dead write pattern:              1 object(s)
memory leak pattern:             7 object(s)
-------- simpleMultiCopy --------
early allocation pattern:        6 object(s)
late de-allocation pattern:      6 object(s)
temporary idle pattern:          8 object(s)
dead write pattern:              3 object(s)

$ ./scripts/overhead.sh
##########################################################################
##         Program   start  at  Sat Feb 11 18:29:07 EST 2023            ##
##         Estimated to end at  Sat Feb 11 22:29:07 EST 2023            ##
##                  May vary from machine to machine.                   ##
##########################################################################
-------------------------- original executing ----------------------------
------------------------- object-level analyzing -------------------------
---------------------- intra-object-level analyzing ----------------------
-------------------------- overhead analyzing ----------------------------
---------------------------------- done ----------------------------------

$ ls results/overhead.pdf
results/overhead.pdf

$ ./scripts/generate_gui.sh
---------------------------------- done ----------------------------------

$ ls results/liveness.json
results/liveness.json
```
