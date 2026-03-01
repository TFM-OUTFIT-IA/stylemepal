import { inject } from '@angular/core';
import { Router, CanActivateFn } from '@angular/router';

export const authGuard: CanActivateFn = (route, state) => {
  const router = inject(Router);
  
  let token = null;

  if (typeof window !== 'undefined') {
    token = localStorage.getItem('token');
  }

  if (token) {
    return true;
  } else {
    router.navigate(['/login']);
    return false;
  }
};