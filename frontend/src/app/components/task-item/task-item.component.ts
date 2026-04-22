import { CommonModule, DatePipe } from '@angular/common';
import { Component, EventEmitter, Input, Output, computed, signal } from '@angular/core';
import { TodoTask, computeStatus } from '../../models/todo-task';

@Component({
  selector: 'app-task-item',
  standalone: true,
  imports: [CommonModule, DatePipe],
  templateUrl: './task-item.component.html',
  styleUrl: './task-item.component.css',
})
export class TaskItemComponent {
  private readonly _task = signal<TodoTask | null>(null);

  @Input({ required: true }) set task(value: TodoTask) {
    this._task.set(value);
  }

  get task(): TodoTask {
    return this._task()!;
  }

  @Output() toggleComplete = new EventEmitter<TodoTask>();
  @Output() delete = new EventEmitter<TodoTask>();

  readonly status = computed(() => {
    const t = this._task();
    return t ? computeStatus(t) : 'Pending';
  });

  onToggle(): void {
    this.toggleComplete.emit(this.task);
  }

  onDelete(): void {
    this.delete.emit(this.task);
  }
}
