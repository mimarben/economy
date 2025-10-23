import { Injectable } from '@angular/core';
import { HotToastService, ToastOptions } from '@ngxpert/hot-toast';
import { environment } from '../../environments/environment';
import { ApiResponse } from '../models/apiResponse';

@Injectable({ providedIn: 'root' })
export class ToastService {
  constructor(private toast: HotToastService) {}

  // Método principal para mostrar el toast, ahora acepta ApiResponse<T>
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

  // Transformar ApiResponse<T> a { response?: string; details?: string }
  private createToastMessage<T>(
    message: ApiResponse<T>,
    type: 'success' | 'error' | 'info' | 'warning'
  ): { response?: string; details?: string } {
    // Si response es un string (típico en errores), usarlo directamente
    if (typeof message.response === 'string') {
      return {
        details: message.details, // Ej: "ERROR_DNI_DUPLICATED"
        response: message.response, // Ej: "DNI already exists"
      };
    }

    // Si response es un objeto (típico en éxito), generar un string representativo
    if (typeof message.response === 'object' && message.response !== null) {
      const obj = message.response as any; // Usar any para acceder a propiedades dinámically
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
        // Fallback para objetos sin propiedades conocidas
        responseMessage = `Item updated successfully`;
      }

      return {
        details: message.details, // Ej: "USER_UPDATED"
        response: responseMessage,
      };
    }

    // Fallback para otros casos (response es null, undefined, etc.)
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
