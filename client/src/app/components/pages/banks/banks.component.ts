import { AfterViewInit, Component, ViewChild, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatPaginator, MatPaginatorModule } from '@angular/material/paginator';
import { MatSort, MatSortModule } from '@angular/material/sort';
import { MatTableDataSource, MatTableModule } from '@angular/material/table';
import { MatInputModule } from '@angular/material/input';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MaterialModule } from '../../../material.module';
import { MatDialog } from '@angular/material/dialog';
import { TranslateModule } from '@ngx-translate/core';

import { AppTranslateService } from '../../../services/app-translate.service';
import { BankService } from '../../../services/bank.service';
import { BankBase as Bank } from '../../../models/BankBase';
import { ApiResponse } from '../../../models/apiResponse';
import { BankFromDialogComponent } from './bank-from-dialog/bank-from-dialog.component';

@Component({
  selector: 'app-banks',
  imports: [
    CommonModule,
    MatFormFieldModule,
    MatInputModule,
    MatTableModule,
    MatSortModule,
    MatPaginatorModule,
    MaterialModule,
    TranslateModule
  ],
  templateUrl: './banks.component.html',
  styleUrl: './banks.component.css'
})
export class BanksComponent implements AfterViewInit {
  banks: Bank[] = [];
  isLoading: boolean = true;
  errorMessage: string = '';
  details: string = '';
  dataSource = new MatTableDataSource<Bank>();
  displayedColumns: string[] = ['id', 'name', 'description', 'active','actions'];
  @ViewChild(MatPaginator) paginator!: MatPaginator;
  @ViewChild(MatSort) sort!: MatSort;

  constructor(
    private bankService: BankService,
    private changeDetectorRef: ChangeDetectorRef,
    private dialog: MatDialog,
    private translateService: AppTranslateService,
    private cdRef: ChangeDetectorRef
  ) {}

  ngAfterViewInit(): void {
    this.bankService.getBanks().subscribe({
      next: (data: ApiResponse<Bank[]>) => {
        if(Array.isArray(data.response)) {
          this.banks = data.response;
          this.dataSource.data = this.banks;
        } else{
          this.errorMessage = data.response;
          this.banks = [];
          this.dataSource.data = [];
        }
        this.details =data.details;
        this.dataSource.data = this.banks;
        this.dataSource.paginator = this.paginator;
        this.dataSource.sort = this.sort;
        this.isLoading = false;
      },
      error: async (error) => {
        this.errorMessage = await this.translateService.translateKeyAsync('error.fetching.banks');
        this.isLoading = false;
      }
    });
  }
  addBank(): void {
    const bankData = {
      id: null, // o null si tu backend lo maneja así
      name: '',
      description: '',
      Active: true
    };

    const dialogRef = this.dialog.open(BankFromDialogComponent, {
      width: 'auto',
      height: 'auto',
      disableClose: true,
      data: bankData // Pasa el nuevo usuario vacío
    });

    dialogRef.afterClosed().subscribe(result => {
      if (result) {

        this.dataSource.data = [result, ...this.dataSource.data];
        this.cdRef.detectChanges(); // Notifica cambios
      }
    });
  }

  editBank(bank: Bank): void {
    const bankData = { ...bank }; // Crea una copia del usuario
    const dialogRef = this.dialog.open(BankFromDialogComponent, {
      width: 'auto',
      height: 'auto',
      disableClose: true,
      data: bankData
    });

    dialogRef.afterClosed().subscribe(result => {
      if (result) {
        const index = this.dataSource.data.findIndex(u => u.id === result.id);
        if (index !== -1) {
          const updatedData = [...this.dataSource.data];
          updatedData[index] = result;
          this.dataSource.data = updatedData;
          this.dataSource._updateChangeSubscription();
        }
      }
    });

  }
  applyFilter(event: Event) {
    const filterValue = (event.target as HTMLInputElement).value;
    this.dataSource.filter = filterValue.trim().toLowerCase();
  }
}
