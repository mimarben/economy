import { Injectable } from '@angular/core';
import { FormFieldConfig } from '@shared/generic-form/form-config';
import { TableColumn } from '@shared/generic-table/generic-table.component';
import { RoleEnum } from '@core/const/Role.enum';
import { CurrencyEnum } from '@core/const/Currency.enum';
import { ActionEnum } from '@core/const/Action.enum';
import { SourceEnum } from '@core/const/Source.enum';
type ModelType = 'account' | 'bank' | 'card' | "houseHold" | 'houseHoldMember' | 'saving_log' | "source" | "saving" | 'investment' | 'investment_category' | 'investment_log' |'income' |'income_category' | 'expense' | 'expense_category';

@Injectable({ providedIn: 'root' })
export class FormFactoryService {
  private readonly formConfigMap: Record<ModelType, FormFieldConfig[]> = {
    account: [
      { key: 'id', label: 'Id', type: 'number' },
      { key: 'name', label: 'Name', type: 'text', required: true, maxLength: 100, minLength: 2 },
      { key: 'description', label: 'Description', type: 'text', maxLength: 200, minLength: 2 },
      { key: 'iban', label: 'IBAN', type: 'text', required: true, pattern: '^[A-Z0-9]{15,34}$', minLength: 24, maxLength: 24 },
      { key: 'balance', label: 'Balance', type: 'number', required: true, min: 0 },
      { key: 'currency', label: 'Currency', type: 'select', required: true, options: this.getCurrencyOptions() },
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
    houseHold: [
      { key: 'id', label: 'Id', type: 'number' },
      { key: 'name', label: 'HouseHold Name', type: 'text', required: true },
      { key: 'address', label: 'Address', type: 'text', required: true },
      { key: 'description', label: 'Description', type: 'text' },
      { key: 'active', label: 'Active', type: 'checkbox' },
    ],
    houseHoldMember: [
      { key: 'id', label: 'Id', type: 'number' },
      { key: 'role', label: 'Role', type: 'select', required: true, options: this.getRoleOptions() },
      { key: 'household_id', label: 'HouseHold', type: 'select', required: true },
      { key: 'user_id', label: 'User', type: 'select',required: true},
      { key: 'active', label: 'Active', type: 'checkbox' },
    ],
    source: [],
   //source:[
   //  { key: 'id', label: 'Id', type: 'number' },
   //  { key: 'name', label: 'Source Name', type: 'text', required: true },
   //  { key: 'description', label: 'Description', type: 'text' },
   //  { key: 'type', label: 'Type', type: 'select', required: true, options: this.getSourceOptions() },
   //  { key: 'active', label: 'Active', type: 'checkbox' }
   //],
   card: [],
    saving_log:[
      { key: 'id', label: 'Id', type: 'number' },
      { key: 'date', label: 'Date', type: 'date', required: true},
      { key: 'amount', label: 'Amount', type: 'number', required: true, min: 0 },
      { key: 'total_amount', label: 'TotalAmount', type: 'number', required: true, min: 0 },
      { key: 'note', label: 'Note', type: 'text' },
      { key: 'saving_id', label: 'Saving-Id', type: 'select',required: true},
      { key: 'source_id', label: 'Soruce-Id', type: 'select',required: true},
    ],
    saving:[
      { key: 'id', label: 'Id', type: 'number' },
      { key: 'description', label: 'Description', type: 'text' },
      { key: 'amount', label: 'Goal Amount', type: 'number', required: true, min: 0 },
      { key: 'date', label: 'Date', type: 'date', required: true},
      { key: 'currency', label: 'Currency', type: 'select', required: true, options: this.getCurrencyOptions() },
      { key: 'user_id', label: 'User', type: 'select',required: true},
      { key: 'account_id', label: 'Account-Id', type: 'select',required: true}
    ],
    investment:[
      { key: 'id', label: 'Id', type: 'number' },
      { key: 'name', label: 'Name', type: 'text', required: true },
      { key: 'date', label: 'Date', type: 'date', required: true},
      { key: 'currency', label: 'Currency', type: 'select', required: true, options: this.getCurrencyOptions() },
      { key: 'user_id', label: 'User', type: 'select',required: true},
      { key: 'account_id', label: 'Account', type: 'select',required: true},
      { key: 'category_id', label: 'Category Investment', type: 'select',required: true}
    ],
    investment_category:[
      { key: 'id', label: 'Id', type: 'number' },
      { key: 'name', label: 'Name', type: 'text', required: true },
      { key: 'description', label: 'Description', type: 'text' },
      { key: 'active', label: 'Active', type: 'checkbox' },
    ],
    investment_log:[
      { key: 'id', label: 'Id', type: 'number' },
      { key: 'date', label: 'Date', type: 'date', required: true},
      { key: 'currentValue', label: 'Current Value', type: 'number', required: true, min: 0 },
      { key: 'pricePerUnit', label: 'Price per Unit', type: 'number', required: true, min: 0 },
      { key: 'unitsBought', label: 'Units bought', type: 'number', required: true, min: 0 },
      { key: 'action', label: 'Action', type: 'select', required: true, options: this.getActionsOptions() },
      { key: 'note', label: 'Note', type: 'text' },
      { key: 'investment_id', label: 'Investment ID', type: 'select',required: true},
    ],
    income:[
      { key: 'id', label: 'Id', type: 'number' },
      { key: 'name', label: 'Name', type: 'text' },
      { key: 'description', label: 'Description', type: 'text' },
      { key: 'amount', label: 'Amount', type: 'number', required: true, min: 0 },
      { key: 'date', label: 'Date', type: 'date', required: true},
      { key: 'user_id', label: 'User', type: 'select',required: true},
      { key: 'currency', label: 'Currency', type: 'select', required: true, options: this.getCurrencyOptions() },
      { key: 'source_id', label: 'Source', type: 'select', required: true },
      { key: 'category_id', label: 'Income Category', type: 'select', required: true },
      { key: 'account_id', label: 'Account', type: 'select',required: true}
    ],
    income_category:[
      { key: 'id', label: 'Id', type: 'number' },
      { key: 'name', label: 'Name', type: 'text', required: true },
      { key: 'description', label: 'Description', type: 'text' },
      { key: 'active', label: 'Active', type: 'checkbox' },
    ],
    expense:[
      { key: 'id', label: 'Id', type: 'number' },
      { key: 'name', label: 'Name', type: 'text' },
      { key: 'description', label: 'Description', type: 'text' },
      { key: 'amount', label: 'Amount', type: 'number', required: true, min: 0 },
      { key: 'date', label: 'Date', type: 'date', required: true},
      { key: 'currency', label: 'Currency', type: 'select', required: true, options: this.getCurrencyOptions() },
      { key: 'user_id', label: 'User', type: 'select',required: true},
      { key: 'category_id', label: 'Expense Category', type: 'select', required: true },
      { key: 'source_id', label: 'Source', type: 'select', required: true },
      { key: 'account_id', label: 'Account', type: 'select',required: true}
    ],
    expense_category:[
      { key: 'id', label: 'Id', type: 'number' },
      { key: 'name', label: 'Name', type: 'text', required: true },
      { key: 'description', label: 'Description', type: 'text' },
      { key: 'active', label: 'Active', type: 'checkbox' },
    ],

  };

  // Generate table columns based on existing form config
  getTableColumns<T>(modelType: ModelType, externalFormatters?: Record<string, (value: any) => string>): TableColumn<T>[] {
    const formFields = this.getFormConfig(modelType);
    return formFields
      .filter(field => this.shouldIncludeInTable(field, modelType))
      .map(field => {
        return {
          key: field.key,
          label: field.label,
          sortable: this.isSortable(field.key, modelType),
          formatter:
            externalFormatters?.[field.key] ??
            this.getFormatter(field.key, field.type, field.options)
        } as TableColumn<T>;
      });
  }

  private shouldIncludeInTable(field: FormFieldConfig, modelType: ModelType): boolean {
    // Define fields to exclude from tables (if any)
    const excludedFields: Record<ModelType, string[]> = {
      account: ['bank_id', 'user_id'], // You might want to show referenced entity names instead
      bank: [],
      houseHold: [],
      houseHoldMember: [],
      source:[],
      saving_log: [],
      saving:[],
      investment:[],
      investment_category:[],
      investment_log:[],
      income_category:[],
      income:[],
      expense:[],
      expense_category:[],
      card: []
    };

    return !excludedFields[modelType].includes(field.key);
  }

  private isSortable(key: string, modelType: ModelType): boolean {
    // Define non-sortable fields (if any)
    const nonSortableFields: Record<ModelType, string[]> = {
      account: ['description'],
      bank: ['description'],
      houseHold: ['description'],
      houseHoldMember: [],
      source:[],
      saving_log: [],
      saving:[],
      investment:[],
      investment_category:[],
      investment_log:[],
      income_category:[],
      income:[],
      expense:[],
      expense_category:[],
      card: []
    };

    return !nonSortableFields[modelType].includes(key);
  }
private getFormatter(
  key: string,
  type: string,
  options?: { value: any; label: string }[]
): ((value: any) => string) | undefined {
  
  if (type === 'checkbox') {
    return (value: boolean) => value ? 'Yes' : 'No';
  }

  if (type === 'number') {
    return (value: number) => value?.toString();
  }

  if (type === 'select' && options) {
    return (value: any) => {
      const match = options.find(o => o.value === value);
      return match ? match.label : value;
    };
  }

  return undefined;
}

  getFormConfig(modelType: ModelType): FormFieldConfig[] {
    return this.formConfigMap[modelType] ?? [];
  }

   // Method to generate Role options
  getRoleOptions() {
    const roles: RoleEnum[] = [
    RoleEnum.HUSBAND,
    RoleEnum.WIFE,
    RoleEnum.CHILD,
    RoleEnum.OTHER
  ];
    return roles.map(role => ({
      value: role,
      label: role.charAt(0).toUpperCase() + role.slice(1),  // Capitalizing first letter for display
    }));
  }
  getCurrencyOptions(){
    const currencies: CurrencyEnum[] = [
      CurrencyEnum.EUR,
      CurrencyEnum.USD,
      CurrencyEnum.JPY,
      CurrencyEnum.BTC,
      CurrencyEnum.ETH,
      CurrencyEnum.USDC,
      CurrencyEnum.DOGE,
      CurrencyEnum.LTC,
      CurrencyEnum.XRP,
      CurrencyEnum.XLM,
      CurrencyEnum.ADA,
      CurrencyEnum.DOT,
      CurrencyEnum.SOL,
      CurrencyEnum.SHIB,
      CurrencyEnum.TRX
    ];
    return currencies.map(currencies => ({
      value: currencies,
      label: currencies.charAt(0).toUpperCase() + currencies.slice(1),  // Capitalizing first letter for display
    }));
  }

  getActionsOptions(){
    const actions: ActionEnum[] = [
      ActionEnum.BUY,
      ActionEnum.SELL,
      ActionEnum.TRANSFER,
      ActionEnum.DEPOSIT,
      ActionEnum.WITHDRAW,
      ActionEnum.HOLD
    ];
    return actions.map(actions => ({
      value: actions,
      label: actions.charAt(0).toUpperCase() + actions.slice(1),
    }));
  }
  getSourceOptions(){
    const sources: SourceEnum[] = [
      SourceEnum.INCOME,
      SourceEnum.SAVING,
      SourceEnum.INVESTMENT,
      SourceEnum.EXPENSE,
      SourceEnum.OTHER
    ];
    return sources.map(sources => ({
      value: sources,
      label: sources.charAt(0).toUpperCase() + sources.slice(1),
    }));
  }

  getTableColumnsFromMetadata<T>(fields: FormFieldConfig[]): TableColumn<T>[] {
  return fields.map(field => ({
    key: field.key,
    label: field.label,
    sortable: true,
    formatter: this.getFormatter(field.key, field.type, field.options)
  }));
}

  enrichMetadataFields(
    fields: FormFieldConfig[],
    relationOptions: Record<string, { value: string | number; label: string }[]> = {},
  ): FormFieldConfig[] {
    return fields.map((field) => {
      const relationKey = field.relation ?? field.key;
      const options = relationOptions[relationKey];
      const isRelationSelect =
        field.ui_type === 'select' || !!field.relation || field.key.endsWith('_id');

      if (!isRelationSelect || !options) {
        return field;
      }

      return {
        ...field,
        type: 'select',
        options,
      };
    });
  }
}
