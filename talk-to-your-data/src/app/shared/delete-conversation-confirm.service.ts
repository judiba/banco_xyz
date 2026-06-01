
import { Injectable, inject, signal } from '@angular/core';
import { ConversationsStore } from './conversations.store';


@Injectable({ providedIn: 'root' })
export class DeleteConversationConfirmService {
  private readonly conversationsStore = inject(ConversationsStore);

  
  readonly isOpen = signal(false);

  
  readonly conversationId = signal<string | null>(null);

  
  private onConfirmDelete: (() => void) | null = null;

  
  readonly title = signal<string>('Excluir conversa?');
  readonly text = signal<string>(
    'Esta ação não pode ser desfeita e todo histórico\nserá permanentemente removido',
  );
  readonly warningText = signal<string | null>(null);

  
  open(conversationId: string): void {
    this.onConfirmDelete = null;
    this.title.set('Excluir conversa?');
    this.text.set(
      'Esta ação não pode ser desfeita e todo histórico\nserá permanentemente removido',
    );
    this.warningText.set(
      'Ao excluir esta conversa, todas as mensagens serão removidas permanentemente, sem possibilidade de recuperação após a confirmação.'
    );

    this.conversationId.set(conversationId);
    this.isOpen.set(true);
  }

  
  openWithCallback(params: {
    onConfirm: () => void;
    title: string;
    text: string;
    warningText?: string | null;
  }): void {
    this.onConfirmDelete = params.onConfirm;
    this.title.set(params.title);
    this.text.set(params.text);
    this.warningText.set(params.warningText ?? null);

    this.conversationId.set(null);
    this.isOpen.set(true);
  }

  close(): void {
    this.isOpen.set(false);
    this.conversationId.set(null);
    this.onConfirmDelete = null;
    this.warningText.set(null);
  }

  confirmDelete(): void {

    if (this.onConfirmDelete) {
      this.onConfirmDelete();
      this.close();
      return;
    }

    const id = this.conversationId();
    if (id) {
      this.conversationsStore.deleteConversation(id);
    }
    this.close();
  }
}
