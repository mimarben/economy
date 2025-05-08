import { Component, Inject } from '@angular/core';
import { MAT_DIALOG_DATA, MatDialogRef } from '@angular/material/dialog';
import { MatDialogModule } from '@angular/material/dialog';

import { FormFieldConfig } from '../generic-form/form-config';
import { GenericFormComponent } from '../generic-form/generic-form.component';
import { MaterialModule } from '../../../material.module';
@Component({
  selector: 'app-generic-dialog',
  styleUrl: './generic-dialog.component.css',
  templateUrl: './generic-dialog.component.html',
  imports: [GenericFormComponent, MatDialogModule, MaterialModule]
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
