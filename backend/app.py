from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import cv2
import numpy as np
import sqlite3
import json
from datetime import datetime
import os
from pathlib import Path
from ultralytics import YOLO
import base64
from PIL import Image
import io

app = Flask(__name__)
CORS(app)

class SpaceStationDetector:
    def __init__(self, model_path="C:/Users/ManojKumar/Downloads/Hackathon_Dataset/HackByte_Dataset/runs/detect/train2/weights/best.pt"):
        self.model_path = model_path
        self.model = None
        self.load_model()
        self.setup_database()
    
    def load_model(self):
        """Load the trained YOLOv8 model"""
        try:
            print(f"   Attempting to load model from: {self.model_path}")
            print(f"📁 File exists: {os.path.exists(self.model_path)}")
            
            self.model = YOLO(self.model_path)
            print(f"✅ Model loaded successfully from {self.model_path}")
            
            # Add debug info
            print(f"📊 Model classes: {self.model.names}")
            print(f"   Number of classes: {len(self.model.names)}")
            
        except Exception as e:
            print(f"❌ Error loading model: {e}")
            print(" Using fallback YOLOv8n model for testing...")
            self.model = YOLO('yolov8n.pt')
    
    def setup_database(self):
        """Setup SQLite database for detection history"""
        os.makedirs('database', exist_ok=True)
        
        conn = sqlite3.connect('database/space_station.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS detections (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                image_path TEXT,
                toolbox_count INTEGER DEFAULT 0,
                oxygen_tank_count INTEGER DEFAULT 0,
                fire_extinguisher_count INTEGER DEFAULT 0,
                confidence_scores TEXT,
                processing_time REAL,
                image_data BLOB
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_settings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                confidence_threshold REAL DEFAULT 0.5,
                detection_mode TEXT DEFAULT 'all',
                ui_preferences TEXT DEFAULT '{}'
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS training_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                model_path TEXT,
                epochs INTEGER,
                mAP_50 REAL,
                mAP_50_95 REAL,
                precision REAL,
                recall REAL,
                training_time REAL,
                config TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
        print("✅ Database setup completed")
    
    def preprocess_image(self, image_data):
        """Preprocess image for detection"""
        try:
            if isinstance(image_data, str):
                if image_data.startswith('data:image'):
                    image_data = image_data.split(',')[1]
                image_bytes = base64.b64decode(image_data)
            else:
                image_bytes = image_data
            
            try:
                image = Image.open(io.BytesIO(image_bytes))
            except Exception as pil_error:
                print(f"PIL failed to open image: {pil_error}")
                nparr = np.frombuffer(image_bytes, np.uint8)
                image_array = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                if image_array is None:
                    raise Exception("Failed to decode image with both PIL and OpenCV")
                image_array = cv2.cvtColor(image_array, cv2.COLOR_BGR2RGB)
                return image_array
            
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            image_array = np.array(image)
            return image_array
            
        except Exception as e:
            print(f"Error preprocessing image: {e}")
            raise Exception(f"Failed to process image: {str(e)}")
    
    def detect_objects(self, image_data, confidence_threshold=0.5):
        """Perform object detection on image"""
        start_time = datetime.now()
        
        print(f"   Starting detection with confidence threshold: {confidence_threshold}")
        
        # Preprocess image
        image = self.preprocess_image(image_data)
        print(f"🖼️ Image preprocessed, shape: {image.shape}")
        
        # Run detection with confidence threshold
        results = self.model(image, conf=confidence_threshold)
        print(f"🔍 Detection completed, results: {len(results)}")
        
        # Process results
        detections = []
        class_counts = {'FireExtinguisher': 0, 'ToolBox': 0, 'OxygenTank': 0}
        
        for i, result in enumerate(results):
            print(f"📊 Processing result {i+1}")
            boxes = result.boxes
            if boxes is not None:
                print(f"   Found {len(boxes)} boxes")
                for j, box in enumerate(boxes):
                    # Get coordinates
                    x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                    
                    # Get confidence and class
                    confidence = float(box.conf[0])
                    class_id = int(box.cls[0])
                    
                    print(f"  Box {j+1}: class_id={class_id}, confidence={confidence:.3f}")
                    
                    # Only include detections above threshold
                    if confidence >= confidence_threshold:
                        # Map class ID to name
                        class_names = ['FireExtinguisher', 'ToolBox', 'OxygenTank']
                        class_name = class_names[class_id] if class_id < len(class_names) else f'object_{class_id}'
                        
                        print(f"  ✅ Detection: {class_name} (confidence: {confidence:.3f})")
                        
                        # Count objects
                        if class_name not in class_counts:
                            class_counts[class_name] = 0
                        class_counts[class_name] += 1
                        
                        detections.append({
                            'bbox': [float(x1), float(y1), float(x2), float(y2)],
                            'confidence': confidence,
                            'class': class_name,
                            'class_id': class_id
                        })
                    else:
                        print(f"  ❌ Below threshold: {confidence:.3f} < {confidence_threshold}")
            else:
                print("📦 No boxes found in result")
        
        processing_time = (datetime.now() - start_time).total_seconds()
        print(f"⏱️ Processing time: {processing_time:.3f}s")
        print(f"   Final class counts: {class_counts}")
        
        return {
            'detections': detections,
            'class_counts': class_counts,
            'processing_time': processing_time,
            'total_objects': sum(class_counts.values())
        }
    
    def save_detection(self, image_data, detection_results):
        """Save detection results to database"""
        conn = sqlite3.connect('database/space_station.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO detections 
            (image_path, toolbox_count, oxygen_tank_count, fire_extinguisher_count, 
             confidence_scores, processing_time, image_data)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            f"detection_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg",
            detection_results['class_counts'].get('ToolBox', 0),
            detection_results['class_counts'].get('OxygenTank', 0),
            detection_results['class_counts'].get('FireExtinguisher', 0),
            json.dumps([d['confidence'] for d in detection_results['detections']]),
            detection_results['processing_time'],
            image_data if isinstance(image_data, bytes) else base64.b64decode(image_data.split(',')[1])
        ))
        
        conn.commit()
        conn.close()

