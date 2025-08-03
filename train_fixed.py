EPOCHS = 10
MOSAIC = 0.5  # Increased for better augmentation
OPTIMIZER = 'AdamW'
MOMENTUM = 0.2
LR0 = 0.001
LRF = 0.0001
SINGLE_CLS = False

import argparse
from ultralytics import YOLO
import os
import sys

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    # epochs
    parser.add_argument('--epochs', type=int, default=EPOCHS, help='Number of epochs')
    # mosaic
    parser.add_argument('--mosaic', type=float, default=MOSAIC, help='Mosaic augmentation')
    # optimizer
    parser.add_argument('--optimizer', type=str, default=OPTIMIZER, help='Optimizer')
    # momentum
    parser.add_argument('--momentum', type=float, default=MOMENTUM, help='Momentum')
    # lr0
    parser.add_argument('--lr0', type=float, default=LR0, help='Initial learning rate')
    # lrf
    parser.add_argument('--lrf', type=float, default=LRF, help='Final learning rate')
    # single_cls
    parser.add_argument('--single_cls', type=bool, default=SINGLE_CLS, help='Single class training')
    args = parser.parse_args()
    
    this_dir = os.path.dirname(__file__)
    os.chdir(this_dir)
    
    model = YOLO(os.path.join(this_dir, "yolov8s.pt"))
    
    results = model.train(
        data=os.path.join(this_dir, "yolo_params.yaml"),
        epochs=args.epochs,
        device='cpu',  # Changed from device=0 to device='cpu'
        single_cls=args.single_cls,
        mosaic=args.mosaic,
        optimizer=args.optimizer,
        lr0=args.lr0,
        lrf=args.lrf,
        momentum=args.momentum,
        batch=8,  # Reduced batch size for CPU
        workers=2,  # Reduced workers for CPU
        patience=3,  # Stop early if no improvement for 3 epochs
        save_period=2,  # Save every 2 epochs
        augment=True,  # Enable data augmentation
        mixup=0.1,  # Add mixup augmentation
        copy_paste=0.1,  # Add copy-paste augmentation
        hsv_h=0.015,  # HSV hue augmentation
        hsv_s=0.7,  # HSV saturation augmentation
        hsv_v=0.4,  # HSV value augmentation
        degrees=10.0,  # Rotation augmentation
        translate=0.1,  # Translation augmentation
        scale=0.5,  # Scale augmentation
        fliplr=0.5,  # Horizontal flip probability
        flipud=0.0,  # Vertical flip probability
        perspective=0.0,  # Perspective transformation
        shear=0.0,  # Shear transformation
        close_mosaic=10  # Close mosaic in last 10 epochs
    )