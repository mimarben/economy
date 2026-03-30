/**
 * Category Rule Form Component
 * 
 * Reactive form for creating/editing categorization rules.
 * Validates regex patterns in real-time.
 */

import { Component, OnInit, Inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ReactiveFormsModule, FormBuilder, FormGroup, Validators, FormsModule } from '@angular/forms';
import { MAT_DIALOG_DATA, MatDialogRef } from '@angular/material/dialog';
import { MatSliderModule } from '@angular/material/slider';
import { MATERIAL_IMPORTS } from '@app/utils/material.imports';

import { CategoryRule } from '../../../services/category-rule/category-rule.service';
import { regexValidator } from '../../../utils/validators/regex.validator';

interface DialogData {
  mode: 'create' | 'edit';
  rule?: CategoryRule;
}

@Component({
  selector: 'app-category-rule-form',
  standalone: true,
  imports: [
    CommonModule,
    ReactiveFormsModule,
    FormsModule,
    ...MATERIAL_IMPORTS,
    MatSliderModule,
  ],
  templateUrl: './category-rule-form.component.html',
  styleUrls: ['./category-rule-form.component.scss'],
})
export class CategoryRuleFormComponent implements OnInit {
  form: FormGroup;
  mode: 'create' | 'edit';
  patternHint = '';
  testDescription = '';
  testResult: boolean | null = null;

  // Transaction types
  transactionTypes = [
    { value: 'expense', label: 'Expense' },
    { value: 'income', label: 'Income' },
    { value: 'investment', label: 'Investment' },
  ];

  constructor(
    private fb: FormBuilder,
    private dialogRef: MatDialogRef<CategoryRuleFormComponent>,
    @Inject(MAT_DIALOG_DATA) public data: DialogData
  ) {
    this.mode = data.mode;
    this.form = this.createForm();
  }

  ngOnInit(): void {
    if (this.mode === 'edit' && this.data.rule) {
      this.form.patchValue(this.data.rule);
    }
  }

  /**
   * Create the reactive form.
   */
  private createForm(): FormGroup {
    return this.fb.group({
      name: ['', [Validators.required, Validators.minLength(3)]],
      pattern: ['', [Validators.required, regexValidator()]],
      type: ['expense', [Validators.required]],
      category_id: [0, [Validators.required, Validators.min(1)]],
      priority: [100, [Validators.required, Validators.min(0)]],
      is_active: [true],
    });
  }

  /**
   * Get error message for a form field.
   */
  getErrorMessage(fieldName: string): string {
    const control = this.form.get(fieldName);

    if (!control || !control.errors || !control.touched) {
      return '';
    }

    if (control.hasError('required')) {
      return `${fieldName} is required.`;
    }

    if (control.hasError('minlength')) {
      const minLength = control.getError('minlength').requiredLength;
      return `${fieldName} must be at least ${minLength} characters.`;
    }

    if (control.hasError('invalidRegex')) {
      return `${fieldName} is not a valid regex pattern.`;
    }

    if (fieldName === 'category_id' && control.hasError('min')) {
      return 'Category ID must be a positive number.';
    }

    return 'Invalid input.';
  }

  /**
   * Test the regex pattern against a sample description.
   */
  testPattern(): void {
    if (!this.testDescription.trim()) {
      this.testResult = null;
      return;
    }

    const patternControl = this.form.get('pattern');
    if (!patternControl || patternControl.invalid) {
      this.testResult = null;
      return;
    }

    try {
      const regex = new RegExp(patternControl.value, 'i');
      this.testResult = regex.test(this.testDescription);
    } catch (e) {
      this.testResult = null;
    }
  }

  /**
   * Update pattern hint based on input.
   */
  onPatternChange(): void {
    const pattern = this.form.get('pattern');
    if (pattern && pattern.valid) {
      this.patternHint = `Pattern is valid: "${pattern.value}"`;
    } else if (pattern && pattern.invalid && pattern.touched) {
      this.patternHint = 'Invalid regex pattern';
    } else {
      this.patternHint = '';
    }
  }

  /**
   * Submit the form.
   */
  onSubmit(): void {
    if (this.form.valid) {
      this.dialogRef.close(this.form.value);
    }
  }

  /**
   * Cancel the dialog.
   */
  onCancel(): void {
    this.dialogRef.close();
  }
}
