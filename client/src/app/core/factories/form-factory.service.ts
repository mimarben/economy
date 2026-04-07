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
  /**
   * Campos técnicos que normalmente ya llegan en meta pero
   * no queremos renderizar en formularios/tablas CRUD.
   */
  private readonly metaHiddenFieldKeys = [
    'id',
    'created_at',
    'updated_at',
    'deleted_at',
    'dedup_hash',
  ];

  private readonly formConfigMap: Record<ModelType, FormFieldConfig[]> = {
    // Todos los formularios se alimentan desde endpoint meta.
    account: [],
    bank: [],
    houseHold: [],
    houseHoldMember: [],
    source: [],
    card: [],
    saving_log: [],
    saving: [],
    investment: [],
    investment_category: [],
    investment_log: [],
    income: [],
    income_category: [],
    expense: [],
    expense_category: [],

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

  private isMetaFieldVisible(field: FormFieldConfig): boolean {
    return !this.metaHiddenFieldKeys.includes(field.key);
  }

  getTableColumnsFromMetadata<T>(fields: FormFieldConfig[]): TableColumn<T>[] {
    return fields
      .filter((field) => this.isMetaFieldVisible(field))
      .map((field) => ({
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
    return fields
    .filter((field) => this.isMetaFieldVisible(field))
    .map((field) => {
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
