import { Component, OnInit } from '@angular/core';
import * as XLSX from 'xlsx';
import { BankFormatService } from '@import_services/bank-format.service';
import { BankProfile } from "@import_models/BankProfile";
import { BankService } from '@finance_services/bank.service';
import { BankBase as Bank} from '@finance_models/BankBase';
import { ToastService } from '@core_services/toast.service';
import { environment } from '@env/environment';
import { ApiResponse } from '@core_models/apiResponse';
import { AppTranslateService } from '@utils/app-translate.service';
import { TranslateModule } from '@ngx-translate/core';
import { MaterialModule } from '@utils/material.module';
@Component({
  selector: 'app-excel-import',
  imports: [TranslateModule, MaterialModule],
  templateUrl: './excel-import.component.html',
  styleUrl: './excel-import.component.scss',
})
export class ExcelImportComponent implements OnInit {
  excelHeaders: string[] = [];
  excelRows: any[] = [];
  banks: Bank[] = [];
  selectedBank: Bank | null = null;
  constructor(private bankService: BankService,
              private toastService: ToastService,
              private translateService: AppTranslateService
  ){
    
  }
  ngOnInit(): void {
    console.log("import excel component loaded");
    this.bankService.getBanks().subscribe({
      next: (res)=>{
        console.log("Api details:", res.details);
        console.log("Api response", res.response)
        this.banks= res.response
        console.log(this.banks);
      },
      error: (error)=>{
        console.error("Error loading banks", error);
        this.toastService.showToast(
                 error.error as ApiResponse<string>,
                 environment.toastType.Error,
                 {}
               );
      }
    })
  }
  
  onBankSelected(bankId: number){
    const id = Number(bankId);
    const bank = this.banks.find(b=>b.id ===id);
    if (!bank){
      console.warn("Bank not found");
      this.toastService.success(this.translateService.translateKey('BANK.NOT_FOUND'));
      return;
    }
    this.selectedBank = bank;

    console.log("Selected bank:", bank);
  }
  
  onFileChange(event: Event) {

    const input = event.target as HTMLInputElement;

    if (!input.files?.length) return;

    const file = input.files[0];

    const reader = new FileReader();

    reader.onload = (e: any) => {

      const workbook = XLSX.read(e.target.result, {
        type: 'binary'
      });

      const sheetName = workbook.SheetNames[0];

      const sheet = workbook.Sheets[sheetName];

      const data = XLSX.utils.sheet_to_json(sheet, {
        header: 1,
        raw: false
      });

      this.excelHeaders = data[0] as string[];
      this.excelRows = data.slice(1);

      console.log(this.excelHeaders);
      console.log(this.excelRows);

    };

    reader.readAsBinaryString(file);

  }
  
}
