import { HttpClient, HttpParams } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';
import { ApiConfig } from './api-config.service';
import { BootstrapResponse } from './api.types';

@Injectable({ providedIn: 'root' })
export class SessionApiService {
  private readonly http = inject(HttpClient);
  private readonly urls = inject(ApiConfig);

  getBootstrap(page = 1, pageSize = 50): Observable<BootstrapResponse> {
    const params = new HttpParams()
      .set('page', String(page))
      .set('pageSize', String(pageSize))
      .set('sort', 'lastUpdatedAt')
      .set('order', 'desc');

    return this.http.get<BootstrapResponse>(this.urls.session.bootstrap(), { params });
  }
}
