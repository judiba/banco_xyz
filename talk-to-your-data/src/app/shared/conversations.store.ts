import { Injectable, computed, inject, signal } from '@angular/core';
import { Observable, map, tap } from 'rxjs';
import { environment } from '../../environments/environment';
import { ConversationsApiService } from '../core/api/conversations-api.service';
import { ChatStreamService } from '../core/api/chat-stream.service';
import { getApiErrorMessage } from '../core/api/api-error.util';
import type {
  ChatMessage,
  ConversationSummary,
  SendMessageResponse,
  WithMessageResponse,
} from '../core/api/api.types';

export type { ConversationSummary, ChatMessage };
export type ChatMessageRole = 'user' | 'assistant';

@Injectable({ providedIn: 'root' })
export class ConversationsStore {
  private readonly api = inject(ConversationsApiService);
  private readonly chatStream = inject(ChatStreamService);

  private readonly _conversations = signal<ConversationSummary[]>([]);
  private readonly _currentConversationId = signal<string | null>(null);
  private readonly _messagesByConversation = signal<Record<string, ChatMessage[]>>({});
  private readonly _isSending = signal(false);
  private readonly _chatError = signal<string | null>(null);
  private streamAbort: AbortController | null = null;

  readonly conversations = this._conversations.asReadonly();
  readonly currentConversationId = this._currentConversationId.asReadonly();
  readonly isSending = this._isSending.asReadonly();
  readonly chatError = this._chatError.asReadonly();

  readonly currentConversation = computed(() => {
    const id = this._currentConversationId();
    if (!id) return null;
    return this._conversations().find((c) => c.id === id) ?? null;
  });

  readonly currentMessages = computed(() => {
    const id = this._currentConversationId();
    if (!id) return [];
    return this._messagesByConversation()[id] ?? [];
  });

  /** Conversas sem pasta — lista da sidebar "Suas conversas". */
  readonly conversationsWithoutFolder = computed(() =>
    this._conversations().filter((c) => c.folderId == null),
  );

  hydrate(conversations: ConversationSummary[]): void {
    const sorted = [...conversations].sort(
      (a, b) => (b.lastUpdatedAt ?? 0) - (a.lastUpdatedAt ?? 0),
    );
    this._conversations.set(sorted);
  }

  upsertConversation(conversation: ConversationSummary): void {
    this._conversations.update((list) => {
      const idx = list.findIndex((c) => c.id === conversation.id);
      if (idx < 0) {
        return [conversation, ...list].sort(
          (a, b) => b.lastUpdatedAt - a.lastUpdatedAt,
        );
      }
      const next = [...list];
      next[idx] = conversation;
      return next.sort((a, b) => b.lastUpdatedAt - a.lastUpdatedAt);
    });
  }

  removeConversationFromList(id: string): void {
    if (this._currentConversationId() === id) {
      this._currentConversationId.set(null);
    }
    this._conversations.update((list) => list.filter((c) => c.id !== id));
    this._messagesByConversation.update((map) => {
      const { [id]: _removed, ...rest } = map;
      return rest;
    });
  }

  /** Inicia chat em branco; a conversa no backend só é criada na primeira mensagem. */
  startNewConversation(): void {
    this.streamAbort?.abort();
    this._currentConversationId.set(null);
    this._chatError.set(null);
  }

  createConversation(): void {
    this.startNewConversation();
    this.api.create({ title: 'Novo chat', folderId: null }).subscribe({
      next: (conv) => {
        this.upsertConversation(conv);
        this._currentConversationId.set(conv.id);
        this.setMessages(conv.id, []);
      },
      error: (err) => console.error('[conversations] create', getApiErrorMessage(err)),
    });
  }

  selectConversation(id: string): void {
    this._currentConversationId.set(id);
    this._chatError.set(null);

    const existing = this._messagesByConversation()[id];
    if (existing !== undefined) return;

    this.api.getMessages(id).subscribe({
      next: (res) => this.setMessages(id, res.data),
      error: (err) => console.error('[conversations] messages', getApiErrorMessage(err)),
    });
  }

  renameConversation(id: string, title: string): void {
    const t = title.trim();
    if (!t) return;

    this.api.patch(id, { title: t }).subscribe({
      next: (conv) => this.upsertConversation(conv),
      error: (err) => console.error('[conversations] rename', getApiErrorMessage(err)),
    });
  }

  setConversationFolder(conversationId: string, folderId: string | null): void {
    this.api.patch(conversationId, { folderId }).subscribe({
      next: (conv) => this.upsertConversation(conv),
      error: (err) =>
        console.error('[conversations] move folder', getApiErrorMessage(err)),
    });
  }

  deleteConversation(id: string): void {
    this.api.delete(id).subscribe({
      next: () => this.removeConversationFromList(id),
      error: (err) => console.error('[conversations] delete', getApiErrorMessage(err)),
    });
  }

  getConversationMessages(conversationId: string): ChatMessage[] {
    return this._messagesByConversation()[conversationId] ?? [];
  }

  sendMessage(content: string): void {
    const text = content.trim();
    if (!text || this._isSending()) return;

    this._chatError.set(null);
    const conversationId = this._currentConversationId();

    if (!conversationId) {
      this.sendFirstMessage(text);
      return;
    }

    if (environment.chatStreaming) {
      this.sendStreaming(conversationId, text);
    } else {
      this.sendSync(conversationId, text);
    }
  }

