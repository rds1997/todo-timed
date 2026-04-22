export interface TodoTask {
  id: string;
  title: string;
  description: string;
  startTime: string;
  endTime: string;
  isCompleted: boolean;
  createdAt: string;
}

export interface CreateTaskPayload {
  title: string;
  description: string;
  startTime: string;
  endTime: string;
}

export interface UpdateTaskPayload extends CreateTaskPayload {
  isCompleted: boolean;
}

export type TaskStatus = 'Pending' | 'Completed' | 'Overdue';

export function computeStatus(task: TodoTask, now: Date = new Date()): TaskStatus {
  if (task.isCompleted) {
    return 'Completed';
  }
  return new Date(task.endTime).getTime() < now.getTime() ? 'Overdue' : 'Pending';
}
