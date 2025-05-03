import { Component, Inject } from '@angular/core';
import { MAT_DIALOG_DATA, MatDialogRef } from '@angular/material/dialog';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { MaterialModule } from '../../../../material.module';

import { BankBase as Bank } from '../../../../models/BankBase';
import { BankService } from '../../../../services/bank.service';
import { ApiResponse } from '../../../../models/apiResponse';
import { ToastService } from '../../../../services/toast.service';
import { environment } from '../../../../../environments/environment';

@Component({
  selector: 'app-bank-from-dialog',
  imports: [
    CommonModule,
    MaterialModule,
    ReactiveFormsModule
  ],
  templateUrl: './bank-from-dialog.component.html',
  styleUrl: './bank-from-dialog.component.css'
})
export class BankFromDialogComponent {
  errorMessage: string | null = null; // Add errorMessage property
  isLoading = false;
  bankForm: FormGroup;
  isEditMode = false;
  constructor(
    private fb: FormBuilder,
    public dialogRef: MatDialogRef<BankFromDialogComponent>,
    @Inject(MAT_DIALOG_DATA) public data: Bank,
    private bankService: BankService,
    private toastService: ToastService) {
      this.isEditMode = !!data?.id;
      this.bankForm = this.fb.group({
        id: [this.isEditMode ? data.id : ''],
        name: [this.isEditMode ? data.name : '', [Validators.required, Validators.minLength(2)]],
        description: [this.isEditMode ? data.description : '', [Validators.required]],
        active: [this.isEditMode ? data.active : true],
      });
    }
  // Getter para acceder fácilmente a los errores de los campos
  get formControls() {
    return this.bankForm.controls;
  }
  updateBank() {
    this.errorMessage = null;
    this.isLoading = true;
    if (this.bankForm.valid) {
      const bankData = this.bankForm.value;
      if (this.isEditMode && this.data?.id) {
      this.bankService.updateBank(this.data.id, bankData).subscribe({
        next: (response: ApiResponse<Bank>) => {
          this.isLoading = false;
          this.toastService.showToast(response,environment.toastType.Success, {});
        },
        error: (error) => {
          console.error('Error updating bank:', error.error);
          this.isLoading = false;
          this.toastService.showToast(error.error as ApiResponse<string>,environment.toastType.Error, {});
          this.dialogRef.close(this.bankForm.value);
        }
      });
    }
    else {
      // Modo creación
      this.bankService.createBank(bankData).subscribe({
        next: (response: ApiResponse<Bank>) => {
          this.isLoading = false;
          this.toastService.showToast(response, environment.toastType.Success, {});
          this.dialogRef.close(response.response); // Devuelve el usuario creado
        },
        error: (error) => {
          console.error('Error creating bank:', error.error);
          this.isLoading = false;
          this.errorMessage = 'Failed to create bank.';
          this.toastService.showToast(error.error as ApiResponse<string>, environment.toastType.Error, {});
        }
      });
    }
      this.dialogRef.close(bankData);
    }

  }

  onCancel() {
    this.dialogRef.close();
  }

}
