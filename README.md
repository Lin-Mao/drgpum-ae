# DrGPUM Artifact Evaluation

## Setup Artifact Outside Docker

* Download packages

```shell
# download link
https://doi.org/10.5281/zenodo.7588406
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

