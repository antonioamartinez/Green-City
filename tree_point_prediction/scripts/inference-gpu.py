import argparse
import os

parser = argparse.ArgumentParser()
parser.add_argument('input', help='path to input tiff file or directory')
parser.add_argument('output', help='path to output json file or directory')
parser.add_argument('log', help='path to log directory')
parser.add_argument('--bands', default='RGBN', help='input bands')
parser.add_argument('--tile_size', type=int, default=2048, help='tile size')
parser.add_argument('--overlap', type=int, default=32, help='overlap between tiles')
parser.add_argument('--gpu_id', type=int, default=0, help='GPU ID to use (0 to num_gpus-1)')
parser.add_argument('--num_gpus', type=int, default=1, help='Total number of GPUs')
args = parser.parse_args()

os.environ['CUDA_VISIBLE_DEVICES'] = str(args.gpu_id)

import numpy as np
from models import SFANet
from utils.preprocess import *
from utils.inference import run_tiled_inference
import yaml
import rasterio
import tqdm
from tqdm import trange
import glob

def main():
    params_path = os.path.join(args.log, 'params.yaml')
    if os.path.exists(params_path):
        with open(params_path, 'r') as f:
            params = yaml.safe_load(f)
            mode = params['mode']
            min_distance = params['min_distance']
            threshold_abs = params['threshold_abs'] if mode == 'abs' else None
            threshold_rel = params['threshold_rel'] if mode == 'rel' else None
    else:
        print(f'warning: params.yaml missing -- using default params')
        min_distance = 1
        threshold_abs = None
        threshold_rel = 0.2
    
    weights_path = os.path.join(args.log, 'weights.best.h5')
    padded_size = args.tile_size + args.overlap * 2
    preprocess = eval(f'preprocess_{args.bands}')
    training_model, model = SFANet.build_model((padded_size, padded_size, len(args.bands)), preprocess_fn=preprocess)
    training_model.load_weights(weights_path)
    
    if os.path.isdir(args.input):
        os.makedirs(args.output, exist_ok=True)
        paths = sorted(glob.glob(os.path.join(args.input, '*.tif')) + glob.glob(os.path.join(args.input, '*.tiff')))
        # Distribute images across GPUs
        paths = [p for i, p in enumerate(paths) if i % args.num_gpus == args.gpu_id]
        pbar = tqdm.tqdm(total=len(paths))
        for input_path in paths:
            output_path = os.path.join(args.output, os.path.basename(input_path).split('.')[0] + '.json')
            if not os.path.exists(output_path):
                run_tiled_inference(model, input_path, output_path, min_distance=min_distance, threshold_abs=threshold_abs, threshold_rel=threshold_rel)
            pbar.update(1)
    else:
        run_tiled_inference(model, args.input, args.output, min_distance=min_distance, threshold_abs=threshold_abs, threshold_rel=threshold_rel)

if __name__ == '__main__':
    main()