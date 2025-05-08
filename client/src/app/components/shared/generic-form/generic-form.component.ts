import { Component, Input } from '@angular/core';
import { FormGroup, FormBuilder, Validators } from '@angular/forms';
import { FormFieldConfig } from './form-config';
import { CommonModule } from '@angular/common';
import { ReactiveFormsModule } from '@angular/forms';
import { MatSelectModule } from '@angular/material/select';


import { MaterialModule } from '../../../material.module';

@Component({
  selector: 'app-generic-form',
  templateUrl: './generic-form.component.html',
  imports: [MaterialModule, CommonModule,ReactiveFormsModule, MatSelectModule]
})
export class GenericFormComponent {
  @Input() fields: FormFieldConfig[] = [];
  @Input() initialData: any = {};
  form: FormGroup;

  constructor(private fb: FormBuilder) {
    this.form = this.fb.group({});
  }

  ngOnChanges() {
    this.buildForm();
  }

  buildForm() {
    const controls: any = {};
    this.fields.forEach(field => {
      const validators = field.validators || [];
      if (field.required) validators.push(Validators.required);
      controls[field.key] = [this.initialData[field.key] || '', validators];
    });
    this.form = this.fb.group(controls);
  }
}
