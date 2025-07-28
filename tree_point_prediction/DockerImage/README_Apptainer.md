### To run Apptainer image

First, build the Apptainer container (note that building requires root privileges):

```
sudo apptainer build --force greencity-tree-location.sif Apptainer.def
```

Then, run the container interactively with NVIDIA GPU support and mount your data directory:

```
apptainer shell --nv --bind $HOME:/workspace/data greencity-tree-location.sif
```

### Inside the Apptainer container

#### Train & Inference

Once inside the container, navigate to the mounted data directory and run the inference commands:

```
cd /workspace/data

git clone https://github.com/fengchenUCB/greencity-tree-location.git

cd /workspace/data/greencity-tree-location

bash run_gpu_train_inference-demo.sh

bash run_gpu_pretrained_inference-demo.sh
```