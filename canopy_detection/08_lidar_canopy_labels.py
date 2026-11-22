#!/usr/bin/env python
"""
08_lidar_canopy_labels.py

Make tree canopy masks for GeoTIFF tiles from USGS 3DEP airborne lidar, read
straight from the public Entwine Point Tile (EPT) copies on AWS. The masks are
the training and evaluation labels for the canopy U-Net (09, 10).

A pixel is canopy when, inside that pixel:
  * the tallest non-ground lidar return is >= --min_height metres above ground
    (ground = 3DEP class 2, interpolated to a terrain model), and
  * at least --min_multireturn of the returns more than 2 m up in the
    surrounding 3x3 pixels come from pulses with several returns. Leaves let
    the laser through and give multiple returns; roofs give one.
Large single-return areas over 2.5 m (roofs) are grown by 2 px and removed, so
the multiple returns at building edges are not counted as trees. Specks under
--min_px pixels are dropped.

Find the EPT dataset that covers your city by listing
https://s3-us-west-2.amazonaws.com/usgs-lidar-public/?list-type=2&delimiter=/
(each prefix has an ept.json with its bounds in EPSG:3857).

Example:
    python 08_lidar_canopy_labels.py --tile_dir tiles --out_dir canopy_labels \
        --ept CA_LosAngeles_1_B23
"""

import argparse
import hashlib
import io
import json
import os
import urllib.request
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import laspy
import numpy as np
import rasterio
from rasterio.warp import transform, transform_bounds
from scipy import ndimage as ndi
from scipy.interpolate import griddata

EPT_ROOT = "https://s3-us-west-2.amazonaws.com/usgs-lidar-public/"


class EPT:
    """Minimal reader for an Entwine Point Tile dataset: every point in a bbox."""

    def __init__(self, name, cache_dir):
        self.url = EPT_ROOT + name + "/"
        self.cache = cache_dir
        os.makedirs(cache_dir, exist_ok=True)
        meta = json.loads(self._get(self.url + "ept.json"))
        self.bounds = meta["bounds"]  # cube in EPSG:3857
        self.hier = {}

    def _get(self, url):
        path = os.path.join(self.cache, hashlib.md5(url.encode()).hexdigest())
        if os.path.exists(path):
            return Path(path).read_bytes()
        for attempt in range(4):
            try:
                data = urllib.request.urlopen(url, timeout=120).read()
                break
            except OSError:
                if attempt == 3:
                    raise
        Path(path).write_bytes(data)
        return data

    def _node_bounds(self, key):
        d, x, y, z = map(int, key.split("-"))
        b, n = self.bounds, 2 ** d
        sx, sy = (b[3] - b[0]) / n, (b[4] - b[1]) / n
        return (b[0] + x * sx, b[1] + y * sy, b[0] + (x + 1) * sx, b[1] + (y + 1) * sy)

    def query(self, minx, miny, maxx, maxy):
        """Points in the 3857 bbox as columns x, y, z, class, number_of_returns."""
        self.hier.update(json.loads(self._get(self.url + "ept-hierarchy/0-0-0-0.json")))
        out, stack = [], ["0-0-0-0"]
        while stack:
            key = stack.pop()
            if key not in self.hier:
                continue
            if self.hier[key] == -1:  # subtree stored in its own hierarchy file
                self.hier.update(json.loads(self._get(self.url + f"ept-hierarchy/{key}.json")))
            nb = self._node_bounds(key)
            if nb[2] < minx or nb[0] > maxx or nb[3] < miny or nb[1] > maxy:
                continue
            if self.hier[key] > 0:
                las = laspy.read(io.BytesIO(self._get(self.url + f"ept-data/{key}.laz")))
                x, y = np.asarray(las.x), np.asarray(las.y)
                m = (x >= minx) & (x <= maxx) & (y >= miny) & (y <= maxy)
                if m.any():
                    out.append(np.stack([x[m], y[m], np.asarray(las.z)[m],
                                         np.asarray(las.classification)[m].astype(float),
                                         np.asarray(las.number_of_returns)[m]], 1))
            d, x, y, z = map(int, key.split("-"))
            stack += [f"{d + 1}-{2 * x + i}-{2 * y + j}-{2 * z + k}" for i in (0, 1) for j in (0, 1) for k in (0, 1)]
        return np.concatenate(out) if out else np.zeros((0, 5))


