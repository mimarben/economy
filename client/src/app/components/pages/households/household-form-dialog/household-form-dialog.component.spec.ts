import { ComponentFixture, TestBed } from '@angular/core/testing';

import { HouseholdFormDialogComponent } from './household-form-dialog.component';

describe('HouseholdFormDialogComponent', () => {
  let component: HouseholdFormDialogComponent;
  let fixture: ComponentFixture<HouseholdFormDialogComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [HouseholdFormDialogComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(HouseholdFormDialogComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
