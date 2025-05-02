import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
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
  }

  private getHeaders(): HttpHeaders {
    return new HttpHeaders(environment.headers);
  }
getUsers(): Observable<ApiResponse<User[]>> {
  return this.http.get<ApiResponse<User[]>>(`${this.apiUrl}/users`);
}
getUserById(id: number): Observable<ApiResponse<User>> {
  return this.http.get<ApiResponse<User>>(`${this.apiUrl}/${id}`);
}
createUser(user: User): Observable<ApiResponse<User>> {
  return this.http.post<ApiResponse<User>>(`${this.apiUrl}/users`, user, { headers: this.getHeaders() } );
}
updateUser(id: number, user: User): Observable<ApiResponse<User>> {
  console.log('Updating user:', user);
  console.log('User ID:', id);
  return this.http.patch<ApiResponse<User>>(`${this.apiUrl}/users/${id}`, user, { headers: this.getHeaders() });
}

}
