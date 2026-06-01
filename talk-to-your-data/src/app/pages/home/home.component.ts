
/**
 * HOME PAGE (SHELL)
 * - Tela principal após login, contendo layout base (sidebar + área de conteúdo)
 * - Orquestra ações de conversas (criar/abrir/renomear/deletar/mover para pasta)
 */
import { CommonModule } from '@angular/common';
import {
  Component,
  ElementRef,
  HostListener,
  OnInit,
  ViewChild,
  computed,
  inject,
  signal,
} from '@angular/core';
import { FormsModule } from '@angular/forms';
import { Router, RouterOutlet } from '@angular/router';

import { AuthService } from '../../core/auth/auth.service';
import { SessionInitService } from '../../core/session/session-init.service';
import { DeleteConversationConfirmService } from '../../shared/delete-conversation-confirm.service';
import { FoldersStore } from '../../shared/folders.store';

import {
  ConversationsStore,
  type ConversationSummary,
} from '../../shared/conversations.store';

@Component({
  selector: 'app-home',
  standalone: true,
  imports: [CommonModule, RouterOutlet, FormsModule],
  templateUrl: './home.component.html',
  styleUrl: './home.component.scss',
})
export class HomeComponent implements OnInit {
  // ROUTING
  readonly router = inject(Router);
  private readonly auth = inject(AuthService);
  private readonly sessionInit = inject(SessionInitService);

  // MODAL INPUT REFS (para foco automático)
  @ViewChild('createFolderInput')
  private createFolderInput?: ElementRef<HTMLInputElement>;

  @ViewChild('renameConversationInput')
  private renameConversationInput?: ElementRef<HTMLInputElement>;

  // STORES (estado e ações da aplicação)
  readonly conversationsStore = inject(ConversationsStore);
  private readonly foldersStore = inject(FoldersStore);

  // SERVICES (UI / confirmação)
  private readonly deleteConversationConfirm = inject(
    DeleteConversationConfirmService,
  );

  // SIDEBAR (estado do menu lateral)
  readonly isSidebarCollapsed = signal(true);

  // USER
  readonly userDisplayName = computed(() => this.auth.getDisplayName());

  // CONVERSATIONS (sidebar — apenas sem pasta)
  readonly conversations = this.conversationsStore.conversationsWithoutFolder;

  // CONVERSATION MENU (menu de 3 pontos por conversa)
  readonly openedConversationMenuId = signal<string | null>(null);
  readonly openedConversationMenuPos = signal<
    | {
        top: number;
        left: number;
      }
    | null
  >(null);
  readonly openedConversationMenuConversation =
    signal<ConversationSummary | null>(null);

  // FOLDERS (lista de pastas)
  readonly folders = this.foldersStore.folders;

  // CREATE FOLDER MODAL
  readonly isCreateFolderModalOpen = signal(false);
  readonly newFolderName = signal('');
  readonly createFolderError = signal<string | null>(null);
  readonly showCreateFolderInfo = signal(true);

  // MOVE TO FOLDER (quando cria pasta a partir do menu "mover")
  readonly createFolderMoveConversationId = signal<string | null>(null);
  readonly openedMoveToFolderMenuPos = signal<
    | {
        top: number;
        left: number;
      }
    | null
  >(null);

  // RENAME CONVERSATION MODAL
  readonly isRenameConversationModalOpen = signal(false);
  readonly renameConversationId = signal<string | null>(null);
  readonly renameConversationTitle = signal('');
  readonly renameConversationError = signal<string | null>(null);

  // TIMER (fechamento atrasado do menu "mover para pasta" para permitir hover)
  private moveToFolderCloseTimer: number | null = null;

  readonly sessionLoading = this.sessionInit.isLoading;

  ngOnInit(): void {
    if (!this.sessionInit.hasInitialized) {
      this.sessionInit.ensureSession().subscribe();
    }
  }

  // (NÃO USADO AINDA) estado para edição inline
  readonly editingConversationId = signal<string | null>(null);
  readonly editedConversationTitle = signal('');

  
  // SIDEBAR
  toggleSidebar(): void {
    this.isSidebarCollapsed.update((v) => !v);
  }

  closeSidebar(): void {
    this.isSidebarCollapsed.set(true);
  }

  private closeSidebarOnMobile(): void {
    if (typeof window !== 'undefined' && window.matchMedia('(max-width: 991px)').matches) {
      this.closeSidebar();
    }
  }

  // CONVERSATIONS - criar e navegar (conversa criada no backend na 1ª mensagem)
  newConversation(): void {
    this.conversationsStore.startNewConversation();
    this.closeSidebarOnMobile();
    this.router.navigateByUrl('/home');
  }

