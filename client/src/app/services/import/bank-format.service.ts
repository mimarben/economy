import { Injectable } from '@angular/core';
import { BANK_PROFILES } from "@const_models/ BankProfiles.const";

@Injectable({
  providedIn: 'root',
})
export class BankFormatService {
   getProfiles() {

    return BANK_PROFILES;

  }
  
}
