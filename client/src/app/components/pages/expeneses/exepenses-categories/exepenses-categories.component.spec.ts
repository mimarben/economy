import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ExepensesCategoriesComponent } from './exepenses-categories.component';

describe('ExepensesCategoriesComponent', () => {
  let component: ExepensesCategoriesComponent;
  let fixture: ComponentFixture<ExepensesCategoriesComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ExepensesCategoriesComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(ExepensesCategoriesComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
