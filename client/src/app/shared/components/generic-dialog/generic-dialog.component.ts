import { Component, Inject, ViewChild } from '@angular/core';
import { MAT_DIALOG_DATA, MatDialogRef } from '@angular/material/dialog';
import { MatDialogModule } from '@angular/material/dialog';

import { FormFieldConfig } from '../generic-form/form-config';
import { GenericFormComponent } from '../generic-form/generic-form.component';
import { MATERIAL_IMPORTS } from '@app/utils/material.imports';

@Component({
  selector: 'app-generic-dialog',
  styleUrl: './generic-dialog.component.css',
  templateUrl: './generic-dialog.component.html',
  imports: [GenericFormComponent, MatDialogModule, ...MATERIAL_IMPORTS]
})
export class GenericDialogComponent {
  @ViewChild(GenericFormComponent) genericFormComponent!: GenericFormComponent;
  isFormValid: boolean = false;
  isFormDirty: boolean = false;
  constructor(
    public dialogRef: MatDialogRef<GenericDialogComponent>,
    @Inject(MAT_DIALOG_DATA) public data: {
      title: string;
      fields: FormFieldConfig[];
      initialData: any;
    }
  ) {}
  ngAfterViewInit(): void {
    if (this.genericFormComponent) {
      this.genericFormComponent.formValidity.subscribe(valid => {
        this.isFormValid = valid;
      });
      this.genericFormComponent.formDirty.subscribe(dirty => {
        this.isFormDirty = dirty;
      });
    }
  }
  onSave() {
    if (this.genericFormComponent?.form?.valid) {
      this.dialogRef.close(this.genericFormComponent.form.getRawValue());
    } else {
      this.genericFormComponent?.form?.markAllAsTouched();
    }
  }

  onCancel() {
    console.log("Cancel")
    this.dialogRef.close();
  }
}
