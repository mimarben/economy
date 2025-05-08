// form-factory.service.ts
import { Injectable } from '@angular/core';
import { FormFieldConfig } from '../../components/shared/generic-form/form-config';

@Injectable({ providedIn: 'root' })
export class FormFactoryService {
  getFormConfig(modelType: 'account' | 'bank' | 'user'): FormFieldConfig[] {
    switch (modelType) {
      case 'account':
        return [
      { key: 'name', label: 'Name', type: 'text', required: true, maxLength: 100 },
      { key: 'description', label: 'Description', type: 'text', maxLength: 200 },
      { key: 'iban', label: 'IBAN', type: 'text', required: true, pattern: '^[A-Z0-9]{15,34}$' },
      { key: 'balance', label: 'Balance', type: 'number', required: true, min: 0 },
      { key: 'active', label: 'Active', type: 'checkbox' },
      { key: 'bank_id', label: 'Bank ID', type: 'number', required: true },
      { key: 'user_id', label: 'User ID', type: 'number', required: true }
        ];
      case 'bank':
        return [
          { key: 'name', label: 'Bank Name', type: 'text', required: true },
          { key: 'country', label: 'Country', type: 'text' }
        ];
      case 'user':
        return [
          { key: 'name', label: 'Name', type: 'text', required: true },
          { key: 'email', label: 'Email', type: 'email', required: true }
        ];
      default:
        return [];
    }
  }
}
