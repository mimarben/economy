import { AfterViewInit, Component, ViewChild } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatPaginator, MatPaginatorModule } from '@angular/material/paginator';
import { MatSort, MatSortModule } from '@angular/material/sort';
import { MatTableDataSource, MatTableModule } from '@angular/material/table';
import { MatInputModule } from '@angular/material/input';
import { MatFormFieldModule } from '@angular/material/form-field';

import { UserService } from '../../../services/user.service';
import { UserBase as User } from '../../../models/UserBase';
import { ApiResponse } from '../../../models/apiResponse';

@Component({
  selector: 'app-users',
  standalone: true, // Add this if using Angular Standalone Components
  imports: [
    CommonModule,
    MatFormFieldModule,
    MatInputModule,
    MatTableModule,
    MatSortModule,
    MatPaginatorModule
  ],
  templateUrl: './users.component.html',
  styleUrl: './users.component.css'
})
export class UsersComponent implements AfterViewInit {
  users: User[] = [];
  isLoading = true;
  errorMessage = '';
  details = '';
  dataSource = new MatTableDataSource<User>();
  displayedColumns: string[] = [
    'id', 'name', 'Surname1', 'Surname2', 'Dni', 'Email', 'Active', 'telephone'
  ];

  @ViewChild(MatPaginator) paginator!: MatPaginator;
  @ViewChild(MatSort) sort!: MatSort;

  constructor(private userService: UserService) {}

  ngAfterViewInit() {
    this.userService.getUsers().subscribe({
      next: (data: ApiResponse<User[]>) => {
        this.users = data.response;
        this.details = data.details;
        this.dataSource.data = this.users;
        this.dataSource.paginator = this.paginator;
        this.dataSource.sort = this.sort;
        this.isLoading = false;
      },
      error: (error) => {
        this.errorMessage = 'Error al cargar los usuarios';
        this.isLoading = false;
      },
    });
  }

  applyFilter(event: Event) {
    const filterValue = (event.target as HTMLInputElement).value;
    this.dataSource.filter = filterValue.trim().toLowerCase();
  }
}