  regenerateAssistantMessage(conversationId: string, messageId: string): void {
    if (this._isSending()) return;
    this._isSending.set(true);
    this._chatError.set(null);

    this.api.regenerate(conversationId, messageId).subscribe({
      next: (res) => {
        this.replaceAssistantMessage(conversationId, messageId, res.message.content);
        this.upsertConversation(res.conversation);
        this._isSending.set(false);
      },
      error: (err) => {
        this._chatError.set(getApiErrorMessage(err));
        this._isSending.set(false);
      },
    });
  }

  refreshConversationsList(params?: {
    q?: string;
    folderId?: string | null;
  }): Observable<ConversationSummary[]> {
    return this.api.list(params ?? {}).pipe(
      tap((res) => this.hydrate(res.data)),
      map((res) => res.data),
    );
  }

  private sendFirstMessage(text: string): void {
    this._isSending.set(true);
    this.api.createWithMessage({ content: text, folderId: null }).subscribe({
      next: (res) => this.applyWithMessageResponse(res),
      error: (err) => {
        this._chatError.set(getApiErrorMessage(err));
        this._isSending.set(false);
      },
    });
  }

  private sendSync(conversationId: string, text: string): void {
    this._isSending.set(true);
    this.api.sendMessage(conversationId, text).subscribe({
      next: (res) => this.applySendMessageResponse(res),
      error: (err) => {
        this._chatError.set(getApiErrorMessage(err));
        this._isSending.set(false);
      },
    });
  }

  private async sendStreaming(conversationId: string, text: string): Promise<void> {
    this.streamAbort?.abort();
    this.streamAbort = new AbortController();
    this._isSending.set(true);

    let assistantMessageId: string | null = null;

    await this.chatStream.streamMessage(
      conversationId,
      text,
      {
        onUserMessage: (m) => {
          this.appendMessage(conversationId, m);
        },
        onAssistantStart: (p) => {
          assistantMessageId = p.messageId;
          const pending: ChatMessage = {
            id: p.messageId,
            conversationId: p.conversationId,
            role: 'assistant',
            content: '',
            createdAt: Date.now(),
            status: 'pending',
          };
          this.appendMessage(conversationId, pending);
        },
        onDelta: (p) => {
          if (!assistantMessageId) return;
          this.appendDelta(conversationId, p.messageId, p.delta);
        },
        onDone: (m) => {
          this.replaceMessage(conversationId, m.id, m);
          this._isSending.set(false);
        },
        onConversationUpdated: (c) => {
          this.upsertConversation(c);
        },
        onError: (p) => {
          this._chatError.set(p.message);
          this._isSending.set(false);
        },
      },
      this.streamAbort.signal,
    );

    if (this._isSending()) {
      this._isSending.set(false);
    }
  }

  private applyWithMessageResponse(res: WithMessageResponse): void {
    this.upsertConversation(res.conversation);
    this.setMessages(res.conversation.id, [res.userMessage, res.assistantMessage]);
    this._currentConversationId.set(res.conversation.id);
    this._isSending.set(false);
  }

  private applySendMessageResponse(res: SendMessageResponse): void {
    this.upsertConversation(res.conversation);
    this.appendMessage(res.conversation.id, res.userMessage);
    this.appendMessage(res.conversation.id, res.assistantMessage);
    this._isSending.set(false);
  }

  private setMessages(conversationId: string, messages: ChatMessage[]): void {
    this._messagesByConversation.update((map) => ({
      ...map,
      [conversationId]: messages,
    }));
  }

  private appendMessage(conversationId: string, message: ChatMessage): void {
    this._messagesByConversation.update((map) => ({
      ...map,
      [conversationId]: [...(map[conversationId] ?? []), message],
    }));
  }

  private appendDelta(conversationId: string, messageId: string, delta: string): void {
    this._messagesByConversation.update((map) => {
      const list = map[conversationId] ?? [];
      const idx = list.findIndex((m) => m.id === messageId);
      if (idx < 0) return map;
      const current = list[idx];
      const updated: ChatMessage = {
        ...current,
        content: current.content + delta,
        status: 'pending',
      };
      const next = [...list];
      next[idx] = updated;
      return { ...map, [conversationId]: next };
    });
  }

  private replaceMessage(conversationId: string, messageId: string, message: ChatMessage): void {
    this._messagesByConversation.update((map) => {
      const list = map[conversationId] ?? [];
      const idx = list.findIndex((m) => m.id === messageId);
      if (idx < 0) return map;
      const next = [...list];
      next[idx] = message;
      return { ...map, [conversationId]: next };
    });
  }

  replaceAssistantMessage(
    conversationId: string,
    messageId: string,
    text: string,
  ): void {
    const message = text.trim();
    if (!message) return;
    const now = Date.now();
    this._messagesByConversation.update((map) => {
      const list = map[conversationId];
      if (!list?.length) return map;
      const idx = list.findIndex((m) => m.id === messageId);
      if (idx < 0) return map;
      const current = list[idx];
      if (current.role !== 'assistant') return map;
      const next = [...list];
      next[idx] = { ...current, content: message, createdAt: now, status: 'completed' };
      return { ...map, [conversationId]: next };
    });
  }

  clear(): void {
    this.streamAbort?.abort();
    this._conversations.set([]);
    this._messagesByConversation.set({});
    this._currentConversationId.set(null);
    this._isSending.set(false);
    this._chatError.set(null);
  }
}
