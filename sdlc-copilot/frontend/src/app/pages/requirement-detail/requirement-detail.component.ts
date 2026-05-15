import { CommonModule } from '@angular/common';
import { Component, Input, OnInit, inject } from '@angular/core';
import { Router, RouterLink } from '@angular/router';
import { MatButtonModule } from '@angular/material/button';
import { MatCardModule } from '@angular/material/card';
import { MatChipsModule } from '@angular/material/chips';
import { MatExpansionModule } from '@angular/material/expansion';
import { MatIconModule } from '@angular/material/icon';
import { MatListModule } from '@angular/material/list';
import { MatProgressBarModule } from '@angular/material/progress-bar';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatSnackBar } from '@angular/material/snack-bar';
import { MatTableModule } from '@angular/material/table';
import { MatTabsModule } from '@angular/material/tabs';
import { MatTooltipModule } from '@angular/material/tooltip';

import { ChatPanelComponent } from '../../components/chat-panel/chat-panel.component';
import { RequirementService } from '../../core/services/requirement.service';
import {
  COMPLEXITY_LABEL, REQUIREMENT_STATUS_LABEL, RequirementDetail,
  SEVERITY_LABEL, TEST_KIND_LABEL,
} from '../../core/models/requirement.models';

@Component({
  selector: 'app-requirement-detail',
  standalone: true,
  imports: [
    CommonModule, RouterLink, ChatPanelComponent,
    MatCardModule, MatTabsModule, MatTableModule, MatChipsModule, MatIconModule,
    MatButtonModule, MatProgressBarModule, MatProgressSpinnerModule,
    MatExpansionModule, MatListModule, MatTooltipModule,
  ],
  template: `
    <ng-container *ngIf="detail; else loadingTpl">
      <div class="header">
        <a mat-icon-button routerLink="/" matTooltip="Back to dashboard">
          <mat-icon>arrow_back</mat-icon>
        </a>
        <h1 class="page-title" style="margin: 0">
          <mat-icon>article</mat-icon>
          {{ detail.title }}
        </h1>
        <span class="spacer"></span>
        <mat-chip-set>
          <mat-chip [color]="detail.status === 2 ? 'primary' : detail.status === 3 ? 'warn' : undefined" selected>
            {{ statusLabel(detail.status) }}
          </mat-chip>
        </mat-chip-set>
        <button mat-flat-button color="primary" (click)="analyze()" [disabled]="analyzing">
          <mat-icon *ngIf="!analyzing">auto_awesome</mat-icon>
          <mat-spinner *ngIf="analyzing" diameter="20"></mat-spinner>
          {{ detail.status === 2 ? 'Re-analyze' : 'Analyze with AI' }}
        </button>
        <a mat-stroked-button [href]="mdUrl" target="_blank" rel="noopener">
          <mat-icon>description</mat-icon> Export MD
        </a>
        <a mat-stroked-button [href]="jsonUrl" target="_blank" rel="noopener">
          <mat-icon>data_object</mat-icon> Export JSON
        </a>
        <a mat-stroked-button [href]="csvUrl" target="_blank" rel="noopener" matTooltip="Jira-compatible CSV">
          <mat-icon>table_chart</mat-icon> Export CSV
        </a>
      </div>

      <mat-progress-bar *ngIf="analyzing" mode="indeterminate"></mat-progress-bar>

      <div class="card-grid" style="margin-top: 16px">
        <div class="kpi-card mat-elevation-z1">
          <span class="kpi-label">Story points</span>
          <span class="kpi-value">{{ detail.estimation.totalStoryPoints }}</span>
          <span class="kpi-sub">{{ detail.estimation.storyCount }} stories</span>
        </div>
        <div class="kpi-card mat-elevation-z1">
          <span class="kpi-label">Total hours</span>
          <span class="kpi-value">{{ detail.estimation.totalEstimatedHours }}h</span>
          <span class="kpi-sub">{{ detail.estimation.taskCount }} tasks</span>
        </div>
        <div class="kpi-card mat-elevation-z1">
          <span class="kpi-label">Backend / Frontend</span>
          <span class="kpi-value">{{ detail.estimation.backendHours }}h / {{ detail.estimation.frontendHours }}h</span>
        </div>
        <div class="kpi-card mat-elevation-z1">
          <span class="kpi-label">QA / Infra</span>
          <span class="kpi-value">{{ detail.estimation.qaHours }}h / {{ detail.estimation.infraHours }}h</span>
        </div>
        <div class="kpi-card mat-elevation-z1">
          <span class="kpi-label">Ambiguities</span>
          <span class="kpi-value">{{ detail.ambiguities.length }}</span>
          <span class="kpi-sub">{{ criticalAmbiguities }} critical</span>
        </div>
      </div>

      <mat-tab-group class="section" dynamicHeight>
        <mat-tab label="Summary">
          <div class="tab-pad">
            <mat-card *ngIf="detail.analysis; else noAnalysis">
              <mat-card-content>
                <h3>Summary</h3>
                <p>{{ detail.analysis.summary }}</p>
                <h3>Goals</h3>
                <pre class="prose">{{ detail.analysis.goals }}</pre>
                <h3>Stakeholders</h3>
                <pre class="prose">{{ detail.analysis.stakeholders }}</pre>
                <h3>Key Constraints</h3>
                <pre class="prose">{{ detail.analysis.keyConstraints }}</pre>
              </mat-card-content>
            </mat-card>
            <ng-template #noAnalysis>
              <div class="empty-state">
                <mat-icon>auto_awesome</mat-icon>
                <p>No analysis yet. Click <strong>Analyze with AI</strong> to generate artifacts.</p>
              </div>
            </ng-template>
            <mat-card style="margin-top: 16px">
              <mat-card-header>
                <mat-card-title><mat-icon>notes</mat-icon> Source text</mat-card-title>
                <mat-card-subtitle *ngIf="detail.sourceFileName">{{ detail.sourceFileName }}</mat-card-subtitle>
              </mat-card-header>
              <mat-card-content>
                <pre class="source">{{ detail.sourceText }}</pre>
              </mat-card-content>
            </mat-card>
          </div>
        </mat-tab>

        <mat-tab [label]="'Epics & Stories (' + detail.userStories.length + ')'">
          <div class="tab-pad">
            <div *ngFor="let epic of detail.epics" class="epic">
              <h3><mat-icon>collections_bookmark</mat-icon> {{ epic.title }}</h3>
              <p class="muted">{{ epic.description }}</p>
              <mat-accordion>
                <mat-expansion-panel *ngFor="let s of storiesFor(epic.id)">
                  <mat-expansion-panel-header>
                    <mat-panel-title>{{ s.title }}</mat-panel-title>
                    <mat-panel-description>
                      <mat-chip-set>
                        <mat-chip>SP {{ s.storyPoints }}</mat-chip>
                        <mat-chip>{{ complexityLabel(s.complexity) }}</mat-chip>
                        <mat-chip>{{ s.estimatedHours }}h</mat-chip>
                      </mat-chip-set>
                    </mat-panel-description>
                  </mat-expansion-panel-header>
                  <p>
                    <strong>As a</strong> {{ s.asA }},
                    <strong>I want</strong> {{ s.iWant }},
                    <strong>so that</strong> {{ s.soThat }}.
                  </p>
                  <h4>Acceptance criteria</h4>
                  <ul>
                    <li *ngFor="let ac of s.acceptanceCriteria">{{ ac }}</li>
                  </ul>
                </mat-expansion-panel>
              </mat-accordion>
            </div>
            <ng-container *ngIf="orphanStories.length">
              <h3 style="margin-top: 24px"><mat-icon>label</mat-icon> Other stories</h3>
              <mat-accordion>
                <mat-expansion-panel *ngFor="let s of orphanStories">
                  <mat-expansion-panel-header>
                    <mat-panel-title>{{ s.title }}</mat-panel-title>
                    <mat-panel-description>
                      <mat-chip-set>
                        <mat-chip>SP {{ s.storyPoints }}</mat-chip>
                        <mat-chip>{{ s.estimatedHours }}h</mat-chip>
                      </mat-chip-set>
                    </mat-panel-description>
                  </mat-expansion-panel-header>
                  <p><strong>As a</strong> {{ s.asA }}, <strong>I want</strong> {{ s.iWant }}, <strong>so that</strong> {{ s.soThat }}.</p>
                  <ul>
                    <li *ngFor="let ac of s.acceptanceCriteria">{{ ac }}</li>
                  </ul>
                </mat-expansion-panel>
              </mat-accordion>
            </ng-container>
            <div *ngIf="!detail.userStories.length" class="empty-state">
              <p>Run analysis to generate user stories.</p>
            </div>
          </div>
        </mat-tab>

        <mat-tab [label]="'Tasks (' + detail.tasks.length + ')'">
          <div class="tab-pad scroll-x">
            <table mat-table [dataSource]="detail.tasks" *ngIf="detail.tasks.length; else emptyTasks" class="full-w">
              <ng-container matColumnDef="title">
                <th mat-header-cell *matHeaderCellDef>Task</th>
                <td mat-cell *matCellDef="let t">
                  <strong>{{ t.title }}</strong>
                  <div class="muted">{{ t.description }}</div>
                </td>
              </ng-container>
              <ng-container matColumnDef="layer">
                <th mat-header-cell *matHeaderCellDef>Layer</th>
                <td mat-cell *matCellDef="let t">
                  <span class="pill" [ngClass]="'layer-' + t.layer">{{ t.layer }}</span>
                </td>
              </ng-container>
              <ng-container matColumnDef="hours">
                <th mat-header-cell *matHeaderCellDef>Hours</th>
                <td mat-cell *matCellDef="let t">{{ t.estimatedHours }}</td>
              </ng-container>
              <ng-container matColumnDef="complexity">
                <th mat-header-cell *matHeaderCellDef>Complexity</th>
                <td mat-cell *matCellDef="let t">{{ complexityLabel(t.complexity) }}</td>
              </ng-container>
              <tr mat-header-row *matHeaderRowDef="taskCols"></tr>
              <tr mat-row *matRowDef="let row; columns: taskCols;"></tr>
            </table>
            <ng-template #emptyTasks>
              <div class="empty-state">No tasks yet — run analysis.</div>
            </ng-template>
          </div>
        </mat-tab>

        <mat-tab [label]="'Test cases (' + detail.testCases.length + ')'">
          <div class="tab-pad">
            <mat-accordion>
              <mat-expansion-panel *ngFor="let t of detail.testCases">
                <mat-expansion-panel-header>
                  <mat-panel-title>
                    <span class="pill" [ngClass]="'chip-' + kindClass(t.kind)">{{ kindLabel(t.kind) }}</span>
                    &nbsp;{{ t.title }}
                  </mat-panel-title>
                </mat-expansion-panel-header>
                <p *ngIf="t.preconditions"><strong>Preconditions:</strong> {{ t.preconditions }}</p>
                <h4>Steps</h4>
                <ol><li *ngFor="let s of t.steps">{{ s }}</li></ol>
                <p><strong>Expected:</strong> {{ t.expectedResult }}</p>
              </mat-expansion-panel>
            </mat-accordion>
            <div *ngIf="!detail.testCases.length" class="empty-state">No test cases yet — run analysis.</div>
          </div>
        </mat-tab>

        <mat-tab [label]="'Ambiguities (' + detail.ambiguities.length + ')'">
          <div class="tab-pad">
            <mat-list>
              <mat-list-item *ngFor="let a of detail.ambiguities" lines="3">
                <mat-icon matListItemIcon [ngClass]="'severity-' + severityClass(a.severity)">warning</mat-icon>
                <div matListItemTitle>
                  <span class="pill" [ngClass]="'severity-' + severityClass(a.severity)">
                    {{ severityLabel(a.severity) }}
                  </span>
                  &nbsp;<em>"{{ a.excerpt }}"</em>
                </div>
                <div matListItemLine><strong>Issue:</strong> {{ a.issue }}</div>
                <div matListItemLine><strong>Suggestion:</strong> {{ a.suggestion }}</div>
              </mat-list-item>
            </mat-list>
            <div *ngIf="!detail.ambiguities.length" class="empty-state">No ambiguities flagged.</div>
          </div>
        </mat-tab>

        <mat-tab label="Estimation">
          <div class="tab-pad">
            <div *ngIf="detail.estimation.totalStoryPoints > 0 || detail.estimation.totalEstimatedHours > 0; else noEstimation">

              <!-- Summary cards -->
              <div class="est-summary-grid">
                <div class="est-hero-card mat-elevation-z2">
                  <span class="est-hero-label">Total Story Points</span>
                  <span class="est-hero-value">{{ detail.estimation.totalStoryPoints }}</span>
                  <span class="est-hero-sub">across {{ detail.estimation.storyCount }} user stories</span>
                </div>
                <div class="est-hero-card mat-elevation-z2">
                  <span class="est-hero-label">Total Estimated Hours</span>
                  <span class="est-hero-value">{{ detail.estimation.totalEstimatedHours }}h</span>
                  <span class="est-hero-sub">{{ detail.estimation.taskCount }} tasks in scope</span>
                </div>
              </div>

              <!-- Layer breakdown -->
              <mat-card style="margin-top: 20px">
                <mat-card-header>
                  <mat-card-title><mat-icon>bar_chart</mat-icon>&nbsp;Effort by Layer</mat-card-title>
                  <mat-card-subtitle>Hours allocated per engineering discipline</mat-card-subtitle>
                </mat-card-header>
                <mat-card-content>
                  <div class="layer-bars">
                    <div class="layer-bar-row">
                      <span class="layer-bar-label pill layer-Backend">Backend</span>
                      <mat-progress-bar
                        mode="determinate"
                        [value]="layerPercent(detail.estimation.backendHours)"
                        color="primary"
                        class="layer-progress">
                      </mat-progress-bar>
                      <span class="layer-bar-hours">{{ detail.estimation.backendHours }}h</span>
                    </div>
                    <div class="layer-bar-row">
                      <span class="layer-bar-label pill layer-Frontend">Frontend</span>
                      <mat-progress-bar
                        mode="determinate"
                        [value]="layerPercent(detail.estimation.frontendHours)"
                        color="accent"
                        class="layer-progress">
                      </mat-progress-bar>
                      <span class="layer-bar-hours">{{ detail.estimation.frontendHours }}h</span>
                    </div>
                    <div class="layer-bar-row">
                      <span class="layer-bar-label pill layer-QA">QA</span>
                      <mat-progress-bar
                        mode="determinate"
                        [value]="layerPercent(detail.estimation.qaHours)"
                        color="warn"
                        class="layer-progress">
                      </mat-progress-bar>
                      <span class="layer-bar-hours">{{ detail.estimation.qaHours }}h</span>
                    </div>
                    <div class="layer-bar-row">
                      <span class="layer-bar-label pill layer-Infra">Infra</span>
                      <mat-progress-bar
                        mode="determinate"
                        [value]="layerPercent(detail.estimation.infraHours)"
                        class="layer-progress">
                      </mat-progress-bar>
                      <span class="layer-bar-hours">{{ detail.estimation.infraHours }}h</span>
                    </div>
                  </div>
                </mat-card-content>
              </mat-card>

              <!-- Per-story breakdown table -->
              <mat-card style="margin-top: 16px" *ngIf="detail.userStories.length">
                <mat-card-header>
                  <mat-card-title><mat-icon>format_list_numbered</mat-icon>&nbsp;Story Points Breakdown</mat-card-title>
                </mat-card-header>
                <mat-card-content>
                  <table mat-table [dataSource]="detail.userStories" class="full-w">
                    <ng-container matColumnDef="title">
                      <th mat-header-cell *matHeaderCellDef>User Story</th>
                      <td mat-cell *matCellDef="let s">{{ s.title }}</td>
                    </ng-container>
                    <ng-container matColumnDef="points">
                      <th mat-header-cell *matHeaderCellDef>SP</th>
                      <td mat-cell *matCellDef="let s"><strong>{{ s.storyPoints }}</strong></td>
                    </ng-container>
                    <ng-container matColumnDef="hours">
                      <th mat-header-cell *matHeaderCellDef>Hours</th>
                      <td mat-cell *matCellDef="let s">{{ s.estimatedHours }}h</td>
                    </ng-container>
                    <ng-container matColumnDef="complexity">
                      <th mat-header-cell *matHeaderCellDef>Complexity</th>
                      <td mat-cell *matCellDef="let s">{{ complexityLabel(s.complexity) }}</td>
                    </ng-container>
                    <tr mat-header-row *matHeaderRowDef="storyCols"></tr>
                    <tr mat-row *matRowDef="let row; columns: storyCols;"></tr>
                  </table>
                </mat-card-content>
              </mat-card>

            </div>
            <ng-template #noEstimation>
              <div class="empty-state">
                <mat-icon>show_chart</mat-icon>
                <p>No estimation data yet. Click <strong>Analyze with AI</strong> to generate estimates.</p>
              </div>
            </ng-template>
          </div>
        </mat-tab>

        <mat-tab label="Assistant">
          <div class="tab-pad">
            <app-chat-panel [requirementId]="detail.id"></app-chat-panel>
          </div>
        </mat-tab>
      </mat-tab-group>
    </ng-container>
    <ng-template #loadingTpl>
      <div class="empty-state"><mat-spinner diameter="32"></mat-spinner><p>Loading…</p></div>
    </ng-template>
  `,
  styles: [`
    .header { display: flex; align-items: center; gap: 12px; flex-wrap: wrap; margin-bottom: 16px; }
    .tab-pad { padding: 16px 4px; }
    .epic { margin-bottom: 24px; }
    .epic h3 { display: flex; align-items: center; gap: 8px; }
    .source {
      background: #f7f7fb; padding: 12px; border-radius: 8px;
      white-space: pre-wrap; max-height: 320px; overflow: auto;
      font-family: inherit; font-size: 0.92rem;
    }
    .prose {
      background: transparent; white-space: pre-wrap; font-family: inherit; margin: 0;
    }
    .full-w { width: 100%; }
    .pill {
      display: inline-block; padding: 2px 10px; border-radius: 999px;
      font-size: 0.75rem; font-weight: 600; text-transform: uppercase;
    }
    /* Estimation tab */
    .est-summary-grid {
      display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 16px;
    }
    .est-hero-card {
      display: flex; flex-direction: column; align-items: center;
      padding: 24px 16px; border-radius: 12px; background: #f3f4ff; text-align: center;
    }
    .est-hero-label { font-size: 0.8rem; font-weight: 600; color: #555; text-transform: uppercase; letter-spacing: 0.05em; }
    .est-hero-value { font-size: 2.6rem; font-weight: 700; color: #3f3f7a; line-height: 1.1; margin: 4px 0; }
    .est-hero-sub   { font-size: 0.78rem; color: #888; }
    .layer-bars { display: flex; flex-direction: column; gap: 14px; padding: 8px 0; }
    .layer-bar-row { display: flex; align-items: center; gap: 12px; }
    .layer-bar-label { min-width: 84px; text-align: center; }
    .layer-progress { flex: 1; height: 10px; border-radius: 6px; }
    .layer-bar-hours { min-width: 52px; text-align: right; font-weight: 600; font-size: 0.9rem; }
  `],
})
export class RequirementDetailComponent implements OnInit {
  private service = inject(RequirementService);
  private snack = inject(MatSnackBar);
  private router = inject(Router);

