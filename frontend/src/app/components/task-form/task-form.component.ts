import { CommonModule } from '@angular/common';
import { Component, EventEmitter, Output, signal } from '@angular/core';
import { FormsModule, NgForm } from '@angular/forms';
import { CreateTaskPayload } from '../../models/todo-task';

interface FormModel {
  title: string;
  description: string;
  startTime: string;
  endTime: string;
}

function defaultStart(): string {
  return toLocalInputValue(new Date());
}

function defaultEnd(): string {
  const d = new Date();
  d.setHours(d.getHours() + 1);
  return toLocalInputValue(d);
}

function toLocalInputValue(d: Date): string {
  const pad = (n: number) => String(n).padStart(2, '0');
  return (
    `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}` +
    `T${pad(d.getHours())}:${pad(d.getMinutes())}`
  );
}

@Component({
  selector: 'app-task-form',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './task-form.component.html',
  styleUrl: './task-form.component.css',
})
export class TaskFormComponent {
  @Output() create = new EventEmitter<CreateTaskPayload>();

  submitting = signal(false);
  error = signal<string | null>(null);

  model: FormModel = {
    title: '',
    description: '',
    startTime: defaultStart(),
    endTime: defaultEnd(),
  };

  onSubmit(form: NgForm): void {
    this.error.set(null);
    if (form.invalid) {
      return;
    }
    const start = new Date(this.model.startTime);
    const end = new Date(this.model.endTime);
    if (end.getTime() <= start.getTime()) {
      this.error.set('End time must be after start time.');
      return;
    }

    this.submitting.set(true);
    this.create.emit({
      title: this.model.title.trim(),
      description: this.model.description.trim(),
      startTime: start.toISOString(),
      endTime: end.toISOString(),
    });
  }

  reset(): void {
    this.submitting.set(false);
    this.model = {
      title: '',
      description: '',
      startTime: defaultStart(),
      endTime: defaultEnd(),
    };
  }

  setError(message: string | null): void {
    this.submitting.set(false);
    this.error.set(message);
  }
}
