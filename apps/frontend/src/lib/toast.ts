import { toast as _toast } from 'vue-sonner';

export const toast = {
  success: (message: string, opts?: object) =>
    _toast.success(message, {
      ...opts,
    }),

  error: (message: string, opts?: object) =>
    _toast.error(message, {
      ...opts,
    }),

  warning: (message: string, opts?: object) =>
    _toast.warning(message, {
      ...opts,
    }),

  info: (message: string, opts?: object) =>
    _toast.info(message, {
      ...opts,
    }),
};
