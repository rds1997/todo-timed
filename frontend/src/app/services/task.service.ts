import { HttpClient } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';
import {
  CreateTaskPayload,
  TodoTask,
  UpdateTaskPayload,
} from '../models/todo-task';

@Injectable({ providedIn: 'root' })
export class TaskService {
  private readonly http = inject(HttpClient);
  private readonly baseUrl = `${environment.apiBaseUrl}/api/tasks`;

  getAll(): Observable<TodoTask[]> {
    return this.http.get<TodoTask[]>(this.baseUrl);
  }

  create(payload: CreateTaskPayload): Observable<TodoTask> {
    return this.http.post<TodoTask>(this.baseUrl, payload);
  }

  update(id: string, payload: UpdateTaskPayload): Observable<TodoTask> {
    return this.http.put<TodoTask>(`${this.baseUrl}/${id}`, payload);
  }

  delete(id: string): Observable<void> {
    return this.http.delete<void>(`${this.baseUrl}/${id}`);
  }
}
