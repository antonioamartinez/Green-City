### build docker image
```
docker build --no-cache -t greencity-tree-location .
```

### to run docker image
```
docker run --gpus all --ipc=host --ulimit memlock=-1 --ulimit stack=67108864 -it -v $HOME:/workspace/data greencity-tree-location
```

### inside of docker image
#### Train & Inference

```
cd /workspace/data

git clone https://github.com/fengchenUCB/greencity-tree-location.git

cd /workspace/data/greencity-tree-location

bash run_gpu_train_inference-demo.sh

bash run_gpu_pretrained_inference-demo.sh
```
