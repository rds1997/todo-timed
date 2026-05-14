import { CommonModule } from '@angular/common';
import { Component, OnInit, inject } from '@angular/core';
import { Router, RouterLink } from '@angular/router';
import { MatButtonModule } from '@angular/material/button';
import { MatCardModule } from '@angular/material/card';
import { MatChipsModule } from '@angular/material/chips';
import { MatIconModule } from '@angular/material/icon';
import { MatProgressBarModule } from '@angular/material/progress-bar';
import { MatTableModule } from '@angular/material/table';
import { MatTooltipModule } from '@angular/material/tooltip';
import { MatSnackBar } from '@angular/material/snack-bar';

import { UploadComponent } from '../../components/upload/upload.component';
import { RequirementService } from '../../core/services/requirement.service';
import { REQUIREMENT_STATUS_LABEL, RequirementSummary } from '../../core/models/requirement.models';

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [
    CommonModule, RouterLink, UploadComponent,
    MatCardModule, MatTableModule, MatIconModule, MatButtonModule,
    MatChipsModule, MatTooltipModule, MatProgressBarModule,
  ],
  template: `
    <h1 class="page-title"><mat-icon>dashboard</mat-icon> SDLC Copilot</h1>
    <p class="page-subtitle">
      Convert raw software requirements into structured SDLC artifacts —
      user stories, dev tasks, test cases, ambiguity findings, and effort estimates.
    </p>

    <div class="dash-grid">
      <app-upload (ingested)="onIngested($event)"></app-upload>

      <mat-card class="kpis">
        <mat-card-header>
          <mat-card-title><mat-icon>insights</mat-icon> Workspace</mat-card-title>
        </mat-card-header>
        <mat-card-content>
          <div class="card-grid">
            <div class="kpi-card">
              <span class="kpi-label">Requirements</span>
              <span class="kpi-value">{{ items.length }}</span>
              <span class="kpi-sub">across all statuses</span>
            </div>
            <div class="kpi-card">
              <span class="kpi-label">User stories</span>
              <span class="kpi-value">{{ totalStories }}</span>
            </div>
            <div class="kpi-card">
              <span class="kpi-label">Dev tasks</span>
              <span class="kpi-value">{{ totalTasks }}</span>
            </div>
            <div class="kpi-card">
              <span class="kpi-label">Test cases</span>
              <span class="kpi-value">{{ totalTests }}</span>
            </div>
          </div>
        </mat-card-content>
      </mat-card>
    </div>

    <div class="section">
      <h2><mat-icon>list_alt</mat-icon> Requirements</h2>
      <mat-card>
        <mat-progress-bar *ngIf="loading" mode="indeterminate"></mat-progress-bar>
        <div class="scroll-x">
          <table mat-table [dataSource]="items" *ngIf="items.length; else emptyTpl" class="reqs-table">
            <ng-container matColumnDef="title">
              <th mat-header-cell *matHeaderCellDef>Title</th>
              <td mat-cell *matCellDef="let r">
                <a [routerLink]="['/requirements', r.id]" class="title-link">
                  <strong>{{ r.title }}</strong>
                </a>
                <div class="muted" *ngIf="r.sourceFileName">{{ r.sourceFileName }}</div>
              </td>
            </ng-container>

            <ng-container matColumnDef="status">
              <th mat-header-cell *matHeaderCellDef>Status</th>
              <td mat-cell *matCellDef="let r">
                <mat-chip-set>
                  <mat-chip [color]="r.status === 2 ? 'primary' : r.status === 3 ? 'warn' : undefined" selected>
                    {{ statusLabel(r.status) }}
                  </mat-chip>
                </mat-chip-set>
              </td>
            </ng-container>

            <ng-container matColumnDef="stories">
              <th mat-header-cell *matHeaderCellDef>Stories</th>
              <td mat-cell *matCellDef="let r">{{ r.userStoryCount }}</td>
            </ng-container>
            <ng-container matColumnDef="tasks">
              <th mat-header-cell *matHeaderCellDef>Tasks</th>
              <td mat-cell *matCellDef="let r">{{ r.taskCount }}</td>
            </ng-container>
            <ng-container matColumnDef="tests">
              <th mat-header-cell *matHeaderCellDef>Tests</th>
              <td mat-cell *matCellDef="let r">{{ r.testCaseCount }}</td>
            </ng-container>
            <ng-container matColumnDef="ambig">
              <th mat-header-cell *matHeaderCellDef>Ambiguities</th>
              <td mat-cell *matCellDef="let r">{{ r.ambiguityCount }}</td>
            </ng-container>
            <ng-container matColumnDef="created">
              <th mat-header-cell *matHeaderCellDef>Created</th>
              <td mat-cell *matCellDef="let r">{{ r.createdAt | date:'short' }}</td>
            </ng-container>
            <ng-container matColumnDef="actions">
              <th mat-header-cell *matHeaderCellDef>Actions</th>
              <td mat-cell *matCellDef="let r">
                <button mat-icon-button color="primary" matTooltip="Open"
                        [routerLink]="['/requirements', r.id]">
                  <mat-icon>open_in_new</mat-icon>
                </button>
                <button mat-icon-button color="warn" matTooltip="Delete" (click)="onDelete(r); $event.stopPropagation()">
                  <mat-icon>delete</mat-icon>
                </button>
              </td>
            </ng-container>

            <tr mat-header-row *matHeaderRowDef="cols"></tr>
            <tr mat-row *matRowDef="let row; columns: cols;"></tr>
          </table>
        </div>
        <ng-template #emptyTpl>
          <div class="empty-state">
            <mat-icon>inbox</mat-icon>
            <p>No requirements yet. Paste text or upload a file above to get started.</p>
          </div>
        </ng-template>
      </mat-card>
    </div>
  `,
  styles: [`
    .dash-grid {
      display: grid;
      gap: 16px;
      grid-template-columns: minmax(0, 1fr) minmax(0, 1fr);
    }
    @media (max-width: 900px) { .dash-grid { grid-template-columns: 1fr; } }
    .reqs-table { width: 100%; }
    .title-link { color: inherit; text-decoration: none; }
    .title-link:hover { text-decoration: underline; }
  `],
})
export class DashboardComponent implements OnInit {
  private service = inject(RequirementService);
  private snack = inject(MatSnackBar);
  private router = inject(Router);

