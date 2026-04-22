import { Component } from '@angular/core';
import { TaskListComponent } from './components/task-list/task-list.component';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [TaskListComponent],
  template: `<app-task-list></app-task-list>`,
  styles: [':host { display: block; min-height: 100vh; background: #f1f5f9; }'],
})
export class AppComponent {}
