import { ComponentFixture, TestBed } from '@angular/core/testing';

import { SavingsLogComponent } from './savings-log.component';

describe('SavingsLogComponent', () => {
  let component: SavingsLogComponent;
  let fixture: ComponentFixture<SavingsLogComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [SavingsLogComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(SavingsLogComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
