"""
canopy_unet.py

Small U-Net for urban tree canopy segmentation from 60 cm RGB imagery, plus the
helpers shared by 09_train_canopy_unet.py and 10_predict_canopy_unet.py.

The model works on ~0.6 m imagery (NAIP-like). Tiles at other resolutions are
resampled to 0.6 m before inference.
"""

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F

MODEL_RES_M = 0.6  # ground resolution the model was trained at, in metres


def _block(cin, cout):
    return nn.Sequential(
        nn.Conv2d(cin, cout, 3, padding=1, bias=False), nn.BatchNorm2d(cout), nn.ReLU(inplace=True),
        nn.Conv2d(cout, cout, 3, padding=1, bias=False), nn.BatchNorm2d(cout), nn.ReLU(inplace=True),
    )


class UNet(nn.Module):
    def __init__(self, base=24, in_ch=3):
        super().__init__()
        ch = [base * 2 ** i for i in range(5)]
        self.enc = nn.ModuleList([_block(in_ch, ch[0])] + [_block(ch[i], ch[i + 1]) for i in range(4)])
        self.up = nn.ModuleList([nn.ConvTranspose2d(ch[i + 1], ch[i], 2, 2) for i in range(4)])
        self.dec = nn.ModuleList([_block(2 * ch[i], ch[i]) for i in range(4)])
        self.out = nn.Conv2d(ch[0], 1, 1)

    def forward(self, x):
        skips = []
        for i, enc in enumerate(self.enc):
            x = enc(x if i == 0 else F.max_pool2d(x, 2))
            skips.append(x)
        x = skips.pop()
        for i in reversed(range(4)):
            x = self.dec[i](torch.cat([self.up[i](x), skips[i]], 1))
        return self.out(x)


def normalize(x):
    """uint8-range float tensor (N,3,H,W) -> per-image standardised input.
    Per-image standardisation keeps the model robust to colour shifts between
    sensors and acquisition years."""
    x = x.float() / 255.0
    mean = x.mean((2, 3), keepdim=True)
    std = x.std((2, 3), keepdim=True) + 1e-3
    return (x - mean) / std


@torch.no_grad()
def predict_prob(model, rgb, tile=256, stride=192, tta=True):
    """Canopy probability for an RGB array (H, W, 3) of any size, by sliding window."""
    model.eval()
    H, W = rgb.shape[:2]
    ph, pw = max(H, tile), max(W, tile)
    img = np.zeros((ph, pw, 3), np.float32)
    img[:H, :W] = rgb
    acc = np.zeros((ph, pw), np.float32)
    cnt = np.zeros((ph, pw), np.float32)
    # weight window centres more than edges, which see less context
    w1 = np.hanning(tile + 2)[1:-1].astype(np.float32)
    win = np.outer(w1, w1) + 1e-3
    ys = list(range(0, ph - tile + 1, stride))
    xs = list(range(0, pw - tile + 1, stride))
    if ys[-1] != ph - tile:
        ys.append(ph - tile)
    if xs[-1] != pw - tile:
        xs.append(pw - tile)
    for y in ys:
        for x in xs:
            patch = torch.from_numpy(img[y:y + tile, x:x + tile]).permute(2, 0, 1)[None]
            ks = range(4) if tta else range(1)
            p = sum(torch.rot90(torch.sigmoid(model(normalize(torch.rot90(patch, k, (2, 3))))), -k, (2, 3)) for k in ks)
            acc[y:y + tile, x:x + tile] += (p / len(ks))[0, 0].numpy() * win
            cnt[y:y + tile, x:x + tile] += win
    return (acc / cnt)[:H, :W]


def load_model(path, device="cpu"):
    ckpt = torch.load(path, map_location=device, weights_only=True)
    model = UNet(base=int(ckpt["base"]))
    model.load_state_dict(ckpt["state_dict"])
    return model.eval(), float(ckpt["threshold"])
