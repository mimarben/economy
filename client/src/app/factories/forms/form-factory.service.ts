// form-factory.service.ts
import { Injectable } from '@angular/core';
import { FormFieldConfig } from '../../components/shared/generic-form/form-config';
import { TableColumn } from '../../components/shared/generic-table/generic-table.component';

type ModelType = 'account' | 'bank' | 'user' | "houseHold";

@Injectable({ providedIn: 'root' })
export class FormFactoryService {
  private readonly formConfigMap: Record<ModelType, FormFieldConfig[]> = {
    account: [
      { key: 'id', label: 'Id', type: 'number' },
      { key: 'name', label: 'Name', type: 'text', required: true, maxLength: 100, minLength: 2 },
      { key: 'description', label: 'Description', type: 'text', maxLength: 200, minLength: 2 },
      { key: 'iban', label: 'IBAN', type: 'text', required: true, pattern: '^[A-Z0-9]{15,34}$', minLength: 24, maxLength: 24 },
      { key: 'balance', label: 'Balance', type: 'number', required: true, min: 0 },
      { key: 'active', label: 'Active', type: 'checkbox' },
      { key: 'bank_id', label: 'Bank ID', type: 'select', required: true },
      { key: 'user_id', label: 'User ID', type: 'select', required: true }
    ],
    bank: [
      { key: 'id', label: 'Id', type: 'number' },
      { key: 'name', label: 'Bank Name', type: 'text', required: true },
      { key: 'description', label: 'Description', type: 'text' },
      { key: 'active', label: 'Active', type: 'checkbox' },
    ],
    user: [
      { key: 'name', label: 'Name', type: 'text', required: true },
      { key: 'email', label: 'Email', type: 'email', required: true }
    ],
    houseHold: [
      { key: 'id', label: 'Id', type: 'number' },
      { key: 'name', label: 'HouseHold Name', type: 'text', required: true },
      { key: 'address', label: 'Address', type: 'text', required: true },
      { key: 'description', label: 'Description', type: 'text' },
      { key: 'active', label: 'Active', type: 'checkbox' },
    ]
  };

  // Generate table columns based on existing form config
  getTableColumns<T>(modelType: ModelType): TableColumn<T>[] {
    const formFields = this.getFormConfig(modelType);
    return formFields
      .filter(field => this.shouldIncludeInTable(field, modelType))
      .map(field => {
        return {
          key: field.key,
          label: field.label,
          sortable: this.isSortable(field.key, modelType),
          formatter: this.getFormatter(field.key, field.type, modelType)
        } as TableColumn<T>;
      });
  }

  private shouldIncludeInTable(field: FormFieldConfig, modelType: ModelType): boolean {
    // Define fields to exclude from tables (if any)
    const excludedFields: Record<ModelType, string[]> = {
      account: ['bank_id', 'user_id'], // You might want to show referenced entity names instead
      bank: [],
      user: [],
      houseHold: []
    };

    return !excludedFields[modelType].includes(field.key);
  }

  private isSortable(key: string, modelType: ModelType): boolean {
    // Define non-sortable fields (if any)
    const nonSortableFields: Record<ModelType, string[]> = {
      account: ['description'],
      bank: ['description'],
      user: [],
      houseHold: ['description']
    };

    return !nonSortableFields[modelType].includes(key);
  }
  private getFormatter(key: string, type: string, modelType: ModelType): ((value: any) => string) | undefined {
    // Define custom formatters for specific fields
    if (type === 'checkbox') {
      return (value: boolean) => value ? 'Yes' : 'No';
    }
    // Add more custom formatters as needed for different field types
    if (key === 'balance' && modelType === 'account') {
      return (value: number) => `$${value.toFixed(2)}`;
    }
    return undefined;
  }

  getFormConfig(modelType: ModelType): FormFieldConfig[] {
    return this.formConfigMap[modelType] ?? [];
  }
}
