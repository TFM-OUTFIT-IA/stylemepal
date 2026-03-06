import { inject } from '@angular/core';
import { CanActivateFn, Router } from '@angular/router';

export const noAuthGuard: CanActivateFn = (route, state) => {
  const router = inject(Router);
  

  const token = localStorage.getItem('token'); 

  if (token) {
    router.navigate(['/dashboard/landing']);
    return false;
  }

  return true;
};