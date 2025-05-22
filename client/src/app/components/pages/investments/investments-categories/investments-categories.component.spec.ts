import { ComponentFixture, TestBed } from '@angular/core/testing';

import { InvestmentsCategoriesComponent } from './investments-categories.component';

describe('InvestmentsCategoriesComponent', () => {
  let component: InvestmentsCategoriesComponent;
  let fixture: ComponentFixture<InvestmentsCategoriesComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [InvestmentsCategoriesComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(InvestmentsCategoriesComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
