import { Component, Input, Output, EventEmitter, OnChanges, SimpleChanges, OnDestroy, ChangeDetectorRef, ViewChildren, QueryList, AfterViewInit } from '@angular/core';
import { FormGroup, FormBuilder, Validators, ValidatorFn } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { MatSelectModule } from '@angular/material/select';
import { Subject } from 'rxjs';
import { takeUntil } from 'rxjs/operators';

import { MATERIAL_IMPORTS } from '@app/utils/material.imports';
import { FormFieldConfig } from './form-config';
import { UtilsService } from '@app/utils/utils.service';
import { TranslateModule } from '@ngx-translate/core';
@Component({
  selector: 'app-generic-form',
  templateUrl: './generic-form.component.html',
  styleUrl: './generic-form.component.css',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    ReactiveFormsModule,
    ...MATERIAL_IMPORTS,
    MatSelectModule,
    TranslateModule
  ]
})
export class GenericFormComponent implements OnChanges, AfterViewInit, OnDestroy {
  @Input() fields: FormFieldConfig[] = [];
  @Input() initialData: Record<string, any> = {};
  @Output() formSubmit = new EventEmitter<Record<string, any>>();
  @Output() formValidity = new EventEmitter<boolean>();
  @Output() formDirty = new EventEmitter<boolean>();
  @ViewChildren('columnKeyInput') columnKeyInputs!: QueryList<any>;
  
  form: FormGroup;
  columnsRows: Array<{ id: number; key: string; aliases: string }> = [];
  private columnRowIdCounter = 0;
  private destroy$ = new Subject<void>();
  private lastAddedRowId: number | null = null;
  private shouldFocusInput = false;

  constructor(private fb: FormBuilder, private utilsService: UtilsService, private cdr: ChangeDetectorRef) {
    this.form = this.fb.group({});
  }

  ngOnDestroy(): void {
    this.destroy$.next();
    this.destroy$.complete();
  }

  ngAfterViewInit(): void {
    // Suscribirse a cambios en los inputs de columnas para hacer focus cuando se añade una nueva fila
    if (this.columnKeyInputs) {
      this.columnKeyInputs.changes
        .pipe(takeUntil(this.destroy$))
        .subscribe(() => {
          if (this.shouldFocusInput) {
            this.focusOnColumnInput();
          }
        });
    }

    // Hacer focus inicial si es necesario
    if (this.shouldFocusInput) {
      this.focusOnColumnInput();
    }
  }

  private emitFormValidity(): void {
  this.form.statusChanges.subscribe(() => {
    this.formValidity.emit(this.form.valid);
    this.formDirty.emit(this.form.dirty)
    });
  }

  ngOnChanges(changes: SimpleChanges): void {
    if (changes['fields']?.currentValue !== changes['fields']?.previousValue ||
        changes['initialData']?.currentValue !== changes['initialData']?.previousValue) {
      this.buildForm();
    }
  }

  /**
   * Builds the form based on the provided fields and initial data.
   */
  private buildForm(): void {
    const controls: Record<string, any> = {};
    this.fields
      .filter(field => this.isValidField(field))
      .forEach(field => {
      if (field.key === 'id') {
        controls[field.key] = this.fb.control(
          { value: this.initialData['id'], disabled: true }
        );
      } else {
        controls[field.key] = this.createControl(field);
      }
      });

    this.form = this.fb.group(controls);

    this.fields.forEach((field) => {
      if (field.onChange && this.form.get(field.key)) {
        this.form.get(field.key)!.valueChanges.subscribe((value) => {
          field.onChange?.(value, this.form);
        });
      }
    });

    this.emitFormValidity();
    this.initColumnsRows();
  }

  /**
   * Validates a FormFieldConfig to ensure it has required properties.
   * @param field - The field configuration to validate.
   * @returns True if the field is valid, false otherwise.
   */
  private isValidField(field: FormFieldConfig): boolean {
    if (!field?.key || !field?.label || !field?.type) {
      console.warn(`Invalid field configuration: ${JSON.stringify(field)}`);
      return false;
    }
    if (field.type === 'select' && (!field.options || !Array.isArray(field.options))) {
      console.warn(`Select field ${field.key} requires valid options array`);
      return false;
    }
    return true;
  }

