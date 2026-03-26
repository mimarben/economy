/**
 * Custom validators for forms.
 */

import { AbstractControl, ValidationErrors, ValidatorFn } from '@angular/forms';

/**
 * Validator for regex patterns.
 * Checks that the input is a valid regex pattern.
 */
export function regexValidator(): ValidatorFn {
  return (control: AbstractControl): ValidationErrors | null => {
    if (!control.value || control.value === '') {
      return null; // Don't validate empty values
    }

    try {
      new RegExp(control.value);
      return null; // Valid regex
    } catch (e) {
      return { invalidRegex: { value: control.value, error: (e as Error).message } };
    }
  };
}
