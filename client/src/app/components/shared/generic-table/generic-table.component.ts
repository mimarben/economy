import { Component, Input, Output, EventEmitter, ViewChild, AfterViewInit } from '@angular/core';
import { MatTableDataSource,MatTableModule } from '@angular/material/table';
import { MatPaginator, MatPaginatorModule } from '@angular/material/paginator';
import { MatSort,MatSortModule} from '@angular/material/sort';
import { TranslateModule } from '@ngx-translate/core';
import { CommonModule } from '@angular/common';


import { MaterialModule } from '../../../material.module';


export interface TableColumn<T> {
  key:  string; // Permite acceder a propiedades
  label: string;         // Nombre de la columna visible
  sortable?: boolean;
  formatter?: (value: any, row: T) => string; // Para formatear celdas
}

@Component({
  selector: 'app-generic-table',
  standalone: true, // Add this if using Angular Standalone Components
  imports: [
    CommonModule,
    MaterialModule,
    TranslateModule,
    MatPaginatorModule,
    MatTableModule,
    MatSortModule
  ],
  templateUrl: './generic-table.component.html',
  styleUrl: './generic-table.component.css'
})
export class GenericTableComponent<T> implements AfterViewInit {
  @Input() data: T[] = [];
  @Input() columns: TableColumn<T>[] = [];
  @Input() isLoading = false;
  @Input() errorMessage = '';
  @Input() filter = '';
  @Output() edit = new EventEmitter<T>();
  @Output() add = new EventEmitter<void>();

  dataSource = new MatTableDataSource<T>();

  @ViewChild(MatPaginator) paginator!: MatPaginator;
  @ViewChild(MatSort) sort!: MatSort;

  ngAfterViewInit() {
    this.dataSource.data = this.data;
    this.dataSource.paginator = this.paginator;
    this.dataSource.sort = this.sort;
  }

  ngOnChanges() {
    this.dataSource.data = this.data;
  }

  applyFilter(event: Event) {
    const filterValue = (event.target as HTMLInputElement).value;
    this.dataSource.filter = filterValue.trim().toLowerCase();
  }

  onEdit(row: T) {
    this.edit.emit(row);
  }

  onAdd() {
    this.add.emit();
  }

  get displayedColumns(): string[] {
    return [...this.columns.map(col => col.key as string), 'actions'];
  }
}