  /**
   * Creates a form control for a field with its validators and initial value.
   * @param field - The field configuration.
   * @returns The form control configuration.
   */
  private createControl(field: FormFieldConfig): any[] {
    const validators = this.getValidators(field);
    const initialValue = this.getInitialValue(field);
    return [initialValue, validators];
  }

  /**
   * Retrieves the initial value for a field.
   * @param field - The field configuration.
   * @returns The initial value for the field.
   */
  private getInitialValue(field: FormFieldConfig): any {
    const value = this.initialData[field.key] ?? null;

  if (field.type === 'date') {
      if (typeof value === 'string' && value) {
        return this.utilsService.formatDateShort(value);
      } else if (value instanceof Date) {
        return value; // Use Date as is
      }
      return null; // No valid date
    } else if (field.type === 'checkbox') {
      return value ?? false;
    } else if (field.type === 'select' && field.multiple) {
      if (Array.isArray(value)) {
        return value;
      }
      return value != null && value !== '' ? [value] : [];
    }
    return value ?? '';
  }

  /**
   * Builds the list of validators for a field based on its configuration.
   * @param field - The field configuration.
   * @returns An array of ValidatorFn.
   */
  private getValidators(field: FormFieldConfig): ValidatorFn[] {
    const validators: ValidatorFn[] = field.validators ? [...field.validators] : [];

    if (field.required) {
      validators.push(Validators.required);
    }

    if (field.type === 'text' || field.type === 'email') {
      if (field.minLength) validators.push(Validators.minLength(field.minLength));
      if (field.maxLength) validators.push(Validators.maxLength(field.maxLength));
      if (field.pattern) validators.push(Validators.pattern(field.pattern));
      if (field.type === 'email') validators.push(Validators.email);
    } else if (field.type === 'number') {
      if (field.min !== undefined) validators.push(Validators.min(field.min));
      if (field.max !== undefined) validators.push(Validators.max(field.max));
    }

    return validators;
  }

  /**
   * Handles form submission, emitting valid data or marking fields as touched.
   */
  submitForm(): void {
    // Sincronizar columnas antes de enviar
    this.syncColumnsControlFromRows();
    
    if (this.form.valid) {
      this.formSubmit.emit(this.form.value);
    } else {
      this.form.markAllAsTouched();
    }
    this.emitFormValidity();
  }

  /**
   * Generates an error message for a field based on its validation state.
   * @param field - The field configuration.
   * @returns The error message or an empty string.
   */
  getErrorMessage(field: FormFieldConfig): string {
    const control = this.form.get(field.key);
    if (!control || !control.errors || !control.touched) return '';

    const errors = control.errors;
    if (errors['required']) return `${field.label} is required`;
    if (errors['email']) return 'Invalid email format';
    if (errors['minlength']) return `Minimum length is ${field.minLength}`;
    if (errors['maxlength']) return `Maximum length is ${field.maxLength}`;
    if (errors['pattern']) return 'Invalid format';
    if (errors['min']) return `Minimum value is ${field.min}`;
    if (errors['max']) return `Maximum value is ${field.max}`;

    return 'Invalid input';
  }

  /**
   * Returns the list of fields with their applied validators for debugging or external use.
   * @returns An array of field configurations with validator details.
   */
  getFieldsAndValidators(): Array<{ key: string; label: string; type: string; required?: boolean; validators: string[] }> {
    return this.fields.map(field => ({
      key: field.key,
      label: field.label,
      type: field.type,
      required: field.required,
      validators: [
        ...(field.required ? ['required'] : []),
        ...(field.type === 'email' ? ['email'] : []),
        ...(field.minLength ? [`minLength(${field.minLength})`] : []),
        ...(field.maxLength ? [`maxLength(${field.maxLength})`] : []),
        ...(field.pattern ? [`pattern(${field.pattern})`] : []),
        ...(field.min !== undefined ? [`min(${field.min})`] : []),
        ...(field.max !== undefined ? [`max(${field.max})`] : []),
        ...(field.validators ? field.validators.map(v => v.name || 'custom') : [])
      ]
    }));
  }