  items: RequirementSummary[] = [];
  loading = false;
  cols = ['title', 'status', 'stories', 'tasks', 'tests', 'ambig', 'created', 'actions'];

  get totalStories(): number { return this.items.reduce((s, r) => s + r.userStoryCount, 0); }
  get totalTasks(): number { return this.items.reduce((s, r) => s + r.taskCount, 0); }
  get totalTests(): number { return this.items.reduce((s, r) => s + r.testCaseCount, 0); }

  ngOnInit(): void { this.refresh(); }

  refresh(): void {
    this.loading = true;
    this.service.list().subscribe({
      next: x => { this.items = x; this.loading = false; },
      error: e => {
        this.loading = false;
        this.snack.open('Failed to load: ' + (e?.error?.error || e.message), 'Dismiss', { duration: 4000 });
      },
    });
  }

  onIngested(r: RequirementSummary): void {
    this.refresh();
    this.router.navigate(['/requirements', r.id]);
  }

  onDelete(r: RequirementSummary): void {
    if (!confirm(`Delete "${r.title}"?`)) return;
    this.service.delete(r.id).subscribe({
      next: () => { this.snack.open('Deleted', 'OK', { duration: 2000 }); this.refresh(); },
      error: e => this.snack.open('Delete failed: ' + (e?.error?.error || e.message), 'Dismiss', { duration: 4000 }),
    });
  }

  statusLabel(s: number): string {
    return REQUIREMENT_STATUS_LABEL[s as 0 | 1 | 2 | 3] || 'Unknown';
  }
}
