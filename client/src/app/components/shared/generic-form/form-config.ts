import { ValidatorFn } from '@angular/forms';

export type FormFieldType = 'text' | 'number' | 'email' | 'password' | 'checkbox' | 'select';

export interface FormFieldConfig {
  key: string;
  label: string;
  type: 'text' | 'number' | 'email' | 'select' | 'checkbox';
  required?: boolean;
  validators?: ValidatorFn[];
  options?: { value: string | number; label: string }[]; // For select fields
  minLength?: number; // For text/email fields
  maxLength?: number; // For text/email fields
  pattern?: string; // For text/email fields
  min?: number; // For number fields
  max?: number; // For number fields
}