def lidar_rasters(ept, tif):
    """Height above ground (max per pixel) and local multi-return fraction on the tile grid."""
    with rasterio.open(tif) as r:
        H, W, crs, tr, bounds = r.height, r.width, r.crs, r.transform, r.bounds
    b = transform_bounds(crs, "EPSG:3857", *bounds)
    p = ept.query(b[0] - 20, b[1] - 20, b[2] + 20, b[3] + 20)
    p = p[(p[:, 3] == 1) | (p[:, 3] == 2)]  # unclassified + ground; drops noise, water etc.
    if len(p) == 0:
        raise ValueError("no lidar points over this tile")
    xs, ys = transform("EPSG:3857", crs, p[:, 0], p[:, 1])
    rows, cols = rasterio.transform.rowcol(tr, np.asarray(xs), np.asarray(ys))
    rows, cols = np.asarray(rows), np.asarray(cols)
    z, ground = p[:, 2], p[:, 3] == 2

    gi = np.where(ground)[0]
    if len(gi) > 60000:
        gi = gi[np.linspace(0, len(gi) - 1, 60000).astype(int)]
    rr, cc = np.mgrid[0:H, 0:W]
    pts = np.stack([rows[gi], cols[gi]], 1).astype(float)
    dtm = griddata(pts, z[gi], (rr, cc), method="linear")
    dtm = np.where(np.isnan(dtm), griddata(pts, z[gi], (rr, cc), method="nearest"), dtm)

    inb = (rows >= 0) & (rows < H) & (cols >= 0) & (cols < W) & ~ground
    r_, c_ = rows[inb], cols[inb]
    hag = z[inb] - dtm[r_, c_]
    idx = r_ * W + c_
    chm = np.full(H * W, -np.inf)
    np.maximum.at(chm, idx, hag)
    chm = chm.reshape(H, W)
    chm[~np.isfinite(chm)] = 0
    high = hag > 2.0
    multi = p[inb, 4] > 1
    n_high = np.bincount(idx[high], minlength=H * W).reshape(H, W).astype(float)
    n_multi = np.bincount(idx[high & multi], minlength=H * W).reshape(H, W).astype(float)
    k = np.ones((3, 3))
    mr = ndi.convolve(n_multi, k) / np.maximum(ndi.convolve(n_high, k), 1)
    return chm, mr


def _drop_small(mask, min_px):
    lab, n = ndi.label(mask)
    if not n:
        return mask
    sizes = ndi.sum(mask, lab, range(1, n + 1))
    return np.isin(lab, np.where(sizes >= min_px)[0] + 1)


def canopy_mask(chm, mr, min_height=3.0, min_multireturn=0.25, min_px=11):
    roofs = ndi.binary_opening((chm >= 2.5) & (mr < 0.12), iterations=2)
    roofs = ndi.binary_dilation(_drop_small(roofs, 80), iterations=2)
    veg = (chm >= min_height) & (mr >= min_multireturn) & ~roofs
    veg = ndi.binary_closing(ndi.binary_opening(veg, iterations=1), iterations=1)
    return _drop_small(veg, min_px)


def _work(job):
    tif, out, args = job
    try:
        ept = EPT(args.ept, args.cache_dir)
        chm, mr = lidar_rasters(ept, tif)
        mask = canopy_mask(chm, mr, args.min_height, args.min_multireturn, args.min_px)
        with rasterio.open(tif) as r:
            prof = r.profile
        prof.update(count=1, dtype="uint8", nodata=None, compress="deflate")
        with rasterio.open(out, "w", **prof) as dst:
            dst.write(mask.astype(np.uint8), 1)
        return f"{Path(tif).name} canopy {100 * mask.mean():.1f}%"
    except Exception as e:  # keep going over the other tiles
        return f"{Path(tif).name} FAILED {e!r}"


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--tile_dir", required=True, help="folder of georeferenced GeoTIFF tiles")
    ap.add_argument("--out_dir", required=True, help="where to write <tile>.tif canopy masks (1 = canopy)")
    ap.add_argument("--ept", default="CA_LosAngeles_1_B23", help="USGS 3DEP EPT dataset name")
    ap.add_argument("--cache_dir", default="ept_cache", help="local cache for downloaded lidar")
    ap.add_argument("--min_height", type=float, default=3.0, help="canopy height cut-off in metres")
    ap.add_argument("--min_multireturn", type=float, default=0.25)
    ap.add_argument("--min_px", type=int, default=11, help="smallest canopy patch kept, in pixels")
    ap.add_argument("--workers", type=int, default=8, help="parallel tiles (download-bound)")
    args = ap.parse_args()

    os.makedirs(args.out_dir, exist_ok=True)
    jobs = [(str(t), os.path.join(args.out_dir, t.name), args)
            for t in sorted(Path(args.tile_dir).glob("*.tif"))
            if not os.path.exists(os.path.join(args.out_dir, t.name))]
    with ProcessPoolExecutor(args.workers) as ex:
        for line in ex.map(_work, jobs):
            print(line, flush=True)


if __name__ == "__main__":
    main()
