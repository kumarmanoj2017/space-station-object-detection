import { Component, OnInit } from '@angular/core';
import { HttpClient } from '@angular/common/http';

@Component({
  selector: 'app-detector',
  templateUrl: './detector.component.html',
  styleUrls: ['./detector.component.css']
})
export class DetectorComponent implements OnInit {
  title = 'Space Station Object Detector';
  
  selectedFile: File | null = null;
  imagePreview: string | null = null;
  detectionResults = {
    toolbox: 0,
    oxygenTank: 0,
    fireExtinguisher: 0,
    processingTime: '0s'
  };
  detailedDetections: any[] = [];
  hasDetected = false;
  confidenceThreshold = 0.5;
  showHistory = false;
  showMetrics = false;
  detectionHistory: any[] = [];
  modelMetrics: any = {};

  // Chart configurations
  public barChartOptions = {
    responsive: true,
    scales: {
      y: {
        beginAtZero: true,
        max: 10
      }
    }
  };
  public barChartLabels = ['Toolbox', 'Oxygen Tank', 'Fire Extinguisher'];
  public barChartLegend = true;
  public barChartData = [
    { 
      data: [0, 0, 0], 
      label: 'Detections',
      backgroundColor: [
        'rgba(255, 99, 132, 0.8)',
        'rgba(54, 162, 235, 0.8)',
        'rgba(255, 206, 86, 0.8)'
      ],
      borderColor: [
        'rgba(255, 99, 132, 1)',
        'rgba(54, 162, 235, 1)',
        'rgba(255, 206, 86, 1)'
      ],
      borderWidth: 1
    }
  ];

  public pieChartOptions = {
    responsive: true
  };
  public pieChartLabels = ['Toolbox', 'Oxygen Tank', 'Fire Extinguisher'];
  public pieChartLegend = true;
  public pieChartData = [
    { 
      data: [0, 0, 0],
      backgroundColor: [
        'rgba(255, 99, 132, 0.8)',
        'rgba(54, 162, 235, 0.8)',
        'rgba(255, 206, 86, 0.8)'
      ],
      borderColor: [
        'rgba(255, 99, 132, 1)',
        'rgba(54, 162, 235, 1)',
        'rgba(255, 206, 86, 1)'
      ],
      borderWidth: 1
    }
  ];

  constructor(private http: HttpClient) {}

  ngOnInit() {
    this.loadSettings();
    this.loadHistory();
    this.loadMetrics();
  }

  onFileSelected(event: any) {
    const file = event.target.files[0];
    if (file) {
      this.selectedFile = file;
      const reader = new FileReader();
      reader.onload = (e: any) => {
        this.imagePreview = e.target.result;
      };
      reader.readAsDataURL(file);
    }
  }

  onImageLoad() {
    // Scale bounding boxes when image loads
    if (this.detailedDetections.length > 0) {
      this.scaleBoundingBoxes();
    }
  }

  clearImage() {
    this.selectedFile = null;
    this.imagePreview = null;
    this.detectionResults = {
      toolbox: 0,
      oxygenTank: 0,
      fireExtinguisher: 0,
      processingTime: '0s'
    };
    this.detailedDetections = [];
    this.updateCharts();
  }

  async detectObjects() {
    if (!this.selectedFile) return;

    try {
      const base64Image = await this.fileToBase64(this.selectedFile);
      
      const response: any = await this.http.post('http://127.0.0.1:5000/api/detect', {
        image: base64Image,
        confidence_threshold: 0.05 // Always use 5% threshold
      }).toPromise();

      if (response.success) {
        console.log('Detection response:', response.results);
        this.updateDetectionResults(response.results);
        this.updateCharts();
        this.loadHistory();
        this.loadMetrics();
      }
    } catch (error) {
      console.error('Detection failed:', error);
    }
  }

  updateDetectionResults(results: any) {
    this.detectionResults = {
      toolbox: results.class_counts.ToolBox || 0,
      oxygenTank: results.class_counts.OxygenTank || 0,
      fireExtinguisher: results.class_counts.FireExtinguisher || 0,
      processingTime: results.processing_time.toFixed(3) + 's'
    };

    console.log('Updated detection results:', this.detectionResults);

    // Update detailed detections with position information
    this.detailedDetections = (results.detections || []).map((detection: any) => ({
      class: detection.class,
      bbox: detection.bbox,
      confidence: detection.confidence,
      position: {
        x1: Math.round(detection.bbox[0]),
        y1: Math.round(detection.bbox[1]),
        x2: Math.round(detection.bbox[2]),
        y2: Math.round(detection.bbox[3]),
        width: Math.round(detection.bbox[2] - detection.bbox[0]),
        height: Math.round(detection.bbox[3] - detection.bbox[1]),
        centerX: Math.round((detection.bbox[0] + detection.bbox[2]) / 2),
        centerY: Math.round((detection.bbox[1] + detection.bbox[3]) / 2)
      },
      confidencePercent: Math.round(detection.confidence * 100)
    }));
    
    this.hasDetected = this.detailedDetections.length > 0;
    
    // Scale bounding boxes to fit the displayed image
    setTimeout(() => {
      this.scaleBoundingBoxes();
    }, 100);
  }