  isColumnsField(field: FormFieldConfig): boolean {
    return field.key === 'columns';
  }

  trackByColumnRowIndex(_index: number, row: { id: number }): number {
    return row.id;
  }

  addColumnsMappingLine(): void {
    const newId = this.columnRowIdCounter++;
    this.columnsRows = [...this.columnsRows, { id: newId, key: '', aliases: '' }];
    this.lastAddedRowId = newId;
    this.shouldFocusInput = true;
    
    // Sincronizar y marcar como dirty
    this.syncColumnsControlFromRows();
    const columnsControl = this.form.get('columns');
    if (columnsControl) {
      columnsControl.markAsDirty();
      columnsControl.markAsTouched();
      // Emitir cambios de estado
      this.formValidity.emit(this.form.valid);
      this.formDirty.emit(this.form.dirty);
    }
    
    this.cdr.markForCheck();
  }

  private focusOnColumnInput(): void {
    if (this.lastAddedRowId === null || !this.columnKeyInputs) {
      return;
    }

    // Buscar el input que coincida con el lastAddedRowId
    const lastRowIndex = this.columnsRows.findIndex(row => row.id === this.lastAddedRowId);
    if (lastRowIndex === -1) {
      this.shouldFocusInput = false;
      return;
    }

    // Obtener el input de clave en la posición correspondiente
    const inputs = this.columnKeyInputs.toArray();
    const nativeElement = inputs[lastRowIndex]?.nativeElement;
    
    if (nativeElement) {
      nativeElement.focus();
      nativeElement.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }
    
    this.shouldFocusInput = false;
  }

  removeColumnsMappingLine(index: number): void {
    this.columnsRows = this.columnsRows.filter((_, i) => i !== index);
    
    // Sincronizar y marcar como dirty
    this.syncColumnsControlFromRows();
    const columnsControl = this.form.get('columns');
    if (columnsControl) {
      columnsControl.markAsDirty();
      columnsControl.markAsTouched();
      // Emitir cambios de estado
      this.formValidity.emit(this.form.valid);
      this.formDirty.emit(this.form.dirty);
    }
  }

  onColumnsRowChange(): void {
    // Sincronizar columnas cuando hay cambios en los inputs
    this.syncColumnsControlFromRows();
    const columnsControl = this.form.get('columns');
    if (columnsControl) {
      columnsControl.markAsDirty();
      columnsControl.markAsTouched();
      // Emitir cambios de estado
      this.formValidity.emit(this.form.valid);
      this.formDirty.emit(this.form.dirty);
    }
  }

  private initColumnsRows(): void {
    const control = this.form.get('columns');
    if (!control) return;

    const parsed = this.parseColumnsValue(control.value);
    const entries = Object.entries(parsed);
    this.columnsRows = entries.length
      ? entries.map(([key, aliases]) => ({
          id: this.columnRowIdCounter++,
          key,
          aliases: aliases.join(', '),
        }))
      : [{ id: this.columnRowIdCounter++, key: '', aliases: '' }];
    this.syncColumnsControlFromRows();
  }

  private syncColumnsControlFromRows(): void {
    const control = this.form.get('columns');
    if (!control) return;

    const normalized = Object.fromEntries(
      this.columnsRows
        .map((row) => ({
          key: row.key.trim(),
          aliases: row.aliases
            .split(',')
            .map((item) => item.trim())
            .filter(Boolean),
        }))
        .filter((row) => row.key.length > 0)
        .map((row) => [row.key, row.aliases]),
    );

    control.setValue(normalized, { emitEvent: false });
  }

  private parseColumnsValue(value: unknown): Record<string, string[]> {
    if (!value) return {};

    if (typeof value === 'string') {
      try {
        const parsed = JSON.parse(value);
        return this.parseColumnsValue(parsed);
      } catch {
        return {};
      }
    }

    if (typeof value === 'object' && !Array.isArray(value)) {
      return Object.fromEntries(
        Object.entries(value as Record<string, unknown>).map(([key, aliases]) => [
          key,
          Array.isArray(aliases) ? aliases.map((item) => String(item)) : [],
        ]),
      );
    }

    return {};
  }
}
