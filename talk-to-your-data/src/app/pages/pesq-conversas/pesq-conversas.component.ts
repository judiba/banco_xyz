
import { CommonModule } from '@angular/common';
import { Component, ElementRef, ViewChild, computed, inject, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { jsPDF } from 'jspdf';

import {
  buildConversationExportTxt,
  renderConversationExportPdf,
} from '../../shared/conversation-export.util';
import { AuthService } from '../../core/auth/auth.service';

import { Router } from '@angular/router';
import { DeleteConversationConfirmService } from '../../shared/delete-conversation-confirm.service';
import { FoldersStore } from '../../shared/folders.store';
import {
  ConversationsStore,
  type ConversationSummary,
} from '../../shared/conversations.store';


@Component({
  selector: 'app-pesq-conversas',
  standalone: true,


  imports: [CommonModule, FormsModule],
  templateUrl: './pesq-conversas.component.html',
  styleUrl: './pesq-conversas.component.scss',
})
export class PesqConversasComponent {
  private readonly router = inject(Router);
  readonly openMenuConversationId = signal<string | null>(null);
  readonly menuPosition = signal<{ left: number; top: number }>({
    left: 0,
    top: 0,
  });

  
  readonly folders = computed(() => this.foldersStore.folders());

  
  readonly openedMoveToFolderMenuPos = signal<
    | {
        top: number;
        left: number;
      }
    | null
  >(null);

  private moveToFolderCloseTimer: number | null = null;

  toggleConversationMenu(event: MouseEvent, conversationId: string): void {
    event.stopPropagation();
    if (this.openMenuConversationId() === conversationId) {
      this.closeConversationMenu();
      return;
    }

    this.openMenuConversationId.set(conversationId);
    const btn = event.currentTarget as HTMLElement | null;
    const rect = btn?.getBoundingClientRect();

    if (!rect) return;

    const POPOVER_WIDTH = 192;
    const GAP = 0;

    const left = Math.max(8, rect.left - POPOVER_WIDTH - GAP);
    const top = rect.bottom + 2;

    this.menuPosition.set({ left, top });
  }

  closeConversationMenu(): void {
    this.openMenuConversationId.set(null);
    this.closeMoveToFolderMenu();
  }

  
  openMoveToFolderMenu(event: MouseEvent): void {
    event.stopPropagation();
    this.cancelCloseMoveToFolderMenu();

    const el = event.currentTarget as HTMLElement | null;
    if (!el) return;

    const rect = el.getBoundingClientRect();

    const menuWidth = 192;
    const menuHeight = 240;
    const gap = 1;


    const mainPos = this.menuPosition();
    const mainWidth = 192; // mesmo do SCSS (.search-menu-popover width)

    let left = mainPos.left + mainWidth + gap;
    if (left + menuWidth > window.innerWidth - 8) {
      left = mainPos.left - menuWidth - gap;
    }
    left = Math.max(8, left);

    let top = rect.top - 8;
    if (top + menuHeight > window.innerHeight - 8) {
      top = window.innerHeight - menuHeight - 8;
    }
    top = Math.max(8, top);

    this.openedMoveToFolderMenuPos.set({ top, left });
  }

  scheduleCloseMoveToFolderMenu(): void {
    this.cancelCloseMoveToFolderMenu();
    this.moveToFolderCloseTimer = window.setTimeout(() => {
      this.openedMoveToFolderMenuPos.set(null);
      this.moveToFolderCloseTimer = null;
    }, 140);
  }

  cancelCloseMoveToFolderMenu(): void {
    if (this.moveToFolderCloseTimer !== null) {
      window.clearTimeout(this.moveToFolderCloseTimer);
      this.moveToFolderCloseTimer = null;
    }
  }

  closeMoveToFolderMenu(): void {
    this.cancelCloseMoveToFolderMenu();
    this.openedMoveToFolderMenuPos.set(null);
  }

  moveConversationToFolderId(conversationId: string, folderId: string): void {
    this.conversationsStore.setConversationFolder(conversationId, folderId);
    this.closeConversationMenu();
  }
  readonly isCreateFolderModalOpen = signal(false);
  readonly newFolderName = signal('');
  readonly createFolderError = signal<string | null>(null);
  readonly showCreateFolderInfo = signal(true);

  
  readonly createFolderMoveConversationId = signal<string | null>(null);

  createFolderFromMoveMenu(conversation: ConversationSummary): void {
    this.createFolderMoveConversationId.set(conversation.id);
    this.openCreateFolderModal();
    this.closeConversationMenu();
  }

  openCreateFolderModal(): void {
    this.createFolderError.set(null);
    this.newFolderName.set('');
    this.showCreateFolderInfo.set(true);
    this.isCreateFolderModalOpen.set(true);

    setTimeout(() => this.createFolderInput?.nativeElement?.focus(), 0);
  }

  closeCreateFolderModal(): void {
    this.isCreateFolderModalOpen.set(false);
    this.createFolderMoveConversationId.set(null);
  }

  submitCreateFolder(): void {
    const name = this.newFolderName().trim();
    if (!name) {
      this.createFolderError.set('Informe o nome da pasta.');
      return;
    }

    const conversationId = this.createFolderMoveConversationId();

    this.foldersStore.createFolder(name, {
      onSuccess: (folder) => {
        if (conversationId) {
          this.conversationsStore.setConversationFolder(conversationId, folder.id);
        }
        this.closeCreateFolderModal();
      },
      onError: (message) => this.createFolderError.set(message),
    });
  }
  readonly isExportModalOpen = signal(false);
  readonly exportFormat = signal<'pdf' | 'txt' | null>(null);

  openExportModal(event?: Event, conversation?: ConversationSummary): void {
    event?.stopPropagation();
    this.closeConversationMenu();
    if (conversation?.id) {
      this.conversationsStore.selectConversation(conversation.id);
    }

    this.exportFormat.set(null);
    this.isExportModalOpen.set(true);
  }

  closeExportModal(): void {
    this.isExportModalOpen.set(false);
  }

  selectExportFormat(format: 'pdf' | 'txt'): void {
    this.exportFormat.set(format);
  }

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

  private downloadConversationAsTxt(): void {
    const date = new Date();

    const conversationTitle = this.conversationsStore.currentConversation()?.title || 'Novo chat';
    const conversationDescription =
      this.conversationsStore.currentConversation()?.description || '(sem descrição)';

    const meta = {
      userName: this.auth.getDisplayName(),
      assistantName: this.auth.assistantDisplayName(),
      conversationTitle,
      conversationDescription,
      exportedAt: date,
    };

    const messages = this.conversationsStore.currentMessages().map((m) => ({
      role: m.role,
      content: m.content,
      createdAt: m.createdAt,
    }));

    const content = buildConversationExportTxt(meta, messages);

    const blob = new Blob([content], { type: 'text/plain;charset=utf-8' });
    this.downloadBlob(blob, this.buildExportFileName('txt', date));
  }

  private downloadConversationAsPdf(): void {
    const date = new Date();

    const conversationTitle = this.conversationsStore.currentConversation()?.title || 'Novo chat';
    const conversationDescription =
      this.conversationsStore.currentConversation()?.description || '(sem descrição)';

    const meta = {
      userName: this.auth.getDisplayName(),
      assistantName: this.auth.assistantDisplayName(),
      conversationTitle,
      conversationDescription,
      exportedAt: date,
    };

    const messages = this.conversationsStore.currentMessages().map((m) => ({
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

  private buildExportFileName(ext: 'txt' | 'pdf', date: Date): string {
    const title = this.conversationsStore.currentConversation()?.title || 'novo-chat';
    const safeTitle = this.sanitizeFileName(title).slice(0, 60) || 'conversa';
    const datePart = date.toISOString().slice(0, 10);
    return `${safeTitle}-${datePart}.${ext}`;
  }

  private sanitizeFileName(name: string): string {
    return name
      .trim()
      .replace(/[\\\/:\*\?"<>\|]/g, ' ')
      .replace(/\s+/g, ' ')
      .trim();
  }

  private downloadBlob(blob: Blob, fileName: string): void {
    const url = URL.createObjectURL(blob);

    const a = document.createElement('a');
    a.href = url;
    a.download = fileName;
    a.click();

    setTimeout(() => URL.revokeObjectURL(url), 250);
  }

  @ViewChild('createFolderInput')
  private createFolderInput?: ElementRef<HTMLInputElement>;
  private readonly auth = inject(AuthService);
  private readonly conversationsStore = inject(ConversationsStore);
  private readonly foldersStore = inject(FoldersStore);
  private readonly deleteConversationConfirm = inject(
    DeleteConversationConfirmService,
  );

  readonly editingConversationId = signal<string | null>(null);
  readonly editedConversationTitle = signal('');
  @ViewChild('renameConversationInput')
  private renameConversationInput?: ElementRef<HTMLInputElement>;

  readonly isRenameConversationModalOpen = signal(false);
  readonly renameConversationId = signal<string | null>(null);
  readonly renameConversationTitle = signal('');
  readonly renameConversationError = signal<string | null>(null);
  readonly conversations = this.conversationsStore.conversations;
  readonly searchQuery = signal('');

  
  private normalizeSearchText(value: string | null | undefined): string {
    return (value ?? '')
      .trim()
      .toLowerCase()
      .normalize('NFD')
      .replace(/[\u0300-\u036f]/g, '');
  }

  
  readonly filteredConversations = computed(() => {
    const q = this.normalizeSearchText(this.searchQuery());
    const list = this.conversations();

    const sorted = [...list].sort(
      (a, b) => (b.lastUpdatedAt ?? 0) - (a.lastUpdatedAt ?? 0),
    );

    if (!q) return sorted;

    return sorted.filter((c) => {
      const haystack = this.normalizeSearchText(
        `${c.title} ${c.description ?? ''}`,
      );
      return haystack.includes(q);
    });
  });

  
  readonly searchResultsCount = computed(() => {
    const q = this.searchQuery().trim();
    if (!q) return 0;
    return this.filteredConversations().length;
  });

  
  clearSearch(): void {
    this.searchQuery.set('');
  }

  
  openConversation(conversation: ConversationSummary): void {
    this.conversationsStore.selectConversation(conversation.id);
    this.router.navigateByUrl('/home');
  }

  openRenameConversationModal(conversation: ConversationSummary): void {
    this.renameConversationError.set(null);
    this.renameConversationId.set(conversation.id);
    this.renameConversationTitle.set(conversation.title?.trim() || '');
    this.isRenameConversationModalOpen.set(true);
    setTimeout(() => {
      const el = this.renameConversationInput?.nativeElement;
      if (!el) return;
      el.focus();
      const end = el.value.length;
      el.setSelectionRange(end, end);
    }, 0);
  }

  closeRenameConversationModal(): void {
    this.isRenameConversationModalOpen.set(false);
    this.renameConversationId.set(null);
    this.renameConversationTitle.set('');
    this.renameConversationError.set(null);
  }

  submitRenameConversation(): void {
    const conversationId = this.renameConversationId();
    if (!conversationId) {
      this.closeRenameConversationModal();
      return;
    }

    const newTitle = this.renameConversationTitle().trim();
    if (!newTitle) {
      this.renameConversationError.set('Informe o nome da conversa.');
      return;
    }

    const current =
      this.conversations().find((c) => c.id === conversationId)?.title?.trim() ||
      '';

    if (newTitle === current) {
      this.closeRenameConversationModal();
      return;
    }

    this.conversationsStore.renameConversation(conversationId, newTitle);
    this.closeRenameConversationModal();
  }

  deleteConversation(event: MouseEvent, conversation: ConversationSummary): void {
    event.stopPropagation();
    this.deleteConversationConfirm.open(conversation.id);
    this.closeConversationMenu();
  }



  
  formatDateLabel(epochMs: number): string {
    const raw = new Date(epochMs).toLocaleDateString('pt-BR', {
      day: 'numeric',
      month: 'short',
    });
    const monthNoDot = raw.replace('.', '');
    return monthNoDot.replace(/^(\d+)\s+de\s+(.+)$/i, '$1 de $2');
  }
}
