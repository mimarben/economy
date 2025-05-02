import { Component, Inject } from '@angular/core';
import { MAT_DIALOG_DATA, MatDialogRef } from '@angular/material/dialog';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { MaterialModule } from '../../../../material.module';


import { UserBase as User } from '../../../../models/UserBase';
import { UserService } from '../../../../services/user.service';
import { ApiResponse } from '../../../../models/apiResponse';
import { ToastService } from '../../../../services/toast.service';
import { environment } from '../../../../../environments/environment';
@Component({
  selector: 'app-user-form-dialog',
  imports: [CommonModule,
            MaterialModule,
            ReactiveFormsModule],
  templateUrl: './user-form-dialog.component.html',
  styleUrl: './user-form-dialog.component.css'
})
export class EditUserDialogComponent {
  errorMessage: string | null = null; // Add errorMessage property
  isLoading = false;
  userForm: FormGroup;
  isEditMode = false;
  constructor(
    private fb: FormBuilder,
    public dialogRef: MatDialogRef<EditUserDialogComponent>,
    @Inject(MAT_DIALOG_DATA) public data: User,
    private userService: UserService,
    private toastService: ToastService) {
      this.isEditMode = !!data?.id;
      this.userForm = this.fb.group({
        name: [this.isEditMode ? data.name : '', [Validators.required, Validators.minLength(2)]],
        surname1: [this.isEditMode ? data.surname1 : '', [Validators.required]],
        surname2: [this.isEditMode ? data.surname2 : ''], // Opcional
        email: [this.isEditMode ? data.email : '', [Validators.required, Validators.email]],
        telephone: [this.isEditMode ? data.telephone : null, [Validators.pattern(/^\d{9}$/)]],
        dni: [this.isEditMode ? data.dni : '', [Validators.required, this.validateDNI]],
        active: [this.isEditMode ? data.active : true],
      });
      // Detecta si es modo edición
    }

    // Validador personalizado para DNI español (8 números y 1 letra)
    validateDNI(control: any) {
      const value = control.value;
      const dniRegex = /^[0-9]{8}[A-Za-z]$/;

      if (!value) {
        return null; // Deja que Validators.required se encargue si es requerido
      }

      if (!dniRegex.test(value)) {
        return { invalidDNI: true };
      }

      // Cálculo de la letra del DNI según el módulo 23
      const dniLetters = "TRWAGMYFPDXBNJZSQVHLCKE";
      const numbers = value.slice(0, 8);
      const letter = value.slice(-1).toUpperCase();

      const expectedLetter = dniLetters[parseInt(numbers, 10) % 23];

      return letter === expectedLetter ? null : {
        invalidDNI: true,
        message: `DNI ${numbers} es '${expectedLetter}'.`
      };
    }

  // Getter para acceder fácilmente a los errores de los campos
  get formControls() {
    return this.userForm.controls;
  }
    updateUser() {
      this.errorMessage = null;
      this.isLoading = true;
      if (this.userForm.valid) {
        const userData = this.userForm.value;
        console.log('User data:', userData);
        if (this.isEditMode && this.data?.id) {
        console.log('User ID:', this.userForm.value.id);
        this.userService.updateUser(this.data.id, userData).subscribe({
          next: (response: ApiResponse<User>) => {
            this.isLoading = false;
            this.toastService.showToast(response,environment.toastType.Success, {});
          },
          error: (error) => {
            console.error('Error updating user:', error.error);
            this.isLoading = false;
            this.toastService.showToast(error.error as ApiResponse<string>,environment.toastType.Error, {});
            this.dialogRef.close(this.userForm.value);
          }
        });
      }
      else {
        // Modo creación
        this.userService.createUser(userData).subscribe({
          next: (response: ApiResponse<User>) => {
            this.isLoading = false;
            this.toastService.showToast(response, environment.toastType.Success, {});
            this.dialogRef.close(response.response); // Devuelve el usuario creado
          },
          error: (error) => {
            console.error('Error creating user:', error.error);
            this.isLoading = false;
            this.errorMessage = 'Failed to create user.';
            this.toastService.showToast(error.error as ApiResponse<string>, environment.toastType.Error, {});
          }
        });
      }
        this.dialogRef.close(this.userForm.value);
      }

    }

  onCancel() {
    this.dialogRef.close();
  }

}
