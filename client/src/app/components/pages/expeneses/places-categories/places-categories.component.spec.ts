import { ComponentFixture, TestBed } from '@angular/core/testing';

import { PlacesCategoriesComponent } from './places-categories.component';

describe('PlacesCategoriesComponent', () => {
  let component: PlacesCategoriesComponent;
  let fixture: ComponentFixture<PlacesCategoriesComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [PlacesCategoriesComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(PlacesCategoriesComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
