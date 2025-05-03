import { ComponentFixture, TestBed } from '@angular/core/testing';

import { HouseholdmembersComponent } from './householdmembers.component';

describe('HouseholdmembersComponent', () => {
  let component: HouseholdmembersComponent;
  let fixture: ComponentFixture<HouseholdmembersComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [HouseholdmembersComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(HouseholdmembersComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
