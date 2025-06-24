#!/usr/bin/env python
"""
Fine-tune the DeepForest release model on pseudo-labels + optional hand labels.
Backbone layers are frozen by default (requires_grad_(False)).
"""
from __future__ import annotations
import argparse, os, random, shutil, tempfile
import pandas as pd
import torch
from deepforest import main


def train_val_split(
    csv_file: str, val_pct: float, seed: int = 42
) -> tuple[str, str, str]:
    df = pd.read_csv(csv_file)
    tiles = df.image_path.unique()
    random.Random(seed).shuffle(tiles)

    val_tiles = set(tiles[: int(len(tiles) * val_pct)])
    train_df = df[~df.image_path.isin(val_tiles)]
    val_df = df[df.image_path.isin(val_tiles)]

    tmpdir = tempfile.mkdtemp()
    train_csv = os.path.join(tmpdir, "train.csv")
    val_csv = os.path.join(tmpdir, "val.csv")
    train_df.to_csv(train_csv, index=False)
    val_df.to_csv(val_csv, index=False)
    return train_csv, val_csv, tmpdir


def finetune(
    train_csv: str,
    val_csv: str,
    root_dir: str,
    epochs: int,
    weights_out: str,
    freeze_backbone: bool,
) -> None:
    model = main.deepforest()
    # modern API (same weights as use_release, no deprecation warning)
    model.load_model(
        "weecology/deepforest-tree"
    )  # :contentReference[oaicite:3]{index=3}

    # Freeze backbone if requested
    if freeze_backbone:
        model.model.backbone.requires_grad_(
            False
        )  # official transfer-learning recipe :contentReference[oaicite:4]{index=4}

    cfg = model.config
    cfg["train"]["csv_file"] = train_csv
    cfg["train"]["root_dir"] = root_dir
    cfg["validation"]["csv_file"] = val_csv
    cfg["validation"]["root_dir"] = root_dir
    cfg["epochs"] = epochs

    model.create_trainer()
    model.trainer.fit(model)

    torch.save(model.model.state_dict(), weights_out)
    print(f"Saved fine-tuned weights → {weights_out}")
    metrics = {k: float(v) for k, v in model.trainer.callback_metrics.items()}
    print("Validation metrics:", metrics)


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--csv", required=True, help="Training CSV from step 01")
    p.add_argument("--root_dir", required=True, help="Folder that holds the tiles")
    p.add_argument("--weights_out", required=True, help="Where to save the .pth")
    p.add_argument("--epochs", type=int, default=6)
    p.add_argument("--val_pct", type=float, default=0.10)
    p.add_argument(
        "--no_freeze",
        action="store_true",
        help="Un-freeze the backbone (rarely needed)",
    )
    args = p.parse_args()

    train_csv, val_csv, tmpdir = train_val_split(args.csv, args.val_pct)
    try:
        finetune(
            train_csv,
            val_csv,
            args.root_dir,
            args.epochs,
            args.weights_out,
            freeze_backbone=not args.no_freeze,
        )
    finally:
        shutil.rmtree(tmpdir)


if __name__ == "__main__":
    main()
