import { Component } from '@angular/core';
import { Router } from '@angular/router';

@Component({
  selector: 'app-landing',
  templateUrl: './landing.component.html',
  styleUrls: ['./landing.component.css']
})
export class LandingComponent {
  
  features = [
    {
      icon: '🔍',
      title: 'Advanced Object Detection',
      description: 'Powered by YOLOv8, our AI model can detect Toolbox, Oxygen Tank, and Fire Extinguisher with high accuracy.'
    },
    {
      icon: '📊',
      title: 'Real-time Analytics',
      description: 'Interactive charts and detailed position data provide comprehensive insights into detected objects.'
    },
    {
      icon: '⚡',
      title: 'Fast Processing',
      description: 'Optimized for speed with processing times under 1 second for most images.'
    },
    {
      icon: '📱',
      title: 'Mobile Responsive',
      description: 'Works seamlessly across all devices - desktop, tablet, and mobile phones.'
    },
    {
      icon: '🎯',
      title: 'Precise Positioning',
      description: 'Get exact coordinates, bounding boxes, and size measurements for each detected object.'
    },
    {
      icon: '🛰️',
      title: 'Space Station Ready',
      description: 'Specifically trained on space station environments for optimal performance in orbital conditions.'
    }
  ];

  stats = [
    { number: '99.2%', label: 'Detection Accuracy' },
    { number: '<1s', label: 'Processing Time' },
    { number: '3', label: 'Object Classes' },
    { number: '640px', label: 'Image Resolution' }
  ];

  constructor(private router: Router) {}

  navigateToApp() {
    this.router.navigate(['/detector']);
  }

  scrollToFeatures() {
    document.getElementById('features')?.scrollIntoView({ behavior: 'smooth' });
  }

  scrollToStats() {
    document.getElementById('stats')?.scrollIntoView({ behavior: 'smooth' });
  }
} 