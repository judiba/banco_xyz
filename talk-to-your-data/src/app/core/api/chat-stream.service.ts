import { Injectable, inject } from '@angular/core';
import { ApiConfig } from './api-config.service';
import { AuthService } from '../auth/auth.service';
import {
  ChatMessage,
  ConversationSummary,
  SseAssistantDeltaPayload,
  SseAssistantStartPayload,
  SseErrorPayload,
  SseEventType,
} from './api.types';
import { ApiErrorBody } from './api.types';

export interface ChatStreamHandlers {
  onUserMessage: (m: ChatMessage) => void;
  onAssistantStart: (p: SseAssistantStartPayload) => void;
  onDelta: (p: SseAssistantDeltaPayload) => void;
  onDone: (m: ChatMessage) => void;
  onConversationUpdated: (c: ConversationSummary) => void;
  onError: (p: SseErrorPayload) => void;
}

@Injectable({ providedIn: 'root' })
export class ChatStreamService {
  private readonly urls = inject(ApiConfig);
  private readonly auth = inject(AuthService);

  async streamMessage(
    conversationId: string,
    content: string,
    handlers: ChatStreamHandlers,
    signal?: AbortSignal,
  ): Promise<void> {
    const token = this.auth.getAccessToken();
    const res = await fetch(this.urls.conversations.stream(conversationId), {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Accept: 'text/event-stream',
        Authorization: `Bearer ${token ?? ''}`,
        'X-Request-Id': crypto.randomUUID(),
      },
      body: JSON.stringify({ content: content.trim() }),
      signal,
    });

    if (!res.ok) {
      let errBody: ApiErrorBody | { error?: SseErrorPayload } = {};
      try {
        errBody = await res.json();
      } catch {
        // noop
      }
      const apiErr = (errBody as ApiErrorBody).error;
      handlers.onError({
        code: apiErr?.code ?? 'STREAM_ERROR',
        message: apiErr?.message ?? 'Falha ao enviar mensagem.',
      });
      return;
    }

    const reader = res.body?.getReader();
    if (!reader) {
      handlers.onError({ code: 'STREAM_ERROR', message: 'Stream indisponível.' });
      return;
    }

    const decoder = new TextDecoder();
    let buffer = '';

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      const blocks = buffer.split('\n\n');
      buffer = blocks.pop() ?? '';

      for (const block of blocks) {
        this.parseSseBlock(block, handlers);
      }
    }

    if (buffer.trim()) {
      this.parseSseBlock(buffer, handlers);
    }
  }

  private parseSseBlock(block: string, handlers: ChatStreamHandlers): void {
    const lines = block.split('\n');
    let event = '';
    let data = '';

    for (const line of lines) {
      if (line.startsWith('event:')) event = line.slice(6).trim();
      if (line.startsWith('data:')) data = line.slice(5).trim();
    }

    if (!event || !data) return;

    try {
      const parsed = JSON.parse(data) as unknown;
      switch (event as SseEventType) {
        case 'user_message':
          handlers.onUserMessage((parsed as { message: ChatMessage }).message);
          break;
        case 'assistant_start':
          handlers.onAssistantStart(parsed as SseAssistantStartPayload);
          break;
        case 'assistant_delta':
          handlers.onDelta(parsed as SseAssistantDeltaPayload);
          break;
        case 'assistant_done':
          handlers.onDone((parsed as { message: ChatMessage }).message);
          break;
        case 'conversation_updated':
          handlers.onConversationUpdated(
            (parsed as { conversation: ConversationSummary }).conversation,
          );
          break;
        case 'error':
          handlers.onError(parsed as SseErrorPayload);
          break;
      }
    } catch {
      handlers.onError({ code: 'PARSE_ERROR', message: 'Erro ao processar resposta.' });
    }
  }
}
