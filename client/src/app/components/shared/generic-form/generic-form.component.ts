import { Component, Input } from '@angular/core';
import { FormGroup, FormBuilder, Validators } from '@angular/forms';


@Component({
  selector: 'app-generic-form',
  templateUrl: './generic-form.component.html',
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
