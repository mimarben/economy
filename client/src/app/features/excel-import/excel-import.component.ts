import { Component } from '@angular/core';
import * as XLSX from 'xlsx';

@Component({
  selector: 'app-excel-import',
  imports: [],
  templateUrl: './excel-import.component.html',
  styleUrl: './excel-import.component.scss',
})
export class ExcelImportComponent {
  excelHeaders: string[] = [];
  excelRows: any[] = [];
  
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
