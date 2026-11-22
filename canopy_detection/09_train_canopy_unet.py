#!/usr/bin/env python
"""
09_train_canopy_unet.py

Train the canopy U-Net (canopy_unet.py) on RGB tiles and canopy masks of the
same name, e.g. masks from 08_lidar_canopy_labels.py. Tiles are expected at
~0.6 m and are cut into 256 x 256 crops. The probability threshold is tuned for
F1 on the validation tiles and saved in the checkpoint.

Example:
    python 09_train_canopy_unet.py --tile_dir tiles --label_dir canopy_labels \
        --train_list train.txt --val_list val.txt --out canopy_unet.pt
"""

import argparse
import time
from pathlib import Path

import numpy as np
import rasterio
import torch
import torch.nn.functional as F

from canopy_unet import UNet, normalize, predict_prob

CROP = 256


def read_list(path, tile_dir):
    if path:
        return [l.strip() for l in open(path) if l.strip()]
    return sorted(p.stem for p in Path(tile_dir).glob("*.tif"))


def load(names, tile_dir, label_dir):
    X, Y = [], []
    for n in names:
        lab = Path(label_dir) / f"{n}.tif"
        if not lab.exists():
            continue
        with rasterio.open(Path(tile_dir) / f"{n}.tif") as r:
            img = r.read([1, 2, 3])
        with rasterio.open(lab) as r:
            m = r.read(1).astype(np.float32)
        # cut larger tiles into CROP-sized pieces; smaller tiles are skipped
        for y in range(0, img.shape[1] - CROP + 1, CROP):
            for x in range(0, img.shape[2] - CROP + 1, CROP):
                X.append(img[:, y:y + CROP, x:x + CROP])
                Y.append(m[y:y + CROP, x:x + CROP])
    return np.stack(X), np.stack(Y)


def augment(x, y):
    k = np.random.randint(4)
    x, y = torch.rot90(x, k, (2, 3)), torch.rot90(y, k, (2, 3))
    if np.random.rand() < 0.5:
        x, y = x.flip(3), y.flip(3)
    gain = 1 + 0.15 * torch.randn(x.shape[0], 3, 1, 1)
    offset = 12 * torch.randn(x.shape[0], 3, 1, 1)
    return (x.float() * gain + offset).clamp(0, 255), y


def f1(prob, Y, t):
    p, g = prob > t, Y > 0
    return 2 * (p & g).sum() / max(p.sum() + g.sum(), 1)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--tile_dir", required=True)
    ap.add_argument("--label_dir", required=True)
    ap.add_argument("--train_list", help="tile names (no extension), one per line; default all tiles")
    ap.add_argument("--val_list", required=True, help="tile names held out for early stopping and the threshold")
    ap.add_argument("--out", default="canopy_unet.pt")
    ap.add_argument("--epochs", type=int, default=40)
    ap.add_argument("--batch", type=int, default=8)
    ap.add_argument("--lr", type=float, default=2e-3)
    ap.add_argument("--base", type=int, default=24, help="U-Net width")
    ap.add_argument("--seed", type=int, default=0)
    args = ap.parse_args()

    torch.manual_seed(args.seed)
    np.random.seed(args.seed)
    val_names = read_list(args.val_list, args.tile_dir)
    train_names = [n for n in read_list(args.train_list, args.tile_dir) if n not in set(val_names)]
    Xtr, Ytr = load(train_names, args.tile_dir, args.label_dir)
    Xva, Yva = load(val_names, args.tile_dir, args.label_dir)
    print(f"train crops {len(Xtr)}, val crops {len(Xva)}", flush=True)

    model = UNet(base=args.base)
    steps = args.epochs * ((len(Xtr) + args.batch - 1) // args.batch)
    opt = torch.optim.AdamW(model.parameters(), args.lr, weight_decay=1e-4)
    sched = torch.optim.lr_scheduler.OneCycleLR(opt, args.lr, total_steps=steps)
    best = -1.0
    for ep in range(args.epochs):
        model.train()
        t0, total = time.time(), 0.0
        perm = np.random.permutation(len(Xtr))
        for i in range(0, len(Xtr), args.batch):
            j = perm[i:i + args.batch]
            x, y = augment(torch.from_numpy(Xtr[j]), torch.from_numpy(Ytr[j])[:, None])
            logits = model(normalize(x))
            p = torch.sigmoid(logits)
            dice = 1 - (2 * (p * y).sum() + 1) / (p.sum() + y.sum() + 1)
            loss = F.binary_cross_entropy_with_logits(logits, y) + dice
            opt.zero_grad()
            loss.backward()
            opt.step()
            sched.step()
            total += loss.item() * len(j)
        msg = f"epoch {ep} loss {total / len(Xtr):.3f} {time.time() - t0:.0f}s"
        if ep % 4 == 3 or ep == args.epochs - 1:
            prob = np.stack([predict_prob(model, x.transpose(1, 2, 0)) for x in Xva])
            score = f1(prob, Yva, 0.5)
            msg += f" val F1 {score:.3f}"
            if score > best:
                best = score
                torch.save({"state_dict": model.state_dict(), "base": args.base, "threshold": 0.5}, args.out)
        print(msg, flush=True)

    # tune the probability threshold on val for the best checkpoint
    ckpt = torch.load(args.out, weights_only=True)
    model.load_state_dict(ckpt["state_dict"])
    prob = np.stack([predict_prob(model, x.transpose(1, 2, 0)) for x in Xva])
    grid = np.round(np.arange(0.3, 0.71, 0.05), 2)
    t = float(max(grid, key=lambda t: f1(prob, Yva, t)))
    ckpt["threshold"] = t
    torch.save(ckpt, args.out)
    print(f"saved {args.out}: val F1 {f1(prob, Yva, t):.3f} at threshold {t}")


if __name__ == "__main__":
    main()