# Initialize detector
detector = SpaceStationDetector()

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'model_loaded': detector.model is not None,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/detect', methods=['POST'])
def detect_objects():
    """Main detection endpoint"""
    try:
        data = request.get_json()
        image_data = data.get('image')
        confidence_threshold = data.get('confidence_threshold', 0.5)
        
        if not image_data:
            return jsonify({'error': 'No image data provided'}), 400
        
        print(f"   Received detection request with confidence threshold: {confidence_threshold}")
        
        # Perform detection
        results = detector.detect_objects(image_data, confidence_threshold)
        
        # Save detection
        detector.save_detection(image_data, results)
        
        return jsonify({
            'success': True,
            'results': results,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        print(f"❌ Error in detection endpoint: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/history', methods=['GET'])
def get_detection_history():
    """Get detection history"""
    try:
        conn = sqlite3.connect('database/space_station.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, timestamp, toolbox_count, oxygen_tank_count, fire_extinguisher_count,
                   confidence_scores, processing_time
            FROM detections
            ORDER BY timestamp DESC
            LIMIT 50
        ''')
        
        rows = cursor.fetchall()
        history = []
        
        for row in rows:
            history.append({
                'id': row[0],
                'timestamp': row[1],
                'toolbox_count': row[2],
                'oxygen_tank_count': row[3],
                'fire_extinguisher_count': row[4],
                'confidence_scores': json.loads(row[5]) if row[5] else [],
                'processing_time': row[6]
            })
        
        conn.close()
        
        return jsonify({
            'success': True,
            'history': history
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/settings', methods=['GET', 'POST'])
def manage_settings():
    """Manage user settings"""
    conn = sqlite3.connect('database/space_station.db')
    cursor = conn.cursor()
    
    if request.method == 'GET':
        cursor.execute('SELECT confidence_threshold, detection_mode, ui_preferences FROM user_settings ORDER BY id DESC LIMIT 1')
        row = cursor.fetchone()
        
        if row:
            settings = {
                'confidence_threshold': row[0],
                'detection_mode': row[1],
                'ui_preferences': json.loads(row[2]) if row[2] else {}
            }
        else:
            settings = {
                'confidence_threshold': 0.5,
                'detection_mode': 'all',
                'ui_preferences': {}
            }
        
        conn.close()
        return jsonify({'success': True, 'settings': settings})
    
    elif request.method == 'POST':
        data = request.get_json()
        
        cursor.execute('''
            INSERT INTO user_settings (confidence_threshold, detection_mode, ui_preferences)
            VALUES (?, ?, ?)
        ''', (
            data.get('confidence_threshold', 0.5),
            data.get('detection_mode', 'all'),
            json.dumps(data.get('ui_preferences', {}))
        ))
        
        conn.commit()
        conn.close()
        
        return jsonify({'success': True, 'message': 'Settings updated'})

@app.route('/api/metrics', methods=['GET'])
def get_model_metrics():
    """Get model performance metrics"""
    try:
        conn = sqlite3.connect('database/space_station.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT mAP_50, mAP_50_95, precision, recall, timestamp
            FROM training_results
            ORDER BY timestamp DESC
            LIMIT 1
        ''')
        
        training_row = cursor.fetchone()
        
        cursor.execute('''
            SELECT 
                COUNT(*) as total_detections,
                AVG(processing_time) as avg_processing_time,
                SUM(toolbox_count + oxygen_tank_count + fire_extinguisher_count) as total_objects
            FROM detections
        ''')
        
        detection_row = cursor.fetchone()
        
        conn.close()
        
        metrics = {
            'model_performance': {
                'mAP_50': training_row[0] if training_row else 0,
                'mAP_50_95': training_row[1] if training_row else 0,
                'precision': training_row[2] if training_row else 0,
                'recall': training_row[3] if training_row else 0,
                'last_training': training_row[4] if training_row else None
            },
            'detection_stats': {
                'total_detections': detection_row[0] if detection_row else 0,
                'avg_processing_time': detection_row[1] if detection_row else 0,
                'total_objects_detected': detection_row[2] if detection_row else 0
            }
        }
        
        return jsonify({'success': True, 'metrics': metrics})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("🚀 Starting Space Station Detection API...")
    print("📊 API Endpoints:")
    print("  - GET  /api/health - Health check")
    print("  - POST /api/detect - Object detection")
    print("  - GET  /api/history - Detection history")
    print("  - GET/POST /api/settings - User settings")
    print("  - GET  /api/metrics - Model metrics")
    
    app.run(debug=True, host='0.0.0.0', port=5000)