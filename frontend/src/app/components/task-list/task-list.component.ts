import { CommonModule } from '@angular/common';
import {
  Component,
  DestroyRef,
  OnInit,
  ViewChild,
  computed,
  inject,
  signal,
} from '@angular/core';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import {
  CreateTaskPayload,
  TaskStatus,
  TodoTask,
  computeStatus,
} from '../../models/todo-task';
import { TaskService } from '../../services/task.service';
import { TaskFormComponent } from '../task-form/task-form.component';
import { TaskItemComponent } from '../task-item/task-item.component';

type FilterValue = 'All' | TaskStatus;

@Component({
  selector: 'app-task-list',
  standalone: true,
  imports: [CommonModule, TaskFormComponent, TaskItemComponent],
  templateUrl: './task-list.component.html',
  styleUrl: './task-list.component.css',
})
export class TaskListComponent implements OnInit {
  private readonly taskService = inject(TaskService);
  private readonly destroyRef = inject(DestroyRef);

  @ViewChild(TaskFormComponent) form?: TaskFormComponent;

  readonly tasks = signal<TodoTask[]>([]);
  readonly loading = signal(true);
  readonly loadError = signal<string | null>(null);
  readonly filter = signal<FilterValue>('All');
  private readonly tick = signal(0);

  readonly filters: FilterValue[] = ['All', 'Pending', 'Overdue', 'Completed'];

  readonly counts = computed(() => {
    this.tick();
    const all = this.tasks();
    const base = { All: all.length, Pending: 0, Overdue: 0, Completed: 0 };
    for (const t of all) {
      base[computeStatus(t)]++;
    }
    return base;
  });

  readonly visibleTasks = computed(() => {
    this.tick();
    const f = this.filter();
    const all = this.tasks();
    if (f === 'All') {
      return all;
    }
    return all.filter((t) => computeStatus(t) === f);
  });

  ngOnInit(): void {
    this.loadTasks();
    const interval = setInterval(() => this.tick.update((n) => n + 1), 30_000);
    this.destroyRef.onDestroy(() => clearInterval(interval));
  }

  loadTasks(): void {
    this.loading.set(true);
    this.loadError.set(null);
    this.taskService
      .getAll()
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: (tasks) => {
          this.tasks.set(tasks);
          this.loading.set(false);
        },
        error: (err) => {
          this.loading.set(false);
          this.loadError.set(this.describeError(err));
        },
      });
  }

  onCreate(payload: CreateTaskPayload): void {
    this.taskService
      .create(payload)
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: (created) => {
          this.tasks.update((list) => [...list, created]);
          this.form?.reset();
        },
        error: (err) => this.form?.setError(this.describeError(err)),
      });
  }

  onToggleComplete(task: TodoTask): void {
    const next = { ...task, isCompleted: !task.isCompleted };
    this.taskService
      .update(task.id, {
        title: next.title,
        description: next.description,
        startTime: next.startTime,
        endTime: next.endTime,
        isCompleted: next.isCompleted,
      })
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: (updated) =>
          this.tasks.update((list) =>
            list.map((t) => (t.id === updated.id ? updated : t)),
          ),
      });
  }

  onDelete(task: TodoTask): void {
    this.taskService
      .delete(task.id)
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: () =>
          this.tasks.update((list) => list.filter((t) => t.id !== task.id)),
      });
  }

  setFilter(f: FilterValue): void {
    this.filter.set(f);
  }

  private describeError(err: unknown): string {
    if (err && typeof err === 'object' && 'message' in err) {
      return String((err as { message: unknown }).message);
    }
    return 'Something went wrong. Please try again.';
  }
}
