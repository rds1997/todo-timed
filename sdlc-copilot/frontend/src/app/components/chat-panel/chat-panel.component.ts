import { CommonModule } from '@angular/common';
import { Component, Input, OnChanges, SimpleChanges, ViewChild, ElementRef, inject } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { MatButtonModule } from '@angular/material/button';
import { MatCardModule } from '@angular/material/card';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatIconModule } from '@angular/material/icon';
import { MatInputModule } from '@angular/material/input';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';

import { ChatMessage } from '../../core/models/requirement.models';
import { RequirementService } from '../../core/services/requirement.service';

@Component({
  selector: 'app-chat-panel',
  standalone: true,
  imports: [
    CommonModule, FormsModule, MatCardModule, MatFormFieldModule, MatInputModule,
    MatButtonModule, MatIconModule, MatProgressSpinnerModule,
  ],
  template: `
    <mat-card class="chat-card">
      <mat-card-header>
        <mat-card-title><mat-icon>forum</mat-icon> Ask the assistant</mat-card-title>
      </mat-card-header>
      <mat-card-content>
        <div class="chat-window" #scroller>
          <div *ngFor="let m of messages" class="msg" [class.user]="m.role === 0" [class.assistant]="m.role === 1">
            <div class="bubble">
              <div class="who">{{ m.role === 0 ? 'You' : 'Assistant' }}</div>
              <div class="content">{{ m.content }}</div>
            </div>
          </div>
          <div *ngIf="!messages.length" class="empty-state">
            <mat-icon>chat</mat-icon>
            <p>Ask anything about this requirement. The assistant has the full text in context.</p>
          </div>
        </div>
        <form (ngSubmit)="send()" class="composer">
          <mat-form-field appearance="outline" class="grow">
            <mat-label>Your message</mat-label>
            <input matInput [(ngModel)]="draft" name="draft"
                   placeholder="What are the biggest risks here?" />
          </mat-form-field>
          <button mat-flat-button color="primary" type="submit"
                  [disabled]="!draft.trim() || sending">
            <mat-icon *ngIf="!sending">send</mat-icon>
            <mat-spinner *ngIf="sending" diameter="22"></mat-spinner>
          </button>
        </form>
      </mat-card-content>
    </mat-card>
  `,
  styles: [`
    .chat-card { display: flex; flex-direction: column; min-height: 480px; }
    .chat-window {
      flex: 1; min-height: 280px; max-height: 420px; overflow-y: auto;
      padding: 8px 4px; display: flex; flex-direction: column; gap: 10px;
    }
    .msg { display: flex; }
    .msg.user { justify-content: flex-end; }
    .bubble {
      max-width: 80%;
      padding: 10px 14px;
      border-radius: 14px;
      background: #f4f5f9;
      box-shadow: 0 1px 2px rgba(0,0,0,0.04);
    }
    .msg.user .bubble {
      background: #e8eaf6;
    }
    .who { font-size: 0.75rem; color: rgba(0,0,0,0.55); margin-bottom: 4px; font-weight: 600; }
    .content { white-space: pre-wrap; line-height: 1.4; }
    .composer { display: flex; gap: 12px; margin-top: 12px; align-items: flex-start; }
    .grow { flex: 1; }
  `],
})
export class ChatPanelComponent implements OnChanges {
  private service = inject(RequirementService);

  @Input() requirementId!: string;
  @ViewChild('scroller') scroller?: ElementRef<HTMLDivElement>;

  messages: ChatMessage[] = [];
  draft = '';
  sending = false;

  ngOnChanges(changes: SimpleChanges): void {
    if (changes['requirementId'] && this.requirementId) {
      this.loadHistory();
    }
  }

  private loadHistory(): void {
    this.service.chatHistory(this.requirementId).subscribe({
      next: msgs => { this.messages = msgs; this.scrollSoon(); },
      error: () => { /* ignore for hackathon scope */ },
    });
  }

  send(): void {
    if (!this.draft.trim() || this.sending) return;
    const text = this.draft.trim();
    this.sending = true;
    this.draft = '';
    this.service.sendChat(this.requirementId, text).subscribe({
      next: turn => {
        this.messages = [...this.messages, turn.userMessage, turn.assistantMessage];
        this.sending = false;
        this.scrollSoon();
      },
      error: () => { this.sending = false; },
    });
  }

  private scrollSoon(): void {
    setTimeout(() => {
      if (this.scroller) {
        this.scroller.nativeElement.scrollTop = this.scroller.nativeElement.scrollHeight;
      }
    }, 50);
  }
}
