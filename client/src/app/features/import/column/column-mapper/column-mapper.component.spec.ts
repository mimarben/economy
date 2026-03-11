import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ColumnMapperComponent } from './column-mapper.component';

describe('ColumnMapperComponent', () => {
  let component: ColumnMapperComponent;
  let fixture: ComponentFixture<ColumnMapperComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ColumnMapperComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(ColumnMapperComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
