import { Component, OnInit } from '@angular/core';
import { HttpClient } from '@angular/common/http';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css']
})
export class AppComponent implements OnInit {
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

    this.detailedDetections = results.detections.map((detection: any) => ({
      class: detection.class,
      bbox: detection.bbox,
      confidence: detection.confidence
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