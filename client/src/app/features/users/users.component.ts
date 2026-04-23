import { ChangeDetectorRef, Component, OnInit } from '@angular/core';
import { MatDialog } from '@angular/material/dialog';
import { TranslateModule } from '@ngx-translate/core';

import { GenericTableComponent, TableColumn } from '@shared/generic-table/generic-table.component';
import { UserService } from '@users_services/user.service';
import { UserBase as User } from '@users_models/UserBase';
import { ApiResponse } from '@app/models/core/APIResponse';
import { UserFromDialogComponent } from './user-form-dialog/user-form-dialog.component';

@Component({
  selector: 'app-users',
  standalone: true,
  imports: [GenericTableComponent, TranslateModule],
  templateUrl: './users.component.html',
  styleUrl: './users.component.css'
})
export class UsersComponent implements OnInit {
  users: User[] = [];
  isLoading = true;
  errorMessage = '';
  details = '';
  filterValue = '';

  columns: TableColumn<User>[] = [
    { key: 'id', label: 'ID', sortable: true },
    { key: 'name', label: 'Name', sortable: true },
    { key: 'surname1', label: 'First Surname', sortable: true },
    { key: 'surname2', label: 'Second Surname', sortable: true },
    { key: 'dni', label: 'DNI', sortable: true },
    { key: 'email', label: 'Email', sortable: true },
    { key: 'active', label: 'Active', sortable: true, formatter: (value) => (value ? 'Yes' : 'No') },
    { key: 'telephone', label: 'Telephone', sortable: true },
    { key: 'role', label: 'Role', sortable: true },
    { key: 'accounts', label: 'Accounts', sortable: false, formatter: (value: { id: number; name: string }[]) => value?.map(a => a.name).join(', ') || 'None' },
  ];

  constructor(
    private userService: UserService,
    private dialog: MatDialog,
    private cdRef: ChangeDetectorRef
  ) {}

  ngOnInit(): void {
    this.loadUsers();
  }

  loadUsers(): void {
    this.isLoading = true;
    this.userService.getUsers().subscribe({
      next: (data: ApiResponse<User[]>) => {
        if (Array.isArray(data.response)) {
          this.users = data.response;
          this.errorMessage = '';
        } else {
          this.errorMessage = data.response;
          this.users = [];
        }
        this.details = data.details;
        this.isLoading = false;
      },
      error: () => {
        this.errorMessage = 'Error al cargar los usuarios';
        this.users = [];
        this.isLoading = false;
      },
    });
  }

  editUser(user: User): void {
    const userData = { ...user };
    const dialogRef = this.dialog.open(UserFromDialogComponent, {
      width: 'auto',
      height: 'auto',
      disableClose: true,
      data: userData,
    });

    dialogRef.afterClosed().subscribe((result) => {
      if (result) {
        const index = this.users.findIndex((u) => u.id === result.id);
        if (index !== -1) {
          const updatedUsers = [...this.users];
          updatedUsers[index] = result;
          this.users = updatedUsers;
          this.cdRef.detectChanges();
        }
      }
    });
  }

  addUser(): void {
    const userData = {
      id: null,
      name: '',
      surname1: '',
      surname2: '',
      dni: '',
      email: '',
      active: true,
      telephone: '',
      role: 'user',
      password: '',
    };

    const dialogRef = this.dialog.open(UserFromDialogComponent, {
      width: 'auto',
      height: 'auto',
      disableClose: true,
      data: userData,
    });

    dialogRef.afterClosed().subscribe((result) => {
      if (result) {
        this.users = [result, ...this.users];
        this.cdRef.detectChanges();
      }
    });
  }

  applyFilter(event: Event): void {
    this.filterValue = (event.target as HTMLInputElement).value
      .trim()
      .toLowerCase();
  }
}
