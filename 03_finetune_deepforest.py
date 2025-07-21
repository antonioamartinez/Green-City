#!/usr/bin/env python3
"""
1. Split annotations into train/val
2. Override the mAP metric to allow up to 500 detections
3. Fine-tune DeepForest (backbone unfrozen) for N epochs
   with:
     • per-batch loss logged w/ batch_size
     • RetinaNet anchors ≈ 22 px
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

# ── NEW: speed-up matmul on Tensor-Core GPUs ────────────────────────────────
torch.set_float32_matmul_precision("high")

warnings.filterwarnings(
    "ignore",
    message="The behavior of DataFrame concatenation with empty or all-NA entries is deprecated.*",
    category=FutureWarning,
)


class PrintAndLogLossCallback(Callback):
    """Prints each training-batch loss *and* logs it with batch_size."""

    def on_train_batch_end(
        self,
        trainer,
        pl_module,
        outputs,
        batch,
        batch_idx: int,
        dataloader_idx: int = 0,
    ):
        loss = outputs["loss"] if isinstance(outputs, dict) else outputs
        pl_module.log("train_loss", loss, batch_size=len(batch[0]))
        # Uncomment for verbose printing:
        # print(f"[{trainer.current_epoch:02d} • {batch_idx:04d}] loss={loss.item():.4f}")


# ─────────────────────────  data split  ──────────────────────────────────────
def train_val_split(csv_file: str, val_pct: float, seed: int = 42):
    df0 = pd.read_csv(csv_file, header=0)
    tiles = df0["image_path"].unique().tolist()
    random.Random(seed).shuffle(tiles)
    n_val = int(len(tiles) * val_pct)
    val_tiles = set(tiles[:n_val])

    df0[~df0.image_path.isin(val_tiles)].to_csv("train.csv", index=False)
    df0[df0.image_path.isin(val_tiles)].to_csv("val.csv", index=False)
    return "train.csv", "val.csv"


# ─────────────────────────  fine-tune  ───────────────────────────────────────
def finetune(
    train_csv: str, val_csv: str, root_dir: str, epochs: int, weights_out: str
):
    model = df.deepforest()
    model.load_model("weecology/deepforest-tree")

    # mAP up to 500 detections
    model.mAP_metric = MeanAveragePrecision(max_detection_thresholds=[1, 10, 500])

    # unfreeze backbone
    model.model.backbone.requires_grad_(True)

    # detection thresholds
    model.config["retinanet"]["score_thresh"] = 0.2
    model.config["nms_thresh"] = 0.3

    # anchors ~22 px on first three FPN levels
    ag = model.model.anchor_generator
    ag.sizes = ((8,), (16,), (32,), ag.sizes[3], ag.sizes[4])
    ag.aspect_ratios = ((1.0,),) * 3 + ag.aspect_ratios[3:]

    # point config to our data
    cfg = model.config
    cfg["train"].update(csv_file=train_csv, root_dir=root_dir, epochs=epochs)
    cfg["validation"].update(csv_file=val_csv, root_dir=root_dir)

    # create Trainer & add callback
    model.create_trainer()
    model.trainer.callbacks.append(PrintAndLogLossCallback())

    # patch ReduceLROnPlateau min_lrs if they’re strings or zero
    for sch_cfg in model.trainer.lr_scheduler_configs:
        sched = sch_cfg.scheduler
        if isinstance(sched, ReduceLROnPlateau):
            # eps might come in as str
            if isinstance(sched.eps, str):
                sched.eps = float(sched.eps)

            # min_lrs is a list (one per param group)
            sched.min_lrs = [
                1e-6 if (isinstance(lr, str) and lr.strip()) else float(lr) or 1e-6
                for lr in sched.min_lrs
            ]
            print(f"[patch] ReduceLROnPlateau min_lrs → {sched.min_lrs}")

    # train
    model.trainer.fit(model)

    # save checkpoint
    os.makedirs(os.path.dirname(weights_out) or ".", exist_ok=True)
    torch.save(model.model.state_dict(), weights_out)
    print(f"✓ Saved fine-tuned weights → {weights_out}")

    # final metrics
    metrics = {k: float(v) for k, v in model.trainer.callback_metrics.items()}
    print("Validation metrics:", metrics)


# ────────────────────────────  CLI  ──────────────────────────────────────────
def main():
    p = argparse.ArgumentParser(
        description="Fine-tune DeepForest with custom anchors & LR patches"
    )
    p.add_argument("-a", "--annotations_csv", required=True)
    p.add_argument("-r", "--root_dir", required=True)
    p.add_argument("-o", "--weights_out", required=True)
    p.add_argument("-e", "--epochs", type=int, default=30)
    p.add_argument("-v", "--val_pct", type=float, default=0.1)
    args = p.parse_args()

    train_csv, val_csv = train_val_split(args.annotations_csv, args.val_pct)
    print(f"Training on {train_csv}, validating on {val_csv}")

    finetune(train_csv, val_csv, args.root_dir, args.epochs, args.weights_out)


if __name__ == "__main__":
    main()
