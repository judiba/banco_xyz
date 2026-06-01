import { Injectable, inject, signal } from '@angular/core';
import { Observable, tap } from 'rxjs';
import { AuthService } from '../auth/auth.service';
import { ConversationsStore } from '../../shared/conversations.store';
import { FoldersStore } from '../../shared/folders.store';

@Injectable({ providedIn: 'root' })
export class SessionInitService {
  private readonly auth = inject(AuthService);
  private readonly conversations = inject(ConversationsStore);
  private readonly folders = inject(FoldersStore);

  readonly isLoading = signal(false);
  readonly initError = signal<string | null>(null);
  private initialized = false;

  ensureSession(): Observable<unknown> {
    this.isLoading.set(true);
    this.initError.set(null);

    return this.auth.bootstrap().pipe(
      tap({
        next: (res) => {
          this.conversations.hydrate(res.conversations.data);
          this.folders.hydrate(res.folders.data);
          this.initialized = true;
          this.isLoading.set(false);
        },
        error: (err) => {
          this.initError.set('Não foi possível carregar os dados da sessão.');
          this.isLoading.set(false);
          console.error('[session] bootstrap failed', err);
        },
      }),
    );
  }

  reset(): void {
    this.initialized = false;
    this.conversations.clear();
    this.folders.clear();
  }

  get hasInitialized(): boolean {
    return this.initialized;
  }
}
