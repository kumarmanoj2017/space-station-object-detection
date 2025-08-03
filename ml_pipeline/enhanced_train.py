import os
import yaml
from ultralytics import YOLO
from pathlib import Path
import torch

def train_space_station_model():
    """Train YOLOv8 model on space station dataset"""
    
    # Dataset path
    dataset_path = Path("C:/Users/ManojKumar/Downloads/Hackathon_Dataset/HackByte_Dataset")
    data_yaml = dataset_path / "data.yaml"
    
    # Check if dataset exists
    if not data_yaml.exists():
        print(f"❌ Error: data.yaml not found at {data_yaml}")
        return
    
    print(f"✅ Found dataset at: {dataset_path}")
    
    # Load and check data configuration
    with open(data_yaml, 'r') as f:
        data_config = yaml.safe_load(f)
    
    print(f"📊 Dataset configuration:")
    print(f"  - Classes: {data_config.get('names', [])}")
    print(f"  - Train: {data_config.get('train', '')}")
    print(f"  - Val: {data_config.get('val', '')}")
    print(f"  - Test: {data_config.get('test', '')}")
    
    # Initialize model
    model = YOLO('yolov8n.pt')  # Start with YOLOv8n for faster training
    
    # Training parameters
    training_args = {
        'data': str(data_yaml),
        'epochs': 100,
        'batch': 16,
        'imgsz': 640,
        'patience': 20,
        'save': True,
        'save_period': 10,
        'cache': True,
        'device': 'auto',
        'workers': 8,
        'project': 'runs/train',
        'name': 'space_station_model',
        'exist_ok': True,
        'pretrained': True,
        'optimizer': 'AdamW',
        'lr0': 0.001,
        'lrf': 0.01,
        'momentum': 0.937,
        'weight_decay': 0.0005,
        'warmup_epochs': 3,
        'warmup_momentum': 0.8,
        'warmup_bias_lr': 0.1,
        'box': 7.5,
        'cls': 0.5,
        'dfl': 1.5,
        'pose': 12.0,
        'kobj': 1.0,
        'label_smoothing': 0.0,
        'nbs': 64,
        'overlap_mask': True,
        'mask_ratio': 4,
        'dropout': 0.0,
        'val': True,
        'plots': True
    }
    
    print("🚀 Starting Space Station Model Training...")
    print("📋 Training Parameters:")
    for key, value in training_args.items():
        print(f"  - {key}: {value}")
    
    # Start training
    try:
        results = model.train(**training_args)
        print("✅ Training completed successfully!")
        
        # Save model path for backend
        model_path = results.save_dir / "weights" / "best.pt"
        print(f"📁 Best model saved at: {model_path}")
        
        # Update backend configuration
        update_backend_model_path(str(model_path))
        
        return str(model_path)
        
    except Exception as e:
        print(f"❌ Training failed: {e}")
        return None

def update_backend_model_path(model_path: str):
    """Update backend to use the trained model"""
    backend_app_path = Path("../backend/app.py")
    
    if backend_app_path.exists():
        with open(backend_app_path, 'r') as f:
            content = f.read()
        
        # Update the model path in the backend
        updated_content = content.replace(
            'model_path="runs/train/space_station_latest/weights/best.pt"',
            f'model_path="{model_path}"'
        )
        
        with open(backend_app_path, 'w') as f:
            f.write(updated_content)
        
        print(f"✅ Backend updated to use trained model: {model_path}")

if __name__ == "__main__":
    print("🎯 Space Station Object Detection Model Training")
    print("=" * 50)
    
    # Check CUDA availability
    if torch.cuda.is_available():
        print(f"✅ CUDA available: {torch.cuda.get_device_name()}")
    else:
        print("⚠️  CUDA not available, using CPU (training will be slower)")
    
    # Train the model
    model_path = train_space_station_model()
    
    if model_path:
        print("\n Training completed!")
        print(f"📁 Model saved at: {model_path}")
        print("🔄 Restart your backend to use the trained model")
    else:
        print("\n❌ Training failed. Check your dataset and try again.")