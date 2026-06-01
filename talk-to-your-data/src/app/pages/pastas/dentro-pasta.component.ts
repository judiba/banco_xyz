
import { CommonModule } from '@angular/common';
import {
  Component,
  DestroyRef,
  ElementRef,
  HostListener,
  ViewChild,
  computed,
  inject,
  signal,
} from '@angular/core';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { FormsModule } from '@angular/forms';
import { ActivatedRoute, Router } from '@angular/router';
import { jsPDF } from 'jspdf';
import {
  buildConversationExportTxt,
  renderConversationExportPdf,
} from '../../shared/conversation-export.util';
import { AuthService } from '../../core/auth/auth.service';
import { DeleteConversationConfirmService } from '../../shared/delete-conversation-confirm.service';
import {
  ConversationsStore,
  type ChatMessage,
  type ConversationSummary,
} from '../../shared/conversations.store';
import { FoldersStore } from '../../shared/folders.store';
import { slugify } from '../../shared/slug.util';

type FolderEntryView = {
  id: string;
  title: string;
  description: string;
  lastUpdatedAt: number; // epoch ms
};

@Component({
  selector: 'app-dentro-pasta',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './dentro-pasta.component.html',
  styleUrl: './dentro-pasta.component.scss',
})
export class DentroPastaComponent {
  private readonly route = inject(ActivatedRoute);
  private readonly router = inject(Router);
  private readonly destroyRef = inject(DestroyRef);
  private readonly conversationsStore = inject(ConversationsStore);
  private readonly foldersStore = inject(FoldersStore);
  private readonly deleteConversationConfirm = inject(
    DeleteConversationConfirmService,
  );
  private readonly auth = inject(AuthService);

  @ViewChild('createFolderInput')
  private createFolderInput?: ElementRef<HTMLInputElement>;

  
  readonly folderParam = signal<string>('');

  
  readonly folder = computed(() => {
    const param = this.folderParam();

    if (!param) return undefined;

    const folders = this.foldersStore.folders();
    const byId = folders.find((f) => f.id === param);
    if (byId) return byId;
    return folders.find((f) => slugify(f.name) === param);
  });

  
  readonly folderId = computed(() => this.folder()?.id ?? this.folderParam());

  readonly folderName = computed(() => this.folder()?.name ?? 'Pasta');

  readonly searchQuery = signal('');

  
  readonly openedEntryMenuId = signal<string | null>(null);

  
  readonly openedEntryMenuPos = signal<{ top: number; left: number } | null>(
    null,
  );

  
  readonly openedEntryMenuConversation = signal<ConversationSummary | null>(null);

  
  readonly folders = this.foldersStore.folders;

  
  readonly openedMoveToFolderMenuPos = signal<
    | {
        top: number;
        left: number;
      }
    | null
  >(null);

  private moveToFolderCloseTimer: number | null = null;
  readonly isCreateFolderModalOpen = signal(false);
  readonly newFolderName = signal('');
  readonly createFolderError = signal<string | null>(null);
  readonly showCreateFolderInfo = signal(true);

  
  readonly createFolderMoveConversationId = signal<string | null>(null);

  readonly userName = () => this.auth.getDisplayName();
  readonly assistantName = () => this.auth.assistantDisplayName();

  readonly isExportModalOpen = signal(false);
  readonly exportFormat = signal<'pdf' | 'txt' | null>(null);

  
  readonly exportConversation = signal<ConversationSummary | null>(null);

  readonly entries = computed<FolderEntryView[]>(() => {
    const folderId = this.folderId();
    const list = this.conversationsStore.conversations();

    return list
      .filter((c) => c.folderId === folderId)
      .map((c) => ({
        id: c.id,
        title: c.title,
        description: c.description ?? '',
        lastUpdatedAt: c.lastUpdatedAt,
      }))
      .sort((a, b) => b.lastUpdatedAt - a.lastUpdatedAt);
  });

