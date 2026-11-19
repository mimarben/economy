import { Component, OnInit, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { AbstractControl, FormBuilder, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { MATERIAL_IMPORTS } from '@app/utils/material.imports';

import { AuthService } from '@auth_services/auth.service';
import { UserService } from '@users_services/user.service';
import { ToastService } from '@core_services/toast.service';
import { UserBase as User } from '@users_models/UserBase';
import { ApiResponse } from '@app/models/core/APIResponse';
import { environment } from '@env/environment';

@Component({
  selector: 'app-profile',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule, ...MATERIAL_IMPORTS],
  templateUrl: './profile.component.html',
  styleUrl: './profile.component.scss'
})
export class ProfileComponent implements OnInit {
  private readonly fb = inject(FormBuilder);
  private readonly auth = inject(AuthService);
  private readonly userService = inject(UserService);
  private readonly toastService = inject(ToastService);

  readonly user = signal<User | null>(null);
  readonly loadingProfile = signal(true);
  readonly savingProfile = signal(false);
  readonly savingPassword = signal(false);
  readonly hideCurrent = signal(true);
  readonly hideNew = signal(true);
  readonly hideConfirm = signal(true);

  profileForm: FormGroup = this.fb.group({
    name: ['', [Validators.required, Validators.minLength(2)]],
    surname1: ['', [Validators.required]],
    surname2: [''],
    email: ['', [Validators.required, Validators.email]],
    telephone: [null, [Validators.pattern(/^\d{9}$/)]],
    dni: ['', [Validators.required, this.validateDNI]],
  });

  passwordForm: FormGroup = this.fb.group(
    {
      current_password: ['', [Validators.required]],
      new_password: ['', [Validators.required, this.strongPassword]],
      confirm_password: ['', [Validators.required]],
    },
    { validators: [this.passwordsMatch] }
  );

  ngOnInit(): void {
    const userId = this.auth.getUserId();
    if (!userId) {
      this.loadingProfile.set(false);
      return;
    }
    this.userService.getById(userId).subscribe({
      next: (response: ApiResponse<User>) => {
        this.user.set(response.response);
        this.profileForm.patchValue(response.response);
        this.loadingProfile.set(false);
      },
      error: () => this.loadingProfile.set(false),
    });
  }

  get profileControls() {
    return this.profileForm.controls;
  }

  get passwordControls() {
    return this.passwordForm.controls;
  }

  saveProfile(): void {
    if (this.profileForm.invalid || this.savingProfile()) {
      return;
    }
    const userId = this.auth.getUserId();
    if (!userId) {
      return;
    }
    this.savingProfile.set(true);
    // Only profile fields: role, active and password never travel from here.
    const { name, surname1, surname2, dni, email, telephone } = this.profileForm.value;
    this.userService.updateUser(userId, { name, surname1, surname2, dni, email, telephone }).subscribe({
      next: (response: ApiResponse<User>) => {
        this.savingProfile.set(false);
        this.user.set(response.response);
        this.toastService.showToast(response, environment.toastType.Success, {});
      },
      error: (error: any) => {
        this.savingProfile.set(false);
        this.toastService.showToast(error.error as ApiResponse<string>, environment.toastType.Error, {});
      },
    });
  }

  changePassword(): void {
    if (this.passwordForm.invalid || this.savingPassword()) {
      return;
    }
    this.savingPassword.set(true);
    const { current_password, new_password } = this.passwordForm.value;
    this.auth.changePassword(current_password, new_password).subscribe({
      next: (response) => {
        this.savingPassword.set(false);
        this.passwordForm.reset();
        this.toastService.showToast(response, environment.toastType.Success, {});
      },
      error: (error: any) => {
        this.savingPassword.set(false);
        this.toastService.showToast(error.error as ApiResponse<string>, environment.toastType.Error, {});
      },
    });
  }

  /** Same DNI check as the user form (8 digits + control letter). */
  private validateDNI(control: AbstractControl) {
    const value: string = control.value;
    if (!value) {
      return null;
    }
    if (!/^[0-9]{8}[A-Za-z]$/.test(value)) {
      return { invalidDNI: true };
    }
    const dniLetters = 'TRWAGMYFPDXBNJZSQVHLCKE';
    const numbers = value.slice(0, 8);
    const letter = value.slice(-1).toUpperCase();
    const expectedLetter = dniLetters[parseInt(numbers, 10) % 23];
    return letter === expectedLetter ? null : { invalidDNI: true };
  }

  /** Mirrors the backend policy: >= 8 chars with upper, lower, digit and symbol. */
  private strongPassword(control: AbstractControl) {
    const value: string = control.value ?? '';
    if (!value) {
      return null;
    }
    const valid =
      value.length >= 8 &&
      /[A-Z]/.test(value) &&
      /[a-z]/.test(value) &&
      /\d/.test(value) &&
      /[^\w\s]/.test(value);
    return valid ? null : { strongPassword: true };
  }

  private passwordsMatch(group: AbstractControl) {
    const newPassword = group.get('new_password')?.value;
    const confirmPassword = group.get('confirm_password')?.value;
    return newPassword && confirmPassword && newPassword !== confirmPassword
      ? { passwordsMismatch: true }
      : null;
  }
}
