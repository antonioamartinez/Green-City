#!/bin/bash

cd /workspace/data/greencity-tree-location

rm -rf ./pasadena_tiles_2048_32_pretrained
mkdir ./pasadena_tiles_2048_32_pretrained

# Inference with pre-trained weights
# Using detected GPUs
num_gpus=$(nvidia-smi --query-gpu=name --format=csv,noheader | wc -l)
for i in $(seq 0 $((num_gpus - 1))); do
    python -m scripts.inference-gpu-2 ./pasadena_tiles_2048_32/images ./pasadena_tiles_2048_32_pretrained/output ./pasadena_train_weights-demo --bands RGB --gpu_id "$i" --num_gpus "$num_gpus" &
done
wait
