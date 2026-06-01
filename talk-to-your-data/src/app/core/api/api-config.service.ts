import { Injectable } from '@angular/core';
import { environment } from '../../../environments/environment';

@Injectable({ providedIn: 'root' })
export class ApiConfig {
  readonly base = environment.apiBaseUrl;

  auth = {
    login: () => `${this.base}/auth/login`,
    refresh: () => `${this.base}/auth/refresh`,
    logout: () => `${this.base}/auth/logout`,
  };

  session = {
    bootstrap: () => `${this.base}/session/bootstrap`,
  };

  users = {
    me: () => `${this.base}/users/me`,
  };

  conversations = {
    list: () => `${this.base}/conversations`,
    create: () => `${this.base}/conversations`,
    withMessage: () => `${this.base}/conversations/with-message`,
    one: (id: string) => `${this.base}/conversations/${id}`,
    messages: (id: string) => `${this.base}/conversations/${id}/messages`,
    stream: (id: string) => `${this.base}/conversations/${id}/messages/stream`,
    regenerate: (convId: string, msgId: string) =>
      `${this.base}/conversations/${convId}/messages/${msgId}/regenerate`,
    export: (id: string, format: 'txt' | 'pdf' = 'txt') =>
      `${this.base}/conversations/${id}/export?format=${format}`,
  };

  folders = {
    list: () => `${this.base}/folders`,
    one: (id: string) => `${this.base}/folders/${id}`,
    bySlug: (slug: string) => `${this.base}/folders/by-slug/${slug}`,
    create: () => `${this.base}/folders`,
    patch: (id: string) => `${this.base}/folders/${id}`,
    delete: (id: string, cascade = true) =>
      `${this.base}/folders/${id}?cascade=${cascade}`,
  };

  messages = {
    feedback: (messageId: string) => `${this.base}/messages/${messageId}/feedback`,
  };
}
