import { Component, OnInit } from '@angular/core';
import { RouterModule } from '@angular/router';
import { CommonModule } from '@angular/common';
import { MaterialModule } from '@utils/material.module';
@Component({
  selector: 'app-not-found',
  imports: [
    MaterialModule,
    CommonModule,
    RouterModule
  ],
  templateUrl: './not-found.component.html',
  styleUrl: './not-found.component.css'
})
export class NotFoundComponent implements OnInit {
  constructor() { }

  ngOnInit(): void {
    this.createStars();
  }

  /**
   * Dynamically creates star elements in the background
   */
  private createStars(): void {
    setTimeout(() => {
      const starsContainer = document.querySelector('.stars-background');
      if (starsContainer) {
        const numberOfStars = 30;

        for (let i = 0; i < numberOfStars; i++) {
          const star = document.createElement('div');
          star.className = 'star';
          star.style.top = `${Math.random() * 100}%`;
          star.style.left = `${Math.random() * 100}%`;
          star.style.animationDelay = `${Math.random() * 2}s`;
          starsContainer.appendChild(star);
        }
      }
    }, 0);
  }
}
