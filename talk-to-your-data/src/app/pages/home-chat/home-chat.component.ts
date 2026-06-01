
/**
 * HOME-CHAT PAGE (CHAT UI)
 * - Renderiza a conversa atual (mensagens)
 * - Envia mensagens do usuário (store)
 * - Exporta a conversa em TXT/PDF
 * - Utilitários de UI: scroll, copiar, formatação simples de markdown
 */
import { CommonModule } from '@angular/common';
import {
  Component,
  ElementRef,
  ViewChild,
  effect,
  inject,
  signal,
} from '@angular/core';
import { FormsModule } from '@angular/forms';
import { jsPDF } from 'jspdf';

// EXPORT (TXT/PDF)
import {
  buildConversationExportTxt,
  renderConversationExportPdf,
} from '../../shared/conversation-export.util';

import { AuthService } from '../../core/auth/auth.service';
import { MessagesApiService } from '../../core/api/messages-api.service';
import { ChatMessage, ConversationsStore } from '../../shared/conversations.store';

@Component({
  selector: 'app-home-chat',
  standalone: true,



  imports: [CommonModule, FormsModule],
  templateUrl: './home-chat.component.html',
  styleUrl: './home-chat.component.scss',
})
export class HomeChatComponent {
  private readonly conversationsStore = inject(ConversationsStore);
  private readonly auth = inject(AuthService);
  private readonly messagesApi = inject(MessagesApiService);

  // UI STATE: feedback por mensagem do assistente (like/deslike)
  // key: messageId
  readonly assistantFeedback = signal<Record<string, 'like' | 'deslike' | null>>(
    {},
  );

  // VIEWCHILD: âncora do final da lista (scroll automático)
  @ViewChild('messagesEnd')
  private readonly messagesEnd?: ElementRef<HTMLDivElement>;

  readonly userName = () => this.auth.getDisplayName();
  readonly assistantName = () => this.auth.assistantDisplayName();
  readonly conversations = this.conversationsStore.conversations;
  readonly currentConversation = this.conversationsStore.currentConversation;
  readonly currentConversationId = this.conversationsStore.currentConversationId;
  readonly currentMessages = this.conversationsStore.currentMessages;
  readonly isSending = this.conversationsStore.isSending;
  readonly chatError = this.conversationsStore.chatError;

  // COMPOSER: input da mensagem atual
  readonly message = signal('');

  // EXPORT MODAL: estado do modal de exportação
  readonly isExportModalOpen = signal(false);
  readonly exportFormat = signal<'pdf' | 'txt' | null>(null);

  constructor() {
    // UI: sempre que a lista de mensagens mudar, rola para o final
    effect(() => {
      void this.currentMessages();
      queueMicrotask(() => this.scrollToBottom());
    });
  }

  
  // COMPOSER: Enter envia (Shift+Enter quebra linha)
  onEnter(event: Event): void {
    const e = event as KeyboardEvent;
    if (e.shiftKey) return;
    e.preventDefault();
    this.send();
  }

  send(): void {
    const text = this.message().trim();
    if (!text || this.isSending()) return;

    this.conversationsStore.sendMessage(text);
    this.message.set('');
  }

  
  // EXPORT MODAL: abrir
  openExportModal(): void {
    this.exportFormat.set(null);
    this.isExportModalOpen.set(true);
  }

  // EXPORT MODAL: fechar
  closeExportModal(): void {
    this.isExportModalOpen.set(false);
  }

  // EXPORT MODAL: selecionar formato
  selectExportFormat(format: 'pdf' | 'txt'): void {
    this.exportFormat.set(format);
  }

