// form-factory.service.ts
import { Injectable } from '@angular/core';
import { FormFieldConfig } from '../../components/shared/generic-form/form-config';

@Injectable({ providedIn: 'root' })
export class FormFactoryService {
  getFormConfig(modelType: 'account' | 'bank' | 'user'): FormFieldConfig[] {
    switch (modelType) {
      case 'account':
        return [
          { key: 'name', label: 'Name', type: 'text', required: true },
          { key: 'iban', label: 'IBAN', type: 'text', required: true },
          { key: 'balance', label: 'Balance', type: 'number' },
          { key: 'active', label: 'Active', type: 'checkbox' }
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
