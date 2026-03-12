import { Injectable } from '@angular/core';
import { BANK_PROFILES } from "@app/core/import/bank-profiles.const";

@Injectable({
  providedIn: 'root',
})
export class BankFormatService {
   getProfiles() {

    return BANK_PROFILES;

  }
  
}