  scaleBoundingBoxes() {
    const imageElement = document.querySelector('.image-container img') as HTMLImageElement;
    if (!imageElement || this.detailedDetections.length === 0) return;

    const originalWidth = 640; // YOLO model input size
    const originalHeight = 640;
    const displayWidth = imageElement.offsetWidth;
    const displayHeight = imageElement.offsetHeight;

    const scaleX = displayWidth / originalWidth;
    const scaleY = displayHeight / originalHeight;

    this.detailedDetections = this.detailedDetections.map(detection => ({
      ...detection,
      scaledPosition: {
        x1: Math.round(detection.position.x1 * scaleX),
        y1: Math.round(detection.position.y1 * scaleY),
        x2: Math.round(detection.position.x2 * scaleX),
        y2: Math.round(detection.position.y2 * scaleY),
        width: Math.round(detection.position.width * scaleX),
        height: Math.round(detection.position.height * scaleY),
        centerX: Math.round(detection.position.centerX * scaleX),
        centerY: Math.round(detection.position.centerY * scaleY)
      }
    }));
  }

  updateCharts() {
    console.log('Updating charts with data:', [
      this.detectionResults.toolbox,
      this.detectionResults.oxygenTank,
      this.detectionResults.fireExtinguisher
    ]);

    // Create new chart data objects to trigger change detection
    this.barChartData = [
      { 
        data: [
          this.detectionResults.toolbox,
          this.detectionResults.oxygenTank,
          this.detectionResults.fireExtinguisher
        ], 
        label: 'Detections',
        backgroundColor: [
          'rgba(255, 99, 132, 0.8)',
          'rgba(54, 162, 235, 0.8)',
          'rgba(255, 206, 86, 0.8)'
        ],
        borderColor: [
          'rgba(255, 99, 132, 1)',
          'rgba(54, 162, 235, 1)',
          'rgba(255, 206, 86, 1)'
        ],
        borderWidth: 1
      }
    ];

    this.pieChartData = [
      { 
        data: [
          this.detectionResults.toolbox,
          this.detectionResults.oxygenTank,
          this.detectionResults.fireExtinguisher
        ],
        backgroundColor: [
          'rgba(255, 99, 132, 0.8)',
          'rgba(54, 162, 235, 0.8)',
          'rgba(255, 206, 86, 0.8)'
        ],
        borderColor: [
          'rgba(255, 99, 132, 1)',
          'rgba(54, 162, 235, 1)',
          'rgba(255, 206, 86, 1)'
        ],
        borderWidth: 1
      }
    ];

    console.log('Charts updated:', {
      barChartData: this.barChartData,
      pieChartData: this.pieChartData
    });
  }

  testCharts() {
    console.log('Testing charts with sample data...');
    
    // Set sample detection results
    this.detectionResults = {
      toolbox: 3,
      oxygenTank: 2,
      fireExtinguisher: 1,
      processingTime: '0.5s'
    };
    
    this.updateCharts();
  }

  getBoundingBoxColor(className: string): string {
    switch (className) {
      case 'ToolBox':
        return '#ff6b6b'; // Red
      case 'OxygenTank':
        return '#4ecdc4'; // Teal
      case 'FireExtinguisher':
        return '#45b7d1'; // Blue
      default:
        return '#95a5a6'; // Gray
    }
  }

  fileToBase64(file: File): Promise<string> {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.readAsDataURL(file);
      reader.onload = () => resolve(reader.result as string);
      reader.onerror = error => reject(error);
    });
  }

  loadSettings() {
    this.http.get('http://127.0.0.1:5000/api/settings').subscribe((response: any) => {
      if (response.success) {
        // Keep UI slider value but don't use it for API calls
      }
    });
  }

  loadHistory() {
    this.http.get('http://127.0.0.1:5000/api/history').subscribe((response: any) => {
      if (response.success) {
        this.detectionHistory = response.history;
      }
    });
  }

  loadMetrics() {
    this.http.get('http://127.0.0.1:5000/api/metrics').subscribe((response: any) => {
      if (response.success) {
        this.modelMetrics = response.metrics;
      }
    });
  }
} 