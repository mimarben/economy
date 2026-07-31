import { Component, OnInit, inject } from '@angular/core';
import {
  AbstractControl,
  ValidationErrors,
  Validators,
  ReactiveFormsModule,
  NonNullableFormBuilder,
} from '@angular/forms';
import { Router } from '@angular/router';
import { TranslateModule } from '@ngx-translate/core';
import { AuthService } from '@auth_services/auth.service';

import { CommonModule } from '@angular/common';
import { HttpErrorResponse } from '@angular/common/http';
import { MATERIAL_IMPORTS } from '@app/utils/material.imports';
import { AppTranslateService } from '@utils/app-translate.service';
import { HotToastService } from '@ngxpert/hot-toast';
import { dniValidator, passwordComplexityValidator } from '@utils/validators/dni-password.validators';

/** Group-level validator ensuring password and confirm match. */
function passwordsMatch(group: AbstractControl): ValidationErrors | null {
  const password = group.get('password')?.value;
  const confirm = group.get('confirmPassword')?.value;
  if (!confirm) {
    return null; // empty confirm is handled by Validators.required
  }
  return password === confirm ? null : { passwordsMismatch: true };
}

@Component({
  selector: 'app-register',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule, ...MATERIAL_IMPORTS, TranslateModule],
  templateUrl: './register.component.html',
  styleUrl: './register.component.scss',
})
export class RegisterComponent implements OnInit {
  private fb = inject(NonNullableFormBuilder);
  private authService = inject(AuthService);
  private router = inject(Router);
  private toast = inject(HotToastService);
  private appTranslateService = inject(AppTranslateService);

  hidePassword = true;
  hideConfirm = true;
  isLoading = false;

  registerForm = this.fb.group(
    {
      name: ['', [Validators.required, Validators.minLength(2)]],
      surname1: ['', [Validators.required]],
      surname2: [''],
      dni: ['', [Validators.required, dniValidator()]],
      email: ['', [Validators.required, Validators.email]],
      telephone: ['', [Validators.pattern(/^\d{9}$/)]],
      password: ['', [Validators.required, Validators.minLength(8), passwordComplexityValidator()]],
      confirmPassword: ['', [Validators.required]],
    },
    { validators: [passwordsMatch] },
  );

  ngOnInit(): void {
    this.appTranslateService.initialize();
  }

  onSubmit(): void {
    if (this.registerForm.invalid) {
      this.registerForm.markAllAsTouched();
      return;
    }

    this.isLoading = true;
    const raw = this.registerForm.getRawValue();

    this.authService
      .register({
        name: raw.name,
        surname1: raw.surname1,
        surname2: raw.surname2 || undefined,
        dni: raw.dni,
        email: raw.email,
        telephone: raw.telephone ? Number(raw.telephone) : undefined,
        password: raw.password,
      })
      .subscribe({
        next: () => {
          this.toast.success('Account created successfully');
          this.router.navigateByUrl('/login');
        },
        error: (err: HttpErrorResponse) => {
          // 409 → backend raised EMAIL_ALREADY_EXISTS / DNI_ALREADY_EXISTS
          if (err.status === 409) {
            this.toast.error('Ya existe una cuenta con ese email o DNI');
          } else {
            this.toast.error(err?.error?.details || 'No se pudo crear la cuenta');
          }
          this.isLoading = false;
        },
      });
  }
}
