// 1. Añadimos ChangeDetectorRef aquí
import { Component, OnInit, ChangeDetectorRef } from '@angular/core'; 
import { FormBuilder, FormGroup, Validators, ReactiveFormsModule } from '@angular/forms';
import { Router, RouterModule } from '@angular/router';
import { AuthService } from '../../services/auth.service';

@Component({
  selector: 'app-login',
  standalone: true,
  imports: [ReactiveFormsModule, RouterModule],
  templateUrl: './login.component.html',
  styleUrls: ['./login.component.css']
})
export class LoginComponent implements OnInit {
  loginForm!: FormGroup;
  errorMessage: string = '';
  isLoading: boolean = false;

  constructor(
    private fb: FormBuilder,
    private authService: AuthService,
    private router: Router,
    // 2. Lo inyectamos en el constructor
    private cdr: ChangeDetectorRef 
  ) {}

  ngOnInit(): void {
    this.loginForm = this.fb.group({
      username: ['', [Validators.required, Validators.minLength(3)]],
      password: ['', [Validators.required]] 
    });
  }

  onSubmit(): void {
    if (this.loginForm.invalid) {
      this.loginForm.markAllAsTouched();
      return; 
    }

    this.isLoading = true;
    this.errorMessage = '';

    this.authService.login(this.loginForm.value).subscribe({
      next: (response) => {
        this.isLoading = false;
        this.router.navigate(['/dashboard']); 
      },
      error: (err) => {
        this.isLoading = false;
        console.error("Error en login:", err); 

        if (err.status === 401) {
          this.errorMessage = 'Usuario o contraseña incorrectos';
        } else if (err.status === 422) {
          this.errorMessage = 'Error de formato. (Posible fallo de FormData)';
        } else {
          this.errorMessage = 'Error de conexión con el servidor';
        }

        // 3. ¡LA MAGIA! Obligamos a Angular a actualizar el HTML
        this.cdr.detectChanges();
      }
    });
  }
}