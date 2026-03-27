import { Component, Input, Output, EventEmitter, ViewChild, AfterViewInit, OnChanges, SimpleChanges } from '@angular/core';
import { MatTableDataSource, MatTableModule } from '@angular/material/table';
import { MatPaginator, MatPaginatorModule } from '@angular/material/paginator';
import { MatSort, MatSortModule } from '@angular/material/sort';
import { TranslateModule } from '@ngx-translate/core';
import { CommonModule } from '@angular/common';

import { MaterialModule } from '@app/utils/material.module';

export interface TableColumn<T> {
  key: string;
  label: string;
  sortable?: boolean;
  formatter?: (value: any, row: T) => string;
}

@Component({
  selector: 'app-generic-table',
  standalone: true,
  imports: [
    CommonModule,
    MaterialModule,
    TranslateModule,
    MatPaginatorModule,
    MatTableModule,
    MatSortModule,
  ],
  templateUrl: './generic-table.component.html',
  styleUrl: './generic-table.component.css',
})
export class GenericTableComponent<T> implements AfterViewInit, OnChanges {
  @Input() data: T[] = [];
  @Input() columns: TableColumn<T>[] = [];
  @Input() isLoading = false;
  @Input() errorMessage = '';
  @Input() filter = '';
  @Input() title = '';
  @Input() subtitle = '';
  @Input() addButtonLabel = 'Add';
  @Input() noDataMessage = 'No records found.';
  @Input() showDeleteAction = false;
  @Input() showRefreshAction = true;

  @Output() edit = new EventEmitter<T>();
  @Output() add = new EventEmitter<void>();
  @Output() delete = new EventEmitter<T>();
  @Output() refresh = new EventEmitter<void>();

  dataSource = new MatTableDataSource<T>([]);

  @ViewChild(MatPaginator) paginator!: MatPaginator;
  @ViewChild(MatSort) sort!: MatSort;

  ngAfterViewInit(): void {
    this.setupDataSource();
  }

  ngOnChanges(changes: SimpleChanges): void {
    if (changes['data']) {
      this.dataSource.data = this.data;
    }

    if (changes['filter'] && this.filter !== undefined) {
      this.dataSource.filter = this.filter.trim().toLowerCase();
    }
  }

  private setupDataSource(): void {
    this.dataSource.data = this.data;
    this.dataSource.paginator = this.paginator;
    this.dataSource.sort = this.sort;
  }

  applyFilter(event: Event): void {
    const filterValue = (event.target as HTMLInputElement).value;
    this.dataSource.filter = filterValue.trim().toLowerCase();
  }

  onEdit(row: T): void {
    this.edit.emit(row);
  }

  onDelete(row: T): void {
    this.delete.emit(row);
  }

  onAdd(): void {
    this.add.emit();
  }

  onRefresh(): void {
    this.refresh.emit();
  }

  get displayedColumns(): string[] {
    return [...this.columns.map((col) => col.key as string), 'actions'];
  }
}