  // EXPORT MODAL: confirmar e fazer download
  confirmExport(): void {
    const format = this.exportFormat();
    if (!format) return;

    if (format === 'txt') {
      this.downloadConversationAsTxt();
    } else {
      this.downloadConversationAsPdf();
    }

    this.closeExportModal();
  }

  
  // EXPORT TXT: monta conteúdo e baixa arquivo .txt
  private downloadConversationAsTxt(): void {
    const date = new Date();

    const conversationTitle = this.currentConversation()?.title || 'Novo chat';
    const conversationDescription =
      this.currentConversation()?.description || '(sem descrição)';

    const meta = {
      userName: this.userName(),
      assistantName: this.assistantName(),
      conversationTitle,
      conversationDescription,
      exportedAt: date,
    };

    const messages = this.currentMessages().map((m) => ({
      role: m.role,
      content: m.content,
      createdAt: m.createdAt,
    }));

    const content = buildConversationExportTxt(meta, messages);

    const blob = new Blob([content], { type: 'text/plain;charset=utf-8' });
    this.downloadBlob(blob, this.buildExportFileName('txt', date));
  }

  
  // EXPORT PDF: renderiza PDF via jsPDF e baixa arquivo
  private downloadConversationAsPdf(): void {
    const date = new Date();

    const conversationTitle = this.currentConversation()?.title || 'Novo chat';
    const conversationDescription =
      this.currentConversation()?.description || '(sem descrição)';

    const meta = {
      userName: this.userName(),
      assistantName: this.assistantName(),
      conversationTitle,
      conversationDescription,
      exportedAt: date,
    };

    const messages = this.currentMessages().map((m) => ({
      role: m.role,
      content: m.content,
      createdAt: m.createdAt,
    }));

    const doc = new jsPDF({
      orientation: 'p',
      unit: 'pt',
      format: 'a4',
    });

    renderConversationExportPdf(doc, meta, messages);
    doc.save(this.buildExportFileName('pdf', date));
  }

  
  // UTIL: nome de arquivo seguro para download
  private buildExportFileName(ext: 'txt' | 'pdf', date: Date): string {
    const title = this.currentConversation()?.title || 'novo-chat';
    const safeTitle = this.sanitizeFileName(title).slice(0, 60) || 'conversa';
    const datePart = date.toISOString().slice(0, 10);
    return `${safeTitle}-${datePart}.${ext}`;
  }

