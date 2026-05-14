import { Component } from '@angular/core';
import { RouterLink, RouterOutlet } from '@angular/router';
import { MatToolbarModule } from '@angular/material/toolbar';
import { MatIconModule } from '@angular/material/icon';
import { MatButtonModule } from '@angular/material/button';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [RouterOutlet, RouterLink, MatToolbarModule, MatIconModule, MatButtonModule],
  template: `
    <mat-toolbar color="primary" class="app-toolbar">
      <mat-icon>auto_awesome</mat-icon>
      <span class="app-title" routerLink="/">SDLC Copilot</span>
      <span class="spacer"></span>
      <a mat-button href="https://github.com/rds1997/todo-timed" target="_blank" rel="noopener">
        <mat-icon>open_in_new</mat-icon> GitHub
      </a>
    </mat-toolbar>
    <main class="app-main">
      <router-outlet />
    </main>
  `,
  styles: [`
    .app-toolbar { gap: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.06); }
    .app-title { font-size: 1.15rem; font-weight: 600; cursor: pointer; }
    .app-main {
      max-width: 1400px;
      margin: 0 auto;
      padding: 32px 24px 64px 24px;
    }
  `],
})
export class AppComponent {}