  readonly filteredEntries = computed(() => {
    const q = this.searchQuery().trim().toLowerCase();
    const list = this.entries();
    if (!q) return list;

    return list.filter((e) => {
      const haystack = `${e.title} ${e.description}`.toLowerCase();
      return haystack.includes(q);
    });
  });

  
  readonly searchResultsCount = computed(() => this.filteredEntries().length);

  constructor() {
    this.route.paramMap
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe((params) => {
        const param = params.get('id') ?? '';
        this.folderParam.set(param);
      });
  }
  openEntry(entry: FolderEntryView): void {
    this.closeEntryMenu();

    this.conversationsStore.selectConversation(entry.id);
    this.router.navigateByUrl('/home');
  }

  
  toggleEntryMenu(event: MouseEvent, conversationId: string): void {
    event.stopPropagation();
    event.preventDefault();

    const isClosing = this.openedEntryMenuId() === conversationId;

    if (isClosing) {
      this.closeEntryMenu();
      (event.currentTarget as HTMLButtonElement | null)?.blur();
      return;
    }

    const gap = 12;
    const menuWidth = 200;
    const menuHeight = 240;

    let left = event.clientX - menuWidth - gap;
    if (left < 8) {
      left = event.clientX + gap;
    }

    left = Math.max(8, left);

    let top = event.clientY - 12;
    if (top + menuHeight > window.innerHeight - 8) {
      top = window.innerHeight - menuHeight - 8;
    }
    top = Math.max(8, top);

    const conversation =
      this.conversationsStore.conversations().find((c) => c.id === conversationId) ??
      null;

    this.openedEntryMenuId.set(conversationId);
    this.openedEntryMenuPos.set({ top, left });
    this.openedEntryMenuConversation.set(conversation);
  }

  closeEntryMenu(): void {
    this.openedEntryMenuId.set(null);
    this.openedEntryMenuPos.set(null);
    this.openedEntryMenuConversation.set(null);
    this.closeMoveToFolderMenu();
  }

  
  @HostListener('document:click')
  onDocumentClick(): void {
    this.closeEntryMenu();
  }

  readonly isRenameConversationModalOpen = signal(false);
  readonly renameConversationTitle = signal('');
  readonly renameConversationError = signal<string | null>(null);
  readonly renameConversationConversationId = signal<string | null>(null);

  @ViewChild('renameConversationInput')
  private renameConversationInput?: ElementRef<HTMLInputElement>;

  renameConversation(event: MouseEvent, conversation: ConversationSummary): void {
    event.stopPropagation();
    event.preventDefault();

    this.renameConversationError.set(null);
    this.renameConversationConversationId.set(conversation.id);
    this.renameConversationTitle.set(conversation.title ?? '');
    this.isRenameConversationModalOpen.set(true);
    this.closeEntryMenu();

    setTimeout(() => this.renameConversationInput?.nativeElement?.focus(), 0);
  }

  closeRenameConversationModal(): void {
    this.isRenameConversationModalOpen.set(false);
    this.renameConversationError.set(null);
    this.renameConversationConversationId.set(null);
  }

  submitRenameConversation(): void {
    const id = this.renameConversationConversationId();
    const title = this.renameConversationTitle().trim();

    if (!id) {
      this.renameConversationError.set('Conversa inválida.');
      return;
    }

    if (!title) {
      this.renameConversationError.set('Informe o nome da conversa.');
      return;
    }

    this.conversationsStore.renameConversation(id, title);
    this.closeRenameConversationModal();
  }

  deleteConversation(event: MouseEvent, conversation: ConversationSummary): void {
    event.stopPropagation();
    this.deleteConversationConfirm.open(conversation.id);
    this.closeEntryMenu();
  }

