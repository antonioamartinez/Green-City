#!/bin/bash

for k in {1..2}; do

cd /workspace/data/greencity-tree-location
mkdir ./pasadena_train_hdf5

rm -rf ./pasadena_tiles_2048_32_finetuned${k}
mkdir ./pasadena_tiles_2048_32_finetuned${k}
cp ./pasadena_tiles_2048_32_finetuned-demo/* ./pasadena_tiles_2048_32_finetuned${k}/

rm -rf ./pasadena_train${k}_weights
mkdir ./pasadena_train${k}_weights

rm -rf ./pasadena_train_hdf5/dataset${k}.h5

cd ./pasadena_data_256_RGB_train_backup/
python dataset_preprocess.py --seed_m {k} --threshold 55

cd /workspace/data/greencity-tree-location
python -m scripts.prepare ./pasadena_data_256_RGB_train_backup ./pasadena_train_hdf5/dataset${k}.h5 --bands RGB

# Train
python -m scripts.train-gpu ./pasadena_train_hdf5/dataset${k}.h5 ./pasadena_train${k}_weights --epochs 200
python -m scripts.tune ./pasadena_train_hdf5/dataset${k}.h5 ./pasadena_train${k}_weights
python -m scripts.test ./pasadena_train_hdf5/dataset${k}.h5 ./pasadena_train${k}_weights

# Inference 
# Automatically detect the number of GPUs
num_gpus=$(nvidia-smi --query-gpu=name --format=csv,noheader | wc -l)

# Using detected GPUs
for i in $(seq 0 $((num_gpus - 1))); do
    python -m scripts.inference-gpu-2 ./pasadena_tiles_2048_32/images ./pasadena_tiles_2048_32_finetuned${k}/output ./pasadena_train${k}_weights --bands RGB --gpu_id "$i" --num_gpus "$num_gpus" &
done
wait

# Evaluation
cd ./pasadena_tiles_2048_32_finetuned${k}; sh merge_GeoJSON.sh; python evaluation-NEW-2.py
cd /workspace/data/greencity-tree-location

done
