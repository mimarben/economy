import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';
import { UserBase as User  } from '../models/UserBase';
import { ApiResponse } from '../models/apiResponse';

@Injectable({
  providedIn: 'root'
})


export class UserService {
  private apiUrl = environment.apiUrl; // Define la URL base de tu API

  constructor(private http: HttpClient) {
    console.log(this.apiUrl+"/users");
  }

// Método para obtener todos los usuarios
getUsers(): Observable<ApiResponse<User[]>> {
  return this.http.get<ApiResponse<User[]>>(`${this.apiUrl}/users`);
}
getUserById(id: number): Observable<User> {
  return this.http.get<User>(`${this.apiUrl}/${id}`);
}

}
