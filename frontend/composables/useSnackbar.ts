import { useState } from '#imports';

interface SnackbarState {
  message: string;
  type: 'success' | 'error' | 'info';
  visible: boolean;
}

// Use a shared state for the timer to prevent race conditions
const timeoutId = useState<NodeJS.Timeout | null>('snackbar-timer', () => null);

export const useSnackbar = () => {
  const snackbar = useState<SnackbarState>('snackbar', () => ({
    message: '',
    type: 'info',
    visible: false,
  }));

  const showSnackbar = (options: { message: string, type?: 'success' | 'error' | 'info', timeout?: number } | string, typeArg?: 'success' | 'error' | 'info') => {
    let message = '';
    let type: 'success' | 'error' | 'info' = 'info';
    let timeout = 4000;

    if (typeof options === 'string') {
      message = options;
      if (typeArg) type = typeArg;
    } else {
      message = options.message;
      if (options.type) type = options.type;
      if (options.timeout) timeout = options.timeout;
    }

    if (timeoutId.value) {
      clearTimeout(timeoutId.value);
    }

    snackbar.value = { message, type, visible: true };

    timeoutId.value = setTimeout(() => {
      snackbar.value.visible = false;
    }, timeout);
  };

  const hideSnackbar = () => {
    if (timeoutId.value) {
      clearTimeout(timeoutId.value);
      timeoutId.value = null;
    }
    snackbar.value.visible = false;
  };

  return {
    snackbar,
    showSnackbar,
    hideSnackbar,
  };
};