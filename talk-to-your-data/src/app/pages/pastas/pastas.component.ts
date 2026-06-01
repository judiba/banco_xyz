
import { CommonModule } from '@angular/common';
import {
  Component,
  ElementRef,
  HostListener,
  ViewChild,
  computed,
  inject,
  signal,
} from '@angular/core';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { ConversationsStore } from '../../shared/conversations.store';
import { DeleteConversationConfirmService } from '../../shared/delete-conversation-confirm.service';
import { type FolderItem } from '../../shared/folders.store';
import { FoldersStore } from '../../shared/folders.store';
import { slugify } from '../../shared/slug.util';

/**
 * PASTAS PAGE
 * - Lista pastas e quantidade de conversas
 * - Permite criar / renomear / excluir pastas
 * - Navega para a tela "dentro da pasta"
 */

/** VIEW MODEL: item da UI (Folder + contador de conversas) */
type FolderCardItem = FolderItem & {
  conversationsCount: number;
};

@Component({
  selector: 'app-pastas',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './pastas.component.html',
  styleUrl: './pastas.component.scss',
})
export class PastasComponent {
  // ROUTING
  private readonly router = inject(Router);

  // STORES/SERVICES
  private readonly conversationsStore = inject(ConversationsStore);
  private readonly foldersStore = inject(FoldersStore);
  private readonly deleteConfirm = inject(DeleteConversationConfirmService);

  // VIEWCHILD: inputs dos modais (criar/renomear)
  @ViewChild('createFolderInput')
  private createFolderInput?: ElementRef<HTMLInputElement>;

  @ViewChild('renameFolderInput')
  private renameFolderInput?: ElementRef<HTMLInputElement>;
  // MENU: controle do "menu de ações" por pasta (3 pontinhos)
  readonly openedFolderMenuId = signal<string | null>(null);

  isFolderMenuOpen(folderId: string): boolean {
    return this.openedFolderMenuId() === folderId;
  }

  toggleFolderMenu(folderId: string, event: MouseEvent): void {
    event.stopPropagation();
    this.openedFolderMenuId.update((current) =>
      current === folderId ? null : folderId,
    );
  }

  closeFolderMenu(): void {
    this.openedFolderMenuId.set(null);
  }

  // GLOBAL EVENTS: fecha menus/modais ao clicar fora ou apertar ESC
  @HostListener('document:click')
  onDocumentClick(): void {
    this.closeFolderMenu();
  }

  @HostListener('document:keydown.escape')
  onDocumentEscape(): void {
    this.closeFolderMenu();
    this.closeRenameFolderModal();
  }
  // MODAL: renomear pasta
  readonly isRenameFolderModalOpen = signal(false);
  readonly renameFolderName = signal('');
  readonly renameFolderError = signal<string | null>(null);
  private renameFolderTargetId: string | null = null;

  // STORE DATA: lista base de pastas
  readonly folders = this.foldersStore.folders;

  // COMPUTED: pastas com contador de conversas
  readonly foldersWithCounts = computed<FolderCardItem[]>(() => {
    const conversations = this.conversationsStore.conversations();
    return this.folders().map((f) => ({
      ...f,
      conversationsCount: conversations.filter((c) => c.folderId === f.id).length,
    }));
  });

  // SEARCH: filtro por nome da pasta
  readonly searchQuery = signal('');

  // UTIL: normaliza texto para comparação (lowercase + sem acento)
  private normalizeSearchText(value: string | null | undefined): string {
    return (value ?? '')
      .trim()
      .toLowerCase()
      .normalize('NFD')
      .replace(/[\u0300-\u036f]/g, '');
  }

  // COMPUTED: aplica filtro de busca em cima das pastas
  readonly filteredFolders = computed(() => {
    const q = this.normalizeSearchText(this.searchQuery());
    const list = this.foldersWithCounts();
    if (!q) return list;
    return list.filter((f) => this.normalizeSearchText(f.name).includes(q));
  });
  // MODAL: criar nova pasta
  readonly isCreateFolderModalOpen = signal(false);
  readonly newFolderName = signal('');
  readonly createFolderError = signal<string | null>(null);
  readonly showCreateFolderInfo = signal(true);

  // UI ACTION: abre modal de criação (atalho usado no template)
  createFolder(): void {
    this.openCreateFolderModal();
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
  }

  submitCreateFolder(): void {
    const name = this.newFolderName().trim();
    if (!name) {
      this.createFolderError.set('Informe o nome da pasta.');
      return;
    }

    this.foldersStore.createFolder(name, {
      onSuccess: () => this.closeCreateFolderModal(),
      onError: (message) => this.createFolderError.set(message),
    });
  }

  // NAVIGATION: abre uma pasta (rota com slug)
  openFolder(folder: FolderCardItem): void {
    const slug = slugify(folder.name) || folder.id;
    this.router.navigateByUrl(`/home/pastas/${slug}`);
  }
  openRenameFolderModal(folder: FolderCardItem, event: MouseEvent): void {
    event.stopPropagation();
    this.closeFolderMenu();

    this.renameFolderTargetId = folder.id;
    this.renameFolderName.set(folder.name);
    this.renameFolderError.set(null);
    this.isRenameFolderModalOpen.set(true);

    setTimeout(() => this.renameFolderInput?.nativeElement?.focus(), 0);
  }

  closeRenameFolderModal(): void {
    this.isRenameFolderModalOpen.set(false);
    this.renameFolderTargetId = null;
  }

  submitRenameFolder(): void {
    const targetId = this.renameFolderTargetId;
    if (!targetId) return;

    const next = this.renameFolderName().trim();
    if (!next) {
      this.renameFolderError.set('Informe o nome da pasta.');
      return;
    }

    const ok = this.foldersStore.renameFolder(targetId, next);
    if (!ok) {
      this.renameFolderError.set(
        'Não foi possível renomear (nome inválido, duplicado, ou pasta inexistente).',
      );
      return;
    }

    this.closeRenameFolderModal();
  }

  // DELETE: confirma exclusão (pasta + conversas dentro dela)
  confirmDeleteFolder(folder: FolderCardItem, event: MouseEvent): void {
    event.stopPropagation();
    this.closeFolderMenu();

    this.deleteConfirm.openWithCallback({
      title: 'Excluir pasta?',
      text: 'Esta ação não pode ser desfeita.',
      warningText:
        'Ao excluir esta pasta, todas as conversas contidas nela também serão removidas permanentemente,\nsem possibilidade de recuperação após a confirmação.',
      onConfirm: () => {
        const conversations = this.conversationsStore.conversations();
        for (const c of conversations) {
          if (c.folderId === folder.id) {
            this.conversationsStore.removeConversationFromList(c.id);
          }
        }
        this.foldersStore.deleteFolder(folder.id);
      },
    });
  }
}
