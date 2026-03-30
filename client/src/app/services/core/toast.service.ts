import { Injectable } from '@angular/core';
import { HotToastService, ToastOptions } from '@ngxpert/hot-toast';
import { environment } from '@env/environment';
import { ApiResponse } from '@core_models/apiResponse';

@Injectable({ providedIn: 'root' })
export class ToastService {
  constructor(private toast: HotToastService) {}

  showToast<T>(
    message: ApiResponse<T>,
    type: 'success' | 'error' | 'info' | 'warning' = 'info',
    options?: ToastOptions<string>
  ) {
    // Transformar ApiResponse<T> al formato esperado por formatMessage
    const toastMessage = this.createToastMessage(message, type);
    // Formatear el mensaje como string
    const formattedMessage = this.formatMessage(toastMessage, type);
    const className = this.getClassName(type);

    const baseOptions: ToastOptions<string> = {
      duration: 4000,
      dismissible: true,
      className,
      ...options,
    };

    switch (type) {
      case environment.toastType.Success:
        this.toast.success(formattedMessage, baseOptions);
        break;
      case environment.toastType.Error:
        this.toast.error(formattedMessage, baseOptions);
        break;
      case environment.toastType.Warning:
        this.toast.warning(formattedMessage, baseOptions);
        break;
      case environment.toastType.Info:
      default:
        this.toast.info(formattedMessage, baseOptions);
        break;
    }
  }

  /**
   * Convenience method to show error toast with a simple string message
   */
  error(message: string, options?: ToastOptions<string>): void {
    const className = this.getClassName('error');
    const baseOptions: ToastOptions<string> = {
      duration: 4000,
      dismissible: true,
      className,
      ...options,
    };
    this.toast.error(message, baseOptions);
  }

  /**
   * Convenience method to show success toast with a simple string message
   */
  success(message: string, options?: ToastOptions<string>): void {
    const className = this.getClassName('success');
    const baseOptions: ToastOptions<string> = {
      duration: 4000,
      dismissible: true,
      className,
      ...options,
    };
    this.toast.success(message, baseOptions);
  }

  /**
   * Convenience method to show info toast with a simple string message
   */
  info(message: string, options?: ToastOptions<string>): void {
    const className = this.getClassName('info');
    const baseOptions: ToastOptions<string> = {
      duration: 4000,
      dismissible: true,
      className,
      ...options,
    };
    this.toast.info(message, baseOptions);
  }

  /**
   * Convenience method to show warning toast with a simple string message
   */
  warning(message: string, options?: ToastOptions<string>): void {
    const className = this.getClassName('warning');
    const baseOptions: ToastOptions<string> = {
      duration: 4000,
      dismissible: true,
      className,
      ...options,
    };
    this.toast.warning(message, baseOptions);
  }

  // Transformar ApiResponse<T> a { response?: string; details?: string }
  private createToastMessage<T>(
    message: ApiResponse<T>,
    type: 'success' | 'error' | 'info' | 'warning'
  ): { response?: string; details?: string } {
    if (typeof message.response === 'string') {
      return {
        details: message.details, // Ej: "ERROR_DNI_DUPLICATED"
        response: message.response, // Ej: "DNI already exists"
      };
    }

    if (typeof message.response === 'object' && message.response !== null) {
      const obj = message.response as any;
      let responseMessage = 'Operation completed successfully';

      // Intentar extraer una propiedad representativa
      if (obj.name) {
        responseMessage = `${obj.name} updated successfully`;
      } else if (obj.id) {
        responseMessage = `Item with ID ${obj.id} updated successfully`;
      } else if (obj.title) {
        responseMessage = `${obj.title} updated successfully`;
      } else if (obj.email) {
        responseMessage = `Item with email ${obj.email} updated successfully`;
      } else {
        responseMessage = `Item updated successfully`;
      }

      return {
        details: message.details, // Ej: "USER_UPDATED"
        response: responseMessage,
      };
    }

    return {
      details: message.details || 'UNKNOWN',
      response: 'Operation completed',
    };
  }

  // Obtener el nombre de la clase CSS
  private getClassName(type: string): string {
    switch (type) {
      case environment.toastType.Success:
        return 'toast-success';
      case environment.toastType.Error:
        return 'toast-error';
      case environment.toastType.Warning:
        return 'toast-warning';
      case environment.toastType.Info:
        return 'toast-info';
      default:
        return 'toast-info';
    }
  }

  // Formatear el mensaje, siempre devuelve string
  private formatMessage(
    message: string | { response?: string; details?: string },
    type: 'success' | 'error' | 'info' | 'warning' = 'info'
  ): string {
    console.log('Formatting message:', type + ' of type ' + typeof type);
    console.log('Message:', message + ' of type ' + typeof message);
    if (typeof message === 'string') {
      return message;
    } else if (typeof message === 'object') {
      const lines = [];
      if (type === 'success') {
        console.log('Success message:', message.response);
        if (message.response) lines.push(`<strong>${message.response}</strong>`);
        if (message.details) lines.push(`${message.details}`);
      } else if (type === 'error') {
        if (message.response) lines.push(`<strong>Error:</strong> ${message.response}`);
        if (message.details) lines.push(`Details: ${message.details}`);
      }
      return lines.join('<br>');
    }
    return '';
  }
}
