import tensorflow as tf
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import ModelCheckpoint
import glob
import numpy as np
from models import SFANet
from utils.preprocess import *
import argparse
import os
import sys
import h5py as h5

def generator(f, batch_size, num_gpus=1):
    train_images = f['train/images']
    train_confidence = f['train/confidence']
    train_attention = f['train/attention']
    
    inds = np.arange(len(train_images))
    np.random.shuffle(inds)
    idx = 0
    while True:
        batch_inds = inds[idx:idx + batch_size * num_gpus]  # Global batch size
        batch_images = np.stack([train_images[i] for i in batch_inds])
        batch_confidence = np.stack([train_confidence[i] for i in batch_inds])
        batch_attention = np.stack([train_attention[i] for i in batch_inds])
        yield (batch_images, [batch_confidence, batch_attention])
        idx += batch_size * num_gpus
        if idx >= len(inds):
            np.random.shuffle(inds)
            idx = 0

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('data', help='path to training data hdf5 file')
    parser.add_argument('log', help='path to log directory')
    parser.add_argument('--lr', type=float, default=1e-4, help='learning rate')
    parser.add_argument('--epochs', type=int, default=500, help='num epochs')
    parser.add_argument('--batch_size', type=int, default=8, help='batch size per GPU')
    args = parser.parse_args()

    # Configure GPU settings before any TensorFlow operations
    physical_devices = tf.config.list_physical_devices('GPU')
    if physical_devices:
        try:
            for device in physical_devices:
                tf.config.experimental.set_memory_growth(device, True)
            print(f"Set memory growth for {len(physical_devices)} GPUs.")
        except RuntimeError as e:
            print(f"Error setting memory growth: {e}")
    else:
        print("No GPUs detected. Training on CPU.")

    # Detect available GPUs and set up MirroredStrategy
    num_gpus = len(tf.config.list_physical_devices('GPU'))
    if num_gpus == 0:
        print("No GPUs detected. Training on CPU.")
        strategy = tf.distribute.OneDeviceStrategy(device="/cpu:0")
    else:
        print(f"Detected {num_gpus} GPUs. Using MirroredStrategy.")
        strategy = tf.distribute.MirroredStrategy(devices=[f"/gpu:{i}" for i in range(num_gpus)])

    global_batch_size = args.batch_size * num_gpus  # Total batch size across all GPUs

    # Open HDF5 file
    f = h5.File(args.data, 'r')
    bands = f.attrs['bands']
    val_images = f['val/images'][:]
    val_confidence = f['val/confidence'][:]
    val_attention = f['val/attention'][:]
    
    preprocess_fn = eval(f'preprocess_{bands}')

    # Build and compile model within strategy scope
    with strategy.scope():
        model, testing_model = SFANet.build_model(val_images.shape[1:], preprocess_fn=preprocess_fn)
        opt = Adam(args.lr)
        model.compile(optimizer=opt, loss=['mse', 'binary_crossentropy'], loss_weights=[1, 0.1])

    print(model.summary())

    os.makedirs(args.log, exist_ok=True)

    callbacks = []

    weights_path = os.path.join(args.log, 'weights.best.weights.h5')
    callbacks.append(ModelCheckpoint(
        filepath=weights_path,
        monitor='val_loss',
        verbose=True,
        save_best_only=True,
        save_weights_only=True,
    ))
    weights_path = os.path.join(args.log, 'weights.latest.weights.h5')
    callbacks.append(ModelCheckpoint(
        filepath=weights_path,
        monitor='val_loss',
        verbose=True,
        save_best_only=False,
        save_weights_only=True,
    ))
    tensorboard_path = os.path.join(args.log, 'tensorboard')
    os.system("rm -rf " + tensorboard_path)
    callbacks.append(tf.keras.callbacks.TensorBoard(tensorboard_path))

    # Create generator
    gen = generator(f, args.batch_size, num_gpus)
    y_val = [val_confidence, val_attention]

    # Train model
    model.fit(
        gen,
        validation_data=(val_images, y_val),
        batch_size=global_batch_size,  # Use global batch size
        epochs=args.epochs,
        steps_per_epoch=len(f['train/images']) // global_batch_size + 1,
        verbose=True,
        callbacks=callbacks,
        use_multiprocessing=False  # Disable multiprocessing with MirroredStrategy
    )

if __name__ == '__main__':
    main()