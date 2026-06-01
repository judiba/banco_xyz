import { HttpClient, HttpParams } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';
import { ApiConfig } from './api-config.service';
import { Folder, FoldersListResponse } from './api.types';

@Injectable({ providedIn: 'root' })
export class FoldersApiService {
  private readonly http = inject(HttpClient);
  private readonly urls = inject(ApiConfig);

  list(q?: string): Observable<FoldersListResponse> {
    let params = new HttpParams();
    if (q) {
      params = params.set('q', q);
    }
    return this.http.get<FoldersListResponse>(this.urls.folders.list(), { params });
  }

  getById(id: string): Observable<Folder> {
    return this.http.get<Folder>(this.urls.folders.one(id));
  }

  getBySlug(slug: string): Observable<Folder> {
    return this.http.get<Folder>(this.urls.folders.bySlug(slug));
  }

  create(name: string): Observable<Folder> {
    return this.http.post<Folder>(this.urls.folders.create(), { name: name.trim() });
  }

  patch(id: string, name: string): Observable<Folder> {
    return this.http.patch<Folder>(this.urls.folders.patch(id), { name: name.trim() });
  }

  delete(id: string, cascade = true): Observable<void> {
    return this.http.delete<void>(this.urls.folders.delete(id, cascade));
  }
}
