import { ComponentFixture, TestBed } from '@angular/core/testing';

import { BankFromDialogComponent } from './bank-from-dialog.component';

describe('BankFromDialogComponent', () => {
  let component: BankFromDialogComponent;
  let fixture: ComponentFixture<BankFromDialogComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [BankFromDialogComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(BankFromDialogComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
