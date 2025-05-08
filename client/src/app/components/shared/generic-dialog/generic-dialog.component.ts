import { Component, Inject } from '@angular/core';
import { MAT_DIALOG_DATA, MatDialogRef } from '@angular/material/dialog';
import { FormFieldConfig } from '../form-config';

@Component({
  selector: 'app-generic-dialog',
  template: `
    <h2 mat-dialog-title>{{ data.title }}</h2>
    <app-generic-form
      [fields]="data.fields"
      [initialData]="data.initialData"
    ></app-generic-form>
    <mat-dialog-actions>
      <button mat-button (click)="onCancel()">Cancel</button>
      <button mat-raised-button color="primary" (click)="onSave()">Save</button>
    </mat-dialog-actions>
  `
})
export class GenericDialogComponent {
  constructor(
    public dialogRef: MatDialogRef<GenericDialogComponent>,
    @Inject(MAT_DIALOG_DATA) public data: {
      title: string;
      fields: FormFieldConfig[];
      initialData: any;
    }
  ) {}

  onSave() {
    this.dialogRef.close(this.data.initialData);
  }

  onCancel() {
    this.dialogRef.close();
  }
}
