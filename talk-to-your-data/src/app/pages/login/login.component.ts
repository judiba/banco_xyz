import { CommonModule } from '@angular/common';
import { Component, OnInit, inject, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { ActivatedRoute, Router } from '@angular/router';
import { environment } from '../../../environments/environment';
import { AuthService } from '../../core/auth/auth.service';
import { buildSamlLoginUrl } from '../../core/auth/saml-auth.util';
import { SessionInitService } from '../../core/session/session-init.service';
import { getApiErrorMessage, getApiErrorCode } from '../../core/api/api-error.util';

@Component({
  selector: 'app-login',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './login.component.html',
  styleUrl: './login.component.scss',
})
export class LoginComponent implements OnInit {
  private readonly router = inject(Router);
  private readonly route = inject(ActivatedRoute);
  private readonly auth = inject(AuthService);
  private readonly sessionInit = inject(SessionInitService);

  readonly authSamlEnabled = environment.authSamlEnabled;

  username = '';
  password = '';

  readonly isSubmitting = signal(false);
  readonly loginError = signal<string | null>(null);

  ngOnInit(): void {
    const token = this.route.snapshot.queryParamMap.get('token');
    const refresh = this.route.snapshot.queryParamMap.get('refresh');

    if (token) {
      this.completeSsoLogin(token, refresh);
    }
  }

  clearError(): void {
    this.loginError.set(null);
  }

  isFormValid(): boolean {
    return this.username.trim().length > 0 && this.password.trim().length > 0;
  }

  loginWithMicrosoft(): void {
    if (this.isSubmitting()) return;

    this.loginError.set(null);
    window.location.href = buildSamlLoginUrl();
  }

  async onSubmit(): Promise<void> {
    if (!this.isFormValid()) return;

    this.isSubmitting.set(true);
    this.loginError.set(null);

    this.auth.login(this.username, this.password).subscribe({
      next: () => {
        this.navigateAfterAuth();
      },
      error: (err) => {
        const code = getApiErrorCode(err);
        if (code === 'AUTH_INVALID_CREDENTIALS') {
          this.loginError.set(getApiErrorMessage(err, 'Usuário ou senha inválidos.'));
        } else {
          this.loginError.set(getApiErrorMessage(err));
        }
        this.isSubmitting.set(false);
      },
    });
  }

  private completeSsoLogin(accessToken: string, refreshToken: string | null): void {
    this.isSubmitting.set(true);
    this.loginError.set(null);

    this.auth.setTokens(accessToken, refreshToken ?? undefined);
    this.navigateAfterAuth();
  }

  private navigateAfterAuth(): void {
    this.sessionInit.reset();
    this.sessionInit.ensureSession().subscribe({
      next: () => {
        void this.router.navigate(['/home'], { replaceUrl: true });
        this.isSubmitting.set(false);
      },
      error: () => {
        this.loginError.set('Login ok, mas falha ao carregar dados. Tente novamente.');
        this.isSubmitting.set(false);
      },
    });
  }
}
