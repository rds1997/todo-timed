import { CommonModule } from '@angular/common';
import { Component, EventEmitter, Output, inject } from '@angular/core';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { MatButtonModule } from '@angular/material/button';
import { MatCardModule } from '@angular/material/card';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatIconModule } from '@angular/material/icon';
import { MatInputModule } from '@angular/material/input';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatSnackBar } from '@angular/material/snack-bar';
import { MatTabsModule } from '@angular/material/tabs';

import { RequirementService } from '../../core/services/requirement.service';
import { RequirementSummary } from '../../core/models/requirement.models';

@Component({
  selector: 'app-upload',
  standalone: true,
  imports: [
    CommonModule, ReactiveFormsModule, MatCardModule, MatTabsModule,
    MatFormFieldModule, MatInputModule, MatButtonModule, MatIconModule, MatProgressSpinnerModule,
  ],
  template: `
    <mat-card>
      <mat-card-header>
        <mat-card-title>
          <mat-icon>upload_file</mat-icon> New requirement
        </mat-card-title>
      </mat-card-header>
      <mat-card-content>
        <mat-tab-group>
          <mat-tab label="Paste text">
            <form [formGroup]="textForm" (ngSubmit)="submitText()" class="form">
              <mat-form-field appearance="outline">
                <mat-label>Title</mat-label>
                <input matInput formControlName="title" placeholder="e.g. Online Banking — Statements Module" />
              </mat-form-field>
              <mat-form-field appearance="outline">
                <mat-label>Requirement text</mat-label>
                <textarea matInput rows="8" formControlName="text"
                  placeholder="Paste the raw requirement, BRD excerpt, or user need..."></textarea>
                <mat-hint>Minimum 20 characters.</mat-hint>
              </mat-form-field>
              <div class="actions">
                <button mat-flat-button color="primary" type="submit"
                        [disabled]="textForm.invalid || submitting">
                  <mat-icon>send</mat-icon>
                  Ingest
                </button>
                <mat-spinner *ngIf="submitting" diameter="22"></mat-spinner>
              </div>
            </form>
          </mat-tab>

          <mat-tab label="Upload file">
            <form [formGroup]="fileForm" (ngSubmit)="submitFile()" class="form">
              <mat-form-field appearance="outline">
                <mat-label>Title (optional)</mat-label>
                <input matInput formControlName="title" />
              </mat-form-field>
              <div class="file-row">
                <input type="file" #fileInput hidden
                       accept=".txt,.md,.pdf,.doc,.docx,application/pdf,text/plain,text/markdown"
                       (change)="onFileSelected($event)" />
                <button mat-stroked-button type="button" (click)="fileInput.click()">
                  <mat-icon>attach_file</mat-icon>
                  {{ selectedFile?.name || 'Choose file' }}
                </button>
                <span *ngIf="selectedFile" class="muted">
                  {{ (selectedFile.size / 1024).toFixed(1) }} KB
                </span>
              </div>
              <div class="actions">
                <button mat-flat-button color="primary" type="submit"
                        [disabled]="!selectedFile || submitting">
                  <mat-icon>send</mat-icon>
                  Ingest file
                </button>
                <mat-spinner *ngIf="submitting" diameter="22"></mat-spinner>
              </div>
            </form>
          </mat-tab>
        </mat-tab-group>
      </mat-card-content>
    </mat-card>
  `,
  styles: [`
    .form { display: flex; flex-direction: column; gap: 12px; padding-top: 16px; }
    .actions { display: flex; align-items: center; gap: 12px; }
    .file-row { display: flex; align-items: center; gap: 12px; }
  `],
})
export class UploadComponent {
  private fb = inject(FormBuilder);
  private service = inject(RequirementService);
  private snack = inject(MatSnackBar);

  @Output() ingested = new EventEmitter<RequirementSummary>();

  submitting = false;
  selectedFile: File | null = null;

  textForm = this.fb.group({
    title: ['New requirement', [Validators.required]],
    text: ['', [Validators.required, Validators.minLength(20)]],
  });

  fileForm = this.fb.group({
    title: [''],
  });

  submitText(): void {
    if (this.textForm.invalid) return;
    this.submitting = true;
    const { title, text } = this.textForm.value as { title: string; text: string };
    this.service.ingestText(title, text).subscribe({
      next: r => {
        this.submitting = false;
        this.snack.open('Requirement ingested', 'OK', { duration: 2500 });
        this.ingested.emit(r);
        this.textForm.patchValue({ text: '' });
      },
      error: e => {
        this.submitting = false;
        this.snack.open('Failed: ' + (e?.error?.error || e.message), 'Dismiss', { duration: 4000 });
      },
    });
  }

  onFileSelected(ev: Event): void {
    const input = ev.target as HTMLInputElement;
    this.selectedFile = input.files && input.files.length ? input.files[0] : null;
  }

  submitFile(): void {
    if (!this.selectedFile) return;
    this.submitting = true;
    const title = (this.fileForm.value.title as string) || '';
    this.service.ingestFile(this.selectedFile, title).subscribe({
      next: r => {
        this.submitting = false;
        this.snack.open('File ingested', 'OK', { duration: 2500 });
        this.ingested.emit(r);
        this.selectedFile = null;
      },
      error: e => {
        this.submitting = false;
        this.snack.open('Failed: ' + (e?.error?.error || e.message), 'Dismiss', { duration: 4000 });
      },
    });
  }
}
