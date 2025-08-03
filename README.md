# 🚀 Space Station Object Detection - Duality AI Hackathon

## Project Overview

This project implements a real-time space station object detection system using YOLOv8, trained on synthetic data from Duality AI's Falcon platform. The system can detect three critical space station objects: **FireExtinguisher**, **ToolBox**, and **OxygenTank**.

## 🎯 Key Features

- **Real-time Object Detection**: YOLOv8 model with 89.3% mAP50 accuracy
- **Mobile-Responsive Web Interface**: Angular frontend with modern UI
- **RESTful API**: Flask backend for model serving
- **Analytics Dashboard**: Charts and visualizations for detection trends
- **Detection History**: SQLite database for storing detection results
- **Configurable Confidence Thresholds**: User-adjustable detection sensitivity

## 📊 Performance Metrics

- **Overall mAP50**: 89.3%
- **FireExtinguisher**: 93.7% mAP50
- **ToolBox**: 91.3% mAP50  
- **OxygenTank**: 82.8% mAP50
- **Training Time**: ~7.8 hours (10 epochs)
- **Inference Speed**: ~588ms per image

## 🏗️ Architecture

```
Space Station Object Detector/
├── backend/                 # Flask API server
│   ├── app.py              # Main API application
│   ├── requirements.txt    # Python dependencies
│   └── database/           # SQLite database
├── frontend/               # Angular web application
│   ├── src/
│   │   ├── app/
│   │   │   ├── app.component.ts
│   │   │   ├── app.component.html
│   │   │   └── app.component.css
│   │   └── main.ts
│   └── package.json
├── ml_pipeline/            # Machine learning scripts
│   ├── enhanced_train.py   # Enhanced training script
│   └── train_fixed.py      # CPU-optimized training
├── runs/                   # Training outputs (generated)
│   └── detect/train2/weights/best.pt
└── README.md
```

## 🚀 Quick Start

### Prerequisites

- **Python 3.8+** with Anaconda
- **Node.js 16+** and npm
- **Angular CLI** (for frontend development)

### 1. Environment Setup

```bash
# Clone the repository
git clone <your-repo-url>
cd space-station-object-detector

# Create and activate Anaconda environment
conda create -n space_station python=3.10
conda activate space_station

# Install Python dependencies
pip install -r backend/requirements.txt
```

### 2. Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create database directory
mkdir database

# Start the Flask server
python app.py
```

The API will be available at `http://127.0.0.1:5000`

### 3. Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Install chart dependencies
npm install chart.js@^3.9.1 ng2-charts@4.0.1

# Start the Angular development server
ng serve
```

The application will be available at `http://localhost:4200`

## 📁 Project Structure

### Backend (`backend/`)

- **`app.py`**: Main Flask application with API endpoints
- **`requirements.txt`**: Python dependencies
- **`database/`**: SQLite database for storing detection history

**API Endpoints:**
- `GET /api/health` - Health check
- `POST /api/detect` - Object detection
- `GET /api/history` - Detection history
- `GET /api/settings` - User settings
- `GET /api/metrics` - Model metrics

### Frontend (`frontend/`)

- **Angular 15** application with modern UI
- **Chart.js integration** for analytics
- **Mobile-responsive design**
- **Real-time detection updates**

### ML Pipeline (`ml_pipeline/`)

- **`enhanced_train.py`**: Advanced training with data augmentation
- **`train_fixed.py`**: CPU-optimized training script

## 🎯 Model Training

### Training Configuration

```python
# Key training parameters
epochs = 10
batch_size = 8
device = 'cpu'  # Optimized for CPU training
confidence_threshold = 0.01 to 1

# Data augmentation
mosaic = 0.5
mixup = 0.1
copy_paste = 0.1
hsv_h = 0.015
hsv_s = 0.7
hsv_v = 0.4
degrees = 10.0
translate = 0.1
scale = 0.5
```

### Training Process

1. **Data Preparation**: Synthetic data from Duality AI Falcon platform
2. **Model Selection**: YOLOv8s pre-trained on COCO dataset
3. **Fine-tuning**: 10 epochs with custom space station classes
4. **Validation**: 154 validation images
5. **Optimization**: Data augmentation and hyperparameter tuning

## 📊 Performance Analysis

### Training Results

```
Epoch GPU_mem box_loss cls_loss dfl_loss Instances Size
10 epochs completed in 7.798 hours

Validation Results:
Class Images Instances Box(P R mAP50 mAP50-95):
all 154 206 0.92 0.836 0.893 0.624
FireExtinguisher 154 67 0.913 0.91 0.937 0.678
ToolBox 154 60 0.981 0.854 0.913 0.686
OxygenTank 154 79 0.867 0.744 0.828 0.507
```

### Model Performance

- **Precision**: 92% overall
- **Recall**: 83.6% overall
- **mAP50**: 89.3% overall
- **mAP50-95**: 62.4% overall

## 🔧 Usage Instructions

### 1. Upload Image
- Click "Choose File" in the Input Image section
- Supported formats: JPG, PNG, AVIF, etc.

### 2. Configure Settings
- Adjust confidence threshold
- Click "Detect Objects" to run inference

### 3. View Results
- Detection counts displayed in result cards
- Detailed object information shown below
- Analytics charts update automatically

### 4. Interpret Charts
- **Bar Chart**: Shows detection counts for each class
- **Pie Chart**: Shows distribution of detected objects

## 🛠️ Troubleshooting

### Common Issues

1. **Model not loading**: Ensure `runs/detect/train2/weights/best.pt` exists
2. **Database errors**: Create `backend/database/` directory
3. **Chart not displaying**: Install chart dependencies with correct versions
4. **CUDA errors**: Use CPU training (already configured)

### Debug Commands

```bash
# Check model file
ls -la runs/detect/train2/weights/

# Test API health
curl http://127.0.0.1:5000/api/health

# Check Angular dependencies
npm list chart.js ng2-charts
```

## 📈 Future Improvements

1. **Model Optimization**: Implement model quantization for faster inference
2. **Data Augmentation**: Add more synthetic data variations
3. **Real-time Video**: Extend to video stream processing
4. **Edge Deployment**: Optimize for edge devices
5. **Multi-class Expansion**: Add more space station objects

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📄 License

This project is developed for the Duality AI Space Station Hackathon.

## 👥 Team

- **Model Development**: YOLOv8 training and optimization
- **Backend Development**: Flask API and database design
- **Frontend Development**: Angular UI and user experience
- **Integration**: Full-stack application deployment

---

**For hackathon submission, see `HACKATHON_REPORT.md` for detailed methodology and analysis.** 
