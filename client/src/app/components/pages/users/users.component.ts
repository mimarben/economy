import { Component } from '@angular/core';
import { OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';

import { UserService } from '../../../services/user.service';
import { UserBase as User } from '../../../models/UserBase';
import { ApiResponse } from '../../../models/apiResponse';
@Component({
  selector: 'app-users',
  imports: [
    CommonModule,
  ],
  templateUrl: './users.component.html',
  styleUrl: './users.component.css'
})
export class UsersComponent  implements OnInit {
  users: User[] = [];
  isLoading: boolean = true;
  errorMessage: string = '';
  details: string = '';
  constructor(private userService: UserService) {}

  ngOnInit(): void {
    this.userService.getUsers().subscribe({
      next: (data: ApiResponse<User[]>) => {
        this.users = data.response;
        this.details = data.details;
        this.isLoading = false;
      },
      error: (error) => {
        this.errorMessage = 'Error al cargar los usuarios';
        this.isLoading = false;
      },
    });
  }
}
