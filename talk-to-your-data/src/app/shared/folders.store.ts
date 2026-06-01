import { Injectable, inject, signal } from '@angular/core';
import { getApiErrorMessage } from '../core/api/api-error.util';
import { FoldersApiService } from '../core/api/folders-api.service';
import type { Folder } from '../core/api/api.types';
import { slugify } from './slug.util';

export type FolderItem = Pick<Folder, 'id' | 'name'> & { slug?: string };

@Injectable({ providedIn: 'root' })
export class FoldersStore {
  private readonly api = inject(FoldersApiService);

  private readonly _folders = signal<FolderItem[]>([]);

  readonly folders = this._folders.asReadonly();

  hydrate(folders: Folder[]): void {
    this._folders.set(
      folders.map((f) => ({ id: f.id, name: f.name, slug: f.slug })),
    );
  }

  createFolder(
    name: string,
    callbacks?: {
      onSuccess?: (folder: FolderItem) => void;
      onError?: (message: string) => void;
    },
  ): void {
    const n = name.trim();
    if (!n) return;

    const nSlug = slugify(n);
    const exists = this._folders().some((f) => slugify(f.name) === nSlug);
    if (exists) {
      callbacks?.onError?.(
        'Não foi possível criar a pasta (nome inválido ou duplicado).',
      );
      return;
    }

    this.api.create(n).subscribe({
      next: (folder) => {
        const item: FolderItem = {
          id: folder.id,
          name: folder.name,
          slug: folder.slug,
        };
        this._folders.update((list) => [...list, item]);
        callbacks?.onSuccess?.(item);
      },
      error: (err) => {
        callbacks?.onError?.(
          getApiErrorMessage(err, 'Não foi possível criar a pasta.'),
        );
      },
    });
  }

  renameFolder(folderId: string, nextName: string, onError?: (message: string) => void): boolean {
    const n = nextName.trim();
    if (!n) return false;

    const nSlug = slugify(n);
    const exists = this._folders().some(
      (f) => f.id !== folderId && slugify(f.name) === nSlug,
    );
    if (exists) {
      onError?.('Não foi possível renomear (nome inválido, duplicado, ou pasta inexistente).');
      return false;
    }

    this.api.patch(folderId, n).subscribe({
      next: (folder) => {
        this._folders.update((list) =>
          list.map((f) =>
            f.id === folderId
              ? { id: folder.id, name: folder.name, slug: folder.slug }
              : f,
          ),
        );
      },
      error: (err) => {
        onError?.(getApiErrorMessage(err, 'Não foi possível renomear a pasta.'));
      },
    });

    return true;
  }

  deleteFolder(folderId: string): void {
    this.api.delete(folderId, true).subscribe({
      next: () => {
        this._folders.update((list) => list.filter((f) => f.id !== folderId));
      },
      error: (err) => console.error('[folders] delete', getApiErrorMessage(err)),
    });
  }

  addFolder(folder: FolderItem): void {
    this._folders.update((list) => {
      if (list.some((f) => f.id === folder.id)) return list;
      return [...list, folder];
    });
  }

  resolveFolder(idOrSlug: string) {
    const isUuid = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i.test(
      idOrSlug,
    );
    return isUuid ? this.api.getById(idOrSlug) : this.api.getBySlug(idOrSlug);
  }

  clear(): void {
    this._folders.set([]);
  }
}