  /** Injected by withComponentInputBinding from the :id route param. */
  @Input() id!: string;

  detail: RequirementDetail | null = null;
  analyzing = false;
  taskCols = ['title', 'layer', 'hours', 'complexity'];
  storyCols = ['title', 'points', 'hours', 'complexity'];

  get mdUrl(): string { return this.service.exportMarkdownUrl(this.id); }
  get jsonUrl(): string { return this.service.exportJsonUrl(this.id); }
  get csvUrl(): string { return this.service.exportCsvUrl(this.id); }

  /** Returns what percentage of total hours a given layer's hours represent (for progress bars). */
  layerPercent(hours: number): number {
    const total = this.detail?.estimation.totalEstimatedHours ?? 0;
    if (!total) return 0;
    return Math.round((hours / total) * 100);
  }

  get orphanStories() {
    if (!this.detail) return [];
    return this.detail.userStories.filter(s => !s.epicId);
  }

  get criticalAmbiguities(): number {
    return this.detail?.ambiguities.filter(a => a.severity >= 2).length ?? 0;
  }

  ngOnInit(): void { this.load(); }

  load(): void {
    this.service.get(this.id).subscribe({
      next: d => { this.detail = d; },
      error: e => {
        this.snack.open('Failed to load: ' + (e?.error?.error || e.message), 'Dismiss', { duration: 4000 });
        this.router.navigate(['/']);
      },
    });
  }

  analyze(): void {
    this.analyzing = true;
    this.service.analyze(this.id).subscribe({
      next: d => {
        this.analyzing = false;
        this.detail = d;
        this.snack.open('Analysis complete', 'OK', { duration: 2500 });
      },
      error: e => {
        this.analyzing = false;
        this.snack.open('Analyze failed: ' + (e?.error?.error || e.message), 'Dismiss', { duration: 4000 });
      },
    });
  }

  storiesFor(epicId: string) {
    return this.detail?.userStories.filter(s => s.epicId === epicId) ?? [];
  }

  statusLabel(s: number): string { return REQUIREMENT_STATUS_LABEL[s as 0 | 1 | 2 | 3] || ''; }
  complexityLabel(c: number): string { return COMPLEXITY_LABEL[c as 0 | 1 | 2 | 3 | 4] || ''; }
  severityLabel(s: number): string { return SEVERITY_LABEL[s as 0 | 1 | 2 | 3] || ''; }
  severityClass(s: number): string { return (this.severityLabel(s) || 'medium').toLowerCase(); }
  kindLabel(k: number): string { return TEST_KIND_LABEL[k as 0 | 1 | 2] || ''; }
  kindClass(k: number): string { return this.kindLabel(k).toLowerCase(); }
}