  // UTIL: remove caracteres inválidos do nome do arquivo
  private sanitizeFileName(name: string): string {
    return name
      .trim()
      .replace(/[\\\/:\*\?"<>\|]/g, ' ')
      .replace(/\s+/g, ' ')
      .trim();
  }

  // UTIL: baixa um Blob no navegador
  private downloadBlob(blob: Blob, fileName: string): void {
    const url = URL.createObjectURL(blob);

    const a = document.createElement('a');
    a.href = url;
    a.download = fileName;
    a.click();

    setTimeout(() => URL.revokeObjectURL(url), 250);
  }




  // TEMPLATE: otimiza *ngFor (evita recriar DOM)
  trackByMessageId(_index: number, m: ChatMessage): string {
    return m.id;
  }

  formatMessageTime(epochMs: number): string {
    if (!epochMs) return '';
    const date = new Date(epochMs);
    const now = new Date();
    const isToday =
      date.getDate() === now.getDate() &&
      date.getMonth() === now.getMonth() &&
      date.getFullYear() === now.getFullYear();

    const time = date.toLocaleTimeString('pt-BR', {
      hour: '2-digit',
      minute: '2-digit',
    });

    if (isToday) return time;

    const yesterday = new Date(now);
    yesterday.setDate(yesterday.getDate() - 1);
    const isYesterday =
      date.getDate() === yesterday.getDate() &&
      date.getMonth() === yesterday.getMonth() &&
      date.getFullYear() === yesterday.getFullYear();

    if (isYesterday) return `Ontem, ${time}`;

    return date.toLocaleString('pt-BR', {
      day: '2-digit',
      month: 'short',
      hour: '2-digit',
      minute: '2-digit',
    });
  }

  messageTimeIso(epochMs: number): string {
    return epochMs ? new Date(epochMs).toISOString() : '';
  }

  userInitial(): string {
    const name = this.userName().trim();
    return (name.charAt(0) || 'V').toUpperCase();
  }

  hasPendingAssistantBubble(): boolean {
    return this.currentMessages().some(
      (m) => m.role === 'assistant' && m.status === 'pending',
    );
  }

  // UI: copiar texto de mensagem
  onCopyClicked(messageId: string, text: string): void {
    this.copyToClipboard(text);
    this.flashAction(messageId, 'copy');
  }

  toggleAssistantFeedback(messageId: string, kind: 'like' | 'deslike'): void {
    const current = this.assistantFeedback()[messageId] ?? null;
    const next: 'like' | 'deslike' | null = current === kind ? null : kind;

    this.assistantFeedback.update((map) => ({ ...map, [messageId]: next }));
    this.flashAction(messageId, kind);

    const apiFeedback: 'like' | 'dislike' | null =
      next === 'like' ? 'like' : next === 'deslike' ? 'dislike' : null;

    this.messagesApi.setFeedback(messageId, apiFeedback).subscribe({
      error: (err) => console.error('[home-chat] feedback', err),
    });
  }

  isFeedbackSelected(messageId: string, kind: 'like' | 'deslike'): boolean {
    return (this.assistantFeedback()[messageId] ?? null) === kind;
  }

  private flashAction(
    messageId: string,
    action: 'copy' | 'like' | 'deslike' | 'refresh',
  ): void {
    const el = document.querySelector(
      `[data-message-id="${messageId}"][data-action="${action}"]`,
    ) as HTMLElement | null;

    if (!el) return;
    el.classList.add('is-active');
    window.setTimeout(() => el.classList.remove('is-active'), 220);
  }

  // UI: copiar texto de mensagem
  copyToClipboard(text: string): void {
    const value = text ?? '';
    if (navigator?.clipboard?.writeText) {
      navigator.clipboard.writeText(value).catch(() => {
        this.copyToClipboardLegacy(value);
      });
      return;
    }
    this.copyToClipboardLegacy(value);
  }

  regenerateAssistantMessage(conversationId: string, messageId: string): void {
    this.flashAction(messageId, 'refresh');
    this.conversationsStore.regenerateAssistantMessage(conversationId, messageId);
  }

  // UI: converte markdown simples -> HTML para renderização
  formatAssistantMessage(content: string): string {
    return this.simpleMarkdownToHtml(String(content ?? ''));
  }

  // UI: scroll para o final da lista de mensagens
  private scrollToBottom(): void {
    try {
      this.messagesEnd?.nativeElement?.scrollIntoView({ block: 'end' });
    } catch {
      // noop
    }
  }

  // LEGACY: fallback para copiar (caso Clipboard API falhe)
  private copyToClipboardLegacy(text: string): void {
    try {
      const ta = document.createElement('textarea');
      ta.value = text;
      ta.setAttribute('readonly', 'true');
      ta.style.position = 'fixed';
      ta.style.left = '-9999px';
      ta.style.top = '0';
      document.body.appendChild(ta);
      ta.select();
      document.execCommand('copy');
      document.body.removeChild(ta);
    } catch {
      // noop
    }
  }

  
  // MARKDOWN: parser mínimo (lista + parágrafo + negrito)
  private simpleMarkdownToHtml(markdown: string): string {
    const escaped = this.escapeHtml(markdown);
    const lines = escaped.split(/\r?\n/);

    let html = '';
    let inList = false;
    let paragraphLines: string[] = [];

    const closeListIfNeeded = () => {
      if (!inList) return;
      html += '</ul>';
      inList = false;
    };

    const flushParagraphIfNeeded = () => {
      if (paragraphLines.length === 0) return;

      const paragraphText = paragraphLines.join(' ').trim();
      if (paragraphText) {
        html += `<p>${this.formatInlineMarkdown(paragraphText)}</p>`;
      }
      paragraphLines = [];
    };

    for (const rawLine of lines) {
      const line = rawLine.trim();

      if (!line) {
        flushParagraphIfNeeded();
        closeListIfNeeded();
        continue;
      }

      const bullet = line.match(/^[-*]\s+(.*)$/);
      if (bullet) {
        flushParagraphIfNeeded();

        if (!inList) {
          html += '<ul>';
          inList = true;
        }

        html += `<li>${this.formatInlineMarkdown(bullet[1])}</li>`;
        continue;
      }

      closeListIfNeeded();
      paragraphLines.push(line);
    }

    flushParagraphIfNeeded();
    closeListIfNeeded();
    return html;
  }

  // MARKDOWN INLINE: apenas **negrito**
  private formatInlineMarkdown(text: string): string {
    return text.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
  }

  // SECURITY: escapa HTML para evitar injeção
  private escapeHtml(value: string): string {
    const AMP = '&' + 'amp;';
    const LT = '&' + 'lt;';
    const GT = '&' + 'gt;';
    const QUOT = '&' + 'quot;';
    const APOS = '&' + '#039;';

    return value
      .replace(/&/g, AMP)
      .replace(/</g, LT)
      .replace(/>/g, GT)
      .replace(/"/g, QUOT)
      .replace(/'/g, APOS);
  }
}
