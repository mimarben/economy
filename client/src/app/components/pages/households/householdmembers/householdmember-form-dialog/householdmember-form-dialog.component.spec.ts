import { ComponentFixture, TestBed } from '@angular/core/testing';

import { HouseholdmemberFormDialogComponent } from './householdmember-form-dialog.component';

describe('HouseholdmemberFormDialogComponent', () => {
  let component: HouseholdmemberFormDialogComponent;
  let fixture: ComponentFixture<HouseholdmemberFormDialogComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [HouseholdmemberFormDialogComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(HouseholdmemberFormDialogComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
