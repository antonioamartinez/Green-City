#!/usr/bin/env python3
"""
1. Split annotations into train/val
2. Override the mAP metric to allow up to 500 detections
3. Fine-tune DeepForest (backbone unfrozen) for 30 epochs
   with:
     • per-batch loss logged w/ batch_size
     • RetinaNet anchors ≈ 22px
     • score_thresh=0.2, nms_thresh=0.3
"""

import argparse
import os
import random
import pandas as pd
import warnings
import torch
from deepforest import main as df
from torchmetrics.detection.mean_ap import MeanAveragePrecision
from pytorch_lightning.callbacks import Callback
from torch.optim.lr_scheduler import ReduceLROnPlateau

warnings.filterwarnings(
    "ignore",
    message="The behavior of DataFrame concatenation with empty or all-NA entries is deprecated.*",
    category=FutureWarning,
)


class PrintAndLogLossCallback(Callback):
    """
    Prints each training-batch loss AND logs it with batch_size,
    so Lightning’s epoch-aggregation is correct.
    """

    def on_train_batch_end(
        self, trainer, pl_module, outputs, batch, batch_idx, dataloader_idx=0
    ):
        # extract loss scalar
        loss = (
            outputs["loss"]
            if isinstance(outputs, dict) and "loss" in outputs
            else outputs
        )
        loss_val = loss.item() if hasattr(loss, "item") else float(loss)
        # ── log with explicit batch_size ───────────────────────────
        pl_module.log("train_loss", loss, batch_size=len(batch[0]))
        # ── print for immediate feedback ──────────────────────────
        # print(
        #     f"[Epoch {trainer.current_epoch} • Batch {batch_idx}] loss = {loss_val:.4f}"
        # )


def train_val_split(csv_file: str, val_pct: float, seed: int = 42):
    """
    Splits a DeepForest-style CSV by UNIQUE tile into train.csv and val.csv.
    """
    df0 = pd.read_csv(csv_file, header=0)
    tiles = df0["image_path"].unique().tolist()
    random.Random(seed).shuffle(tiles)
    n_val = int(len(tiles) * val_pct)
    val_tiles = set(tiles[:n_val])

    train_df = df0[~df0.image_path.isin(val_tiles)]
    val_df = df0[df0.image_path.isin(val_tiles)]

    train_df.to_csv("train.csv", index=False)
    val_df.to_csv("val.csv", index=False)
    return "train.csv", "val.csv"


def finetune(
    train_csv: str, val_csv: str, root_dir: str, epochs: int, weights_out: str
):
    # 1. Load pretrained DeepForest
    model = df.deepforest()
    model.load_model("weecology/deepforest-tree")

    # 2. Allow up to 500 detections per image for mAP
    model.mAP_metric = MeanAveragePrecision(max_detection_thresholds=[1, 10, 500])

    # 3. Unfreeze backbone
    model.model.backbone.requires_grad_(True)

    # 4. Tweak score & NMS thresholds
    model.config["retinanet"][
        "score_thresh"
    ] = 0.2  # drop low‐confidence preds :contentReference[oaicite:2]{index=2}
    model.config["nms_thresh"] = (
        0.3  # be more aggressive in suppression :contentReference[oaicite:3]{index=3}
    )

    # 5. Adjust RetinaNet anchors to focus on ~22px objects:
    #    sizes per FPN level = (8,), (16,), (32,), rest untouched
    ag = model.model.anchor_generator  # torchvision AnchorGenerator
    ag.sizes = ((8,), (16,), (32,), ag.sizes[3], ag.sizes[4])
    ag.aspect_ratios = (
        (1.0,),
        (1.0,),
        (1.0,),
        ag.aspect_ratios[3],
        ag.aspect_ratios[4],
    )
    # This ensures the model proposes anchors at ~8,16,32px for the small crowns :contentReference[oaicite:4]{index=4}

    # 6. Point config at our data, set epochs
    cfg = model.config
    cfg["train"]["csv_file"] = train_csv
    cfg["train"]["root_dir"] = root_dir
    cfg["validation"]["csv_file"] = val_csv
    cfg["validation"]["root_dir"] = root_dir
    cfg["train"]["epochs"] = epochs

    # 7. Create Trainer & inject our callback
    model.create_trainer()
    model.trainer.callbacks.append(PrintAndLogLossCallback())
    for sched_conf in model.trainer.lr_scheduler_configs:
        sched = sched_conf.scheduler
        if isinstance(sched, ReduceLROnPlateau) and isinstance(sched.eps, str):
            sched.eps = float(sched.eps)

    # 8. Run fine‐tuning
    model.trainer.fit(model)

    # 9. Save weights + print final metrics
    weights_dir = os.path.dirname(weights_out)
    if weights_dir:
        os.makedirs(weights_dir, exist_ok=True)
    torch.save(model.model.state_dict(), weights_out)
    print(f"Saved fine‐tuned weights → {weights_out}")
    metrics = {k: float(v) for k, v in model.trainer.callback_metrics.items()}
    print("Validation metrics:", metrics)


def main():
    p = argparse.ArgumentParser(
        description="Fine-tune DeepForest: 30 epochs, score_thresh=0.2, nms_thresh=0.3"
    )
    p.add_argument(
        "-a",
        "--annotations_csv",
        required=True,
        help="CSV with header: image_path,xmin,ymin,xmax,ymax,label",
    )
    p.add_argument(
        "-r", "--root_dir", required=True, help="Directory containing 800×800 tiles"
    )
    p.add_argument(
        "-o", "--weights_out", required=True, help="Output .pth checkpoint path"
    )
    p.add_argument(
        "-e", "--epochs", type=int, default=30, help="Number of epochs (default: 30)"
    )
    p.add_argument(
        "-v",
        "--val_pct",
        type=float,
        default=0.1,
        help="Fraction of tiles for validation (default: 0.1)",
    )
    args = p.parse_args()

    train_csv, val_csv = train_val_split(args.annotations_csv, args.val_pct)
    print(f"Training on {train_csv}, validating on {val_csv}")

    finetune(train_csv, val_csv, args.root_dir, args.epochs, args.weights_out)


if __name__ == "__main__":
    main()
