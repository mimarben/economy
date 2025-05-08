// form-config.ts
export type FormFieldType = 'text' | 'number' | 'email' | 'password' | 'checkbox' | 'select';

export interface FormFieldConfig {
  key: string;
  label: string;
  type: FormFieldType;
  required?: boolean;
  validators?: any[];
  options?: { value: any; label: string }[]; // Para selects
}
