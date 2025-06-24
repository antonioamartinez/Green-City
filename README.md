# Green-City
Urban Tree Canopy Monitor
# 0.  make sure your 4096-px tiles live in tile_cache/

# 1.  convert pseudo-labels → CSV
python 01_prepare_pseudo_dataset.py \
    --pseudo_geojson prediction_geojson.geojson \
    --tiles_dir tile_cache \
    --out_csv pseudo_train.csv \
    --score_thresh 0.2

# (optionally add one or more --extra_geojson my_hand_labels.geojson)

# 2.  fine-tune
python 02_finetune_deepforest.py \
    --csv pseudo_train.csv \
    --root_dir tile_cache \
    --weights_out pasadena_finetuned.pth \
    --epochs 6

# 3.  batch inference
python 03_predict_tile_folder.py \
    --tile_dir tile_cache \
    --weights pasadena_finetuned.pth \
    --out pasadena_predictions.geojson \
    --patch_size 1024 --overlap 0.10 --nms_thresh 0.40 --score_thresh 0.20

# 4.  (optional) evaluation against a hand-checked set
python 04_evaluate_iou.py \
    --gt_geojson pasadena_val_human.geojson \
    --pred_geojson pasadena_predictions.geojson \
    --out_csv metrics_pasadena.csv
