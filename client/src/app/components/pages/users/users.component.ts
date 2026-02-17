import { AfterViewInit, Component, ViewChild, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatPaginator, MatPaginatorModule } from '@angular/material/paginator';
import { MatSort, MatSortModule } from '@angular/material/sort';
import { MatTableDataSource, MatTableModule } from '@angular/material/table';
import { MatInputModule } from '@angular/material/input';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MaterialModule } from '@utils/material.module';
import { MatDialog } from '@angular/material/dialog';
import { TranslateModule } from '@ngx-translate/core';

import { UserService } from '@users_services/user.service';
import { UserBase as User } from '@users_models/UserBase';
import { ApiResponse } from '@core_models/apiResponse';
import { UserFromDialogComponent } from './user-form-dialog/user-form-dialog.component';
@Component({
  selector: 'app-users',
  standalone: true, // Add this if using Angular Standalone Components
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
    'id', 'name', 'Surname1', 'Surname2', 'Dni', 'Email', 'Active', 'telephone', 'Role', 'Password','actions'
  ];

  @ViewChild(MatPaginator) paginator!: MatPaginator;
  @ViewChild(MatSort) sort!: MatSort;

  constructor(
    private userService: UserService,
    private dialog: MatDialog,
    private cdRef: ChangeDetectorRef) {}

  ngAfterViewInit() {
    this.userService.getUsers().subscribe({
      next: (data: ApiResponse<User[]>) => {
        if (Array.isArray(data.response)) {
          this.users = data.response;
          this.dataSource.data = this.users;
        } else {
          // Si response es un string, puedes manejarlo como error o mensaje informativo
          this.errorMessage = data.response;
          this.users = []; // O manejarlo como prefieras
          this.dataSource.data = [];
        }
        this.details = data.details;
        this.dataSource.data = this.users;
        this.dataSource.paginator = this.paginator;
        this.dataSource.sort = this.sort;
        this.isLoading = false;
      },
      error: (error: any) => {
        this.errorMessage = 'Error al cargar los usuarios';
        this.isLoading = false;
      },
    });
  }

  applyFilter(event: Event) {
    const filterValue = (event.target as HTMLInputElement).value;
    this.dataSource.filter = filterValue.trim().toLowerCase();
  }

  editUser(user: User): void {
    const userData = { ...user }; // Crea una copia del usuario
    const dialogRef = this.dialog.open(UserFromDialogComponent, {
      width: 'auto',
      height: 'auto',
      disableClose: true,
      data: userData
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

  addUser(): void {
    const userData = {
      id: null, // o null si tu backend lo maneja así
      name: '',
      Surname1: '',
      Surname2: '',
      Dni: '',
      Email: '',
      Active: true,
      telephone: '',
      Role: 'USER',
      Password: ''
    };

    const dialogRef = this.dialog.open(UserFromDialogComponent, {
      width: 'auto',
      height: 'auto',
      disableClose: true,
      data: userData // Pasa el nuevo usuario vacío
    });

    dialogRef.afterClosed().subscribe(result => {
      if (result) {
        console.log('Nuevo usuario creado:', result);
        // Añade el nuevo usuario a la tabla
        this.dataSource.data = [result, ...this.dataSource.data];
        this.cdRef.detectChanges(); // Notifica cambios
      }
    });
  }
}