  openMoveToFolderMenu(event: MouseEvent): void {
    event.stopPropagation();
    this.cancelCloseMoveToFolderMenu();

    const el = event.currentTarget as HTMLElement | null;
    if (!el) return;
    const mainPos = this.openedEntryMenuPos();
    if (!mainPos) return;
    const menuWidth = 192;
    const menuHeight = 240;
    const gap = 1;

    const mainMenuWidth = 200;
    let left = mainPos.left + mainMenuWidth + gap;
    if (left + menuWidth > window.innerWidth - 8) {
      left = mainPos.left - menuWidth - gap;
    }

    left = Math.max(8, left);


    const triggerRect = el.getBoundingClientRect();
    const triggerTop = triggerRect.top;

    const submenuContainerPaddingTop = 10;
    const submenuFirstItemPaddingTop = 10;

    let top =
      triggerTop - (submenuContainerPaddingTop + submenuFirstItemPaddingTop) + 10;

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
    this.closeEntryMenu();
  }

  createFolderFromMoveMenu(conversation: ConversationSummary): void {
    this.createFolderMoveConversationId.set(conversation.id);
    this.openCreateFolderModal();
    this.closeEntryMenu();
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

  openExportModalFromMenu(event: MouseEvent, conversation: ConversationSummary): void {
    event.stopPropagation();
    event.preventDefault();

    this.exportConversation.set(conversation);
    this.exportFormat.set(null);
    this.isExportModalOpen.set(true);
    this.closeEntryMenu();
  }

  closeExportModal(): void {
    this.isExportModalOpen.set(false);
    this.exportFormat.set(null);
    this.exportConversation.set(null);
  }

  selectExportFormat(format: 'pdf' | 'txt'): void {
    this.exportFormat.set(format);
  }

  confirmExport(): void {
    const format = this.exportFormat();
    const conversation = this.exportConversation();
    if (!format || !conversation) return;

    if (format === 'txt') {
      this.downloadConversationAsTxt(conversation);
    } else {
      this.downloadConversationAsPdf(conversation);
    }

    this.closeExportModal();
  }

  private downloadConversationAsTxt(conversation: ConversationSummary): void {
    const date = new Date();

    const meta = {
      userName: this.userName(),
      assistantName: this.assistantName(),
      conversationTitle: conversation.title || 'Novo chat',
      conversationDescription: conversation.description || '(sem descrição)',
      exportedAt: date,
    };

    const messages: ChatMessage[] = this.conversationsStore.getConversationMessages(
      conversation.id,
    );

    const content = buildConversationExportTxt(
      meta,
      messages.map((m) => ({
        role: m.role,
        content: m.content,
        createdAt: m.createdAt,
      })),
    );

    const blob = new Blob([content], { type: 'text/plain;charset=utf-8' });
    this.downloadBlob(blob, this.buildExportFileName(conversation, 'txt', date));
  }

  private downloadConversationAsPdf(conversation: ConversationSummary): void {
    const date = new Date();

    const meta = {
      userName: this.userName(),
      assistantName: this.assistantName(),
      conversationTitle: conversation.title || 'Novo chat',
      conversationDescription: conversation.description || '(sem descrição)',
      exportedAt: date,
    };

    const messages: ChatMessage[] = this.conversationsStore.getConversationMessages(
      conversation.id,
    );

    const doc = new jsPDF({
      orientation: 'p',
      unit: 'pt',
      format: 'a4',
    });

    renderConversationExportPdf(
      doc,
      meta,
      messages.map((m) => ({
        role: m.role,
        content: m.content,
        createdAt: m.createdAt,
      })),
    );

    doc.save(this.buildExportFileName(conversation, 'pdf', date));
  }

  private buildExportFileName(
    conversation: ConversationSummary,
    ext: 'txt' | 'pdf',
    date: Date,
  ): string {
    const title = conversation.title || 'novo-chat';
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

  
  formatDateLabel(epochMs: number): string {
    const raw = new Date(epochMs).toLocaleDateString('pt-BR', {
      day: 'numeric',
      month: 'short',
    });
    const monthNoDot = raw.replace('.', '');
    return monthNoDot.replace(/^(\d+)\s+de\s+(.+)$/i, '$1 de $2');
  }
}
