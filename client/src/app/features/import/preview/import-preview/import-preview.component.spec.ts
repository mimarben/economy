import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ImportPreviewComponent } from './import-preview.component';

describe('ImportPreviewComponent', () => {
  let component: ImportPreviewComponent;
  let fixture: ComponentFixture<ImportPreviewComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ImportPreviewComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(ImportPreviewComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
