import { TestBed } from '@angular/core/testing';

import { BankFormatService } from './bank-format.service';

describe('BankFormatService', () => {
  let service: BankFormatService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(BankFormatService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
