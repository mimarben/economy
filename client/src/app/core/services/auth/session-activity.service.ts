import { DestroyRef, Injectable, NgZone, inject } from '@angular/core';
import { fromEvent, merge, Subscription } from 'rxjs';
import { throttleTime } from 'rxjs/operators';
import { AuthService } from './auth.service';

@Injectable({
  providedIn: 'root'
})
export class SessionActivityService {
  private readonly authService = inject(AuthService);
  private readonly ngZone = inject(NgZone);
  private readonly destroyRef = inject(DestroyRef);
  private activitySubscription?: Subscription;

  startTracking(): void {
    if (this.activitySubscription) {
      return;
    }

    this.ngZone.runOutsideAngular(() => {
      this.activitySubscription = merge(
        fromEvent(document, 'click'),
        fromEvent(document, 'keydown'),
        fromEvent(document, 'touchstart'),
        fromEvent(document, 'pointerdown'),
        fromEvent(window, 'scroll'),
        fromEvent(window, 'wheel'),
        fromEvent(document, 'visibilitychange')
      )
        .pipe(throttleTime(1000, undefined, { leading: true, trailing: true }))
        .subscribe(() => {
          if (document.visibilityState === 'hidden') {
            return;
          }

          this.authService.registerUserActivity();
        });
    });

    this.destroyRef.onDestroy(() => {
      this.activitySubscription?.unsubscribe();
      this.activitySubscription = undefined;
    });
  }
}
