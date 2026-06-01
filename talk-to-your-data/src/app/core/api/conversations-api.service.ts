import { HttpClient, HttpParams } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';
import { ApiConfig } from './api-config.service';
import {
  ChatMessage,
  ConversationSummary,
  CreateConversationRequest,
  PaginatedResponse,
  PatchConversationRequest,
  RegenerateMessageResponse,
  SendMessageResponse,
  WithMessageRequest,
  WithMessageResponse,
} from './api.types';

@Injectable({ providedIn: 'root' })
export class ConversationsApiService {
  private readonly http = inject(HttpClient);
  private readonly urls = inject(ApiConfig);

  list(params: {
    page?: number;
    pageSize?: number;
    q?: string;
    folderId?: string | null;
  }): Observable<PaginatedResponse<ConversationSummary>> {
    let httpParams = new HttpParams()
      .set('page', String(params.page ?? 1))
      .set('pageSize', String(params.pageSize ?? 50))
      .set('sort', 'lastUpdatedAt')
      .set('order', 'desc');

    if (params.q) {
      httpParams = httpParams.set('q', params.q);
    }
    if (params.folderId === null) {
      httpParams = httpParams.set('folderId', 'null');
    } else if (params.folderId) {
      httpParams = httpParams.set('folderId', params.folderId);
    }

    return this.http.get<PaginatedResponse<ConversationSummary>>(
      this.urls.conversations.list(),
      { params: httpParams },
    );
  }

  getOne(id: string): Observable<ConversationSummary> {
    return this.http.get<ConversationSummary>(this.urls.conversations.one(id));
  }

  create(body: CreateConversationRequest = {}): Observable<ConversationSummary> {
    return this.http.post<ConversationSummary>(this.urls.conversations.create(), {
      title: body.title ?? 'Novo chat',
      folderId: body.folderId ?? null,
    });
  }

  createWithMessage(body: WithMessageRequest): Observable<WithMessageResponse> {
    return this.http.post<WithMessageResponse>(
      this.urls.conversations.withMessage(),
      {
        content: body.content.trim(),
        folderId: body.folderId ?? null,
      },
    );
  }

  patch(id: string, body: PatchConversationRequest): Observable<ConversationSummary> {
    return this.http.patch<ConversationSummary>(
      this.urls.conversations.one(id),
      body,
    );
  }

  delete(id: string): Observable<void> {
    return this.http.delete<void>(this.urls.conversations.one(id));
  }

  getMessages(
    conversationId: string,
    page = 1,
    pageSize = 100,
  ): Observable<PaginatedResponse<ChatMessage>> {
    const params = new HttpParams()
      .set('page', String(page))
      .set('pageSize', String(pageSize))
      .set('order', 'asc');

    return this.http.get<PaginatedResponse<ChatMessage>>(
      this.urls.conversations.messages(conversationId),
      { params },
    );
  }

  sendMessage(conversationId: string, content: string): Observable<SendMessageResponse> {
    return this.http.post<SendMessageResponse>(
      this.urls.conversations.messages(conversationId),
      { content: content.trim() },
    );
  }

  regenerate(
    conversationId: string,
    messageId: string,
  ): Observable<RegenerateMessageResponse> {
    return this.http.post<RegenerateMessageResponse>(
      this.urls.conversations.regenerate(conversationId, messageId),
      {},
    );
  }

  exportTxt(conversationId: string): Observable<Blob> {
    return this.http.get(this.urls.conversations.export(conversationId, 'txt'), {
      responseType: 'blob',
    });
  }
}