  // CONVERSATIONS - abrir conversa existente
  openConversation(conversation: ConversationSummary): void {
    this.closeConversationMenu();

    this.conversationsStore.selectConversation(conversation.id);
    this.closeSidebarOnMobile();
    this.router.navigateByUrl('/home');
  }

  
  // CONVERSATION MENU (3 pontos) - abrir/fechar e posicionar
  toggleConversationMenu(event: MouseEvent, conversationId: string): void {
    event.stopPropagation();

    const isClosing = this.openedConversationMenuId() === conversationId;
    if (isClosing) {
      this.closeConversationMenu();
      (event.currentTarget as HTMLButtonElement | null)?.blur();
      return;
    }

    // UI POSICIONAMENTO (evita estourar viewport)
    const gap = 12;
    const menuWidth = 240;
    const menuHeight = 190;

    let left = event.clientX + gap;
    if (left + menuWidth > window.innerWidth - 8) {
      left = event.clientX - menuWidth - gap;
    }
    left = Math.max(8, left);

    let top = event.clientY - 12;
    if (top + menuHeight > window.innerHeight - 8) {
      top = window.innerHeight - menuHeight - 8;
    }
    top = Math.max(8, top);

    const conversation =
      this.conversations().find((c) => c.id === conversationId) ?? null;

    this.openedConversationMenuId.set(conversationId);
    this.openedConversationMenuPos.set({ top, left });
    this.openedConversationMenuConversation.set(conversation);
  }

  
  // CONVERSATION MENU - fechar e limpar estado
  closeConversationMenu(): void {
    this.openedConversationMenuId.set(null);
    this.openedConversationMenuPos.set(null);
    this.openedConversationMenuConversation.set(null);
    this.closeMoveToFolderMenu();
  }

  // GLOBAL CLICK - fecha menus abertos ao clicar fora
  @HostListener('document:click')
  onDocumentClick(): void {
    this.closeConversationMenu();
  }

  // RENAME - ação iniciada no menu da conversa
  renameConversation(event: MouseEvent, conversation: ConversationSummary): void {
    event.stopPropagation();

    this.openRenameConversationModal(conversation);
    this.closeConversationMenu();
  }

  // RENAME MODAL - abrir e focar input
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

  // RENAME MODAL - validar e persistir novo título
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

  
  // MOVE TO FOLDER MENU - abrir/posicionar (submenu do menu de conversa)
  openMoveToFolderMenu(event: MouseEvent): void {
    event.stopPropagation();
    this.cancelCloseMoveToFolderMenu();

    const el = event.currentTarget as HTMLElement | null;
    if (!el) return;

    const rect = el.getBoundingClientRect();

    const menuWidth = 260;
    const menuHeight = 240;
    const gap = 10;

    let left = rect.right + gap;
    if (left + menuWidth > window.innerWidth - 8) {
      left = rect.left - menuWidth - gap;
    }
    left = Math.max(8, left);

    let top = rect.top - 8;
    if (top + menuHeight > window.innerHeight - 8) {
      top = window.innerHeight - menuHeight - 8;
    }
    top = Math.max(8, top);

    this.openedMoveToFolderMenuPos.set({ top, left });
  }

  // MOVE TO FOLDER MENU - fecha com atraso (permite mover mouse para o submenu)
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

  // MOVE TO FOLDER - persistir folderId na conversa
  moveConversationToFolderId(conversationId: string, folderId: string): void {
    this.conversationsStore.setConversationFolder(conversationId, folderId);
    this.closeConversationMenu();
  }

  // CREATE FOLDER (a partir do menu "mover para pasta")
  createFolderFromMoveMenu(conversation: ConversationSummary): void {
    this.createFolderMoveConversationId.set(conversation.id);
    this.openCreateFolderModal();
    this.closeConversationMenu();
  }

  // CREATE FOLDER MODAL - abrir e focar input
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

  // CREATE FOLDER MODAL - validar e criar pasta (opcionalmente move conversa)
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
      onError: (message) => {
        this.createFolderError.set(message);
      },
    });
  }

  
  // DELETE (com confirmação)
  deleteConversation(event: MouseEvent, conversation: ConversationSummary): void {
    event.stopPropagation();

    this.deleteConversationConfirm.open(conversation.id);
    this.closeConversationMenu();
  }

  // NAVIGATION (atalhos do header/sidebar)
  goToHomeChat(): void {
    this.router.navigateByUrl('/home');
  }

  goToConversationSearch(): void {
    this.closeSidebarOnMobile();
    this.router.navigateByUrl('/home/buscar-conversas');
  }

  goToPastas(): void {
    this.closeSidebarOnMobile();
    this.router.navigateByUrl('/home/pastas');
  }

  
  // UTIL - formatação de data para label "3 de abr"
  formatDateLabel(epochMs: number): string {
    const raw = new Date(epochMs).toLocaleDateString('pt-BR', {
      day: 'numeric',
      month: 'short',
    });

    const monthNoDot = raw.replace('.', '');
    return monthNoDot.replace(/^(\d+)\s+de\s+(.+)$/i, '$1 de $2');
  }

  // AUTH - sair (volta para login)
  logout(): void {
    this.sessionInit.reset();
    this.auth.logoutAndRedirect();
  }

}
