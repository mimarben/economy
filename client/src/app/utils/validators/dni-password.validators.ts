/**
 * Shared DNI / password validators.
 *
 * Extracted (verbatim logic) from the user-form-dialog so the public register
 * form can reuse them. The dialog still keeps its own local copies for now;
 * pointing it at these shared functions is a trivial follow-up dedup.
 */
import { AbstractControl, ValidationErrors, ValidatorFn } from '@angular/forms';

/**
 * Validates a Spanish DNI: 8 digits + a check letter (input letter is
 * case-insensitive). Returns null for empty values so it composes with
 * `Validators.required`.
 */
export function dniValidator(): ValidatorFn {
  return (control: AbstractControl): ValidationErrors | null => {
    const value: string = control.value;
    if (!value) {
      return null;
    }

    const dniRegex = /^[0-9]{8}[A-Za-z]$/;
    if (!dniRegex.test(value)) {
      return { invalidDNI: true };
    }

    const dniLetters = 'TRWAGMYFPDXBNJZSQVHLCKE';
    const numbers = value.slice(0, 8);
    const letter = value.slice(-1).toUpperCase();
    const expectedLetter = dniLetters[parseInt(numbers, 10) % 23];

    return letter === expectedLetter ? null : { invalidDNI: true };
  };
}

/**
 * Validates password complexity (uppercase, lowercase, digit, symbol, 8+ chars).
 * Only runs when the field has a value of 8+ characters; the length floor is
 * enforced separately via `Validators.minLength(8)`.
 */
export function passwordComplexityValidator(): ValidatorFn {
  return (control: AbstractControl): ValidationErrors | null => {
    const value: string = control.value;
    if (!value || value.length < 8) {
      return null;
    }
    const passwordRegex =
      /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*¿?&_!¡€#|/(){}-])[A-Za-z\d@$!%*?&]{8,}$/;
    return passwordRegex.test(value) ? null : { strongPassword: true };
  };
}
