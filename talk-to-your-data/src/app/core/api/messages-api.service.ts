import { HttpClient } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';
import { ApiConfig } from './api-config.service';
import { FeedbackRequest, FeedbackResponse } from './api.types';

@Injectable({ providedIn: 'root' })
export class MessagesApiService {
  private readonly http = inject(HttpClient);
  private readonly urls = inject(ApiConfig);

  setFeedback(
    messageId: string,
    feedback: FeedbackRequest['feedback'],
  ): Observable<FeedbackResponse> {
    return this.http.put<FeedbackResponse>(this.urls.messages.feedback(messageId), {
      feedback,
    });
  }
}
