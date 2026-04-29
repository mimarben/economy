import { Injectable } from '@angular/core';
import { BANK_PROFILES } from "@app/core/const/bank-profiles.const";

@Injectable({
  providedIn: 'root',
})
export class BankFormatService {
   getProfiles() {

    return BANK_PROFILES;

  }
  
}
