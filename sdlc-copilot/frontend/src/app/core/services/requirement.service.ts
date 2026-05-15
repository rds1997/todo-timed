import { HttpClient } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';

import { environment } from '../../../environments/environment';
import {
  ChatMessage, ChatTurn, RequirementDetail, RequirementSummary,
} from '../models/requirement.models';

@Injectable({ providedIn: 'root' })
export class RequirementService {
  private http = inject(HttpClient);
  private base = `${environment.apiBaseUrl}/api/v1/requirements`;

  list(): Observable<RequirementSummary[]> {
    return this.http.get<RequirementSummary[]>(this.base);
  }

  get(id: string): Observable<RequirementDetail> {
    return this.http.get<RequirementDetail>(`${this.base}/${id}`);
  }

  ingestText(title: string, text: string): Observable<RequirementSummary> {
    return this.http.post<RequirementSummary>(this.base, { title, text });
  }

  ingestFile(file: File, title: string): Observable<RequirementSummary> {
    const fd = new FormData();
    fd.append('file', file);
    if (title) fd.append('title', title);
    return this.http.post<RequirementSummary>(`${this.base}/upload`, fd);
  }

  analyze(id: string): Observable<RequirementDetail> {
    return this.http.post<RequirementDetail>(`${this.base}/${id}/analyze`, {});
  }

  delete(id: string): Observable<void> {
    return this.http.delete<void>(`${this.base}/${id}`);
  }

  chatHistory(id: string): Observable<ChatMessage[]> {
    return this.http.get<ChatMessage[]>(`${this.base}/${id}/chat`);
  }

  sendChat(id: string, message: string): Observable<ChatTurn> {
    return this.http.post<ChatTurn>(`${this.base}/${id}/chat`, { message });
  }

  exportMarkdownUrl(id: string): string {
    return `${this.base}/${id}/export.md`;
  }

  exportJsonUrl(id: string): string {
    return `${this.base}/${id}/export.json`;
  }

  exportCsvUrl(id: string): string {
    return `${this.base}/${id}/export.csv`;
  }
}
