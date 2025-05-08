import { Component, Inject } from '@angular/core';
import { MAT_DIALOG_DATA, MatDialogRef } from '@angular/material/dialog';
import { MatDialogModule } from '@angular/material/dialog';

import { FormFieldConfig } from '../generic-form/form-config';
import { GenericFormComponent } from '../generic-form/generic-form.component';
@Component({
  selector: 'app-generic-dialog',
  templateUrl: './generic-dialog.component.html',
  imports: [GenericFormComponent, MatDialogModule]
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
