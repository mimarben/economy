import { TestBed } from '@angular/core/testing';

import { ImportTransformService } from './import-transform.service';

describe('ImportTransformService', () => {
  let service: ImportTransformService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(ImportTransformService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
