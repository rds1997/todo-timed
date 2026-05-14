export type RequirementStatus = 0 | 1 | 2 | 3;
export const REQUIREMENT_STATUS_LABEL: Record<RequirementStatus, string> = {
  0: 'Ingested',
  1: 'Analyzing',
  2: 'Analyzed',
  3: 'Failed',
};

export type Complexity = 0 | 1 | 2 | 3 | 4;
export const COMPLEXITY_LABEL: Record<Complexity, string> = {
  0: 'Trivial', 1: 'Low', 2: 'Medium', 3: 'High', 4: 'Very High',
};

export type Severity = 0 | 1 | 2 | 3;
export const SEVERITY_LABEL: Record<Severity, string> = {
  0: 'Low', 1: 'Medium', 2: 'High', 3: 'Critical',
};

export type TestCaseKind = 0 | 1 | 2;
export const TEST_KIND_LABEL: Record<TestCaseKind, string> = {
  0: 'Positive', 1: 'Negative', 2: 'Edge',
};

export type ChatRole = 0 | 1 | 2;

export interface RequirementSummary {
  id: string;
  title: string;
  sourceFileName?: string | null;
  status: RequirementStatus;
  createdAt: string;
  updatedAt: string;
  userStoryCount: number;
  taskCount: number;
  testCaseCount: number;
  ambiguityCount: number;
}

export interface Analysis {
  summary: string;
  goals: string;
  stakeholders: string;
  keyConstraints: string;
}

export interface Epic { id: string; title: string; description: string; orderIndex: number; }

export interface UserStory {
  id: string;
  epicId?: string | null;
  title: string;
  asA: string;
  iWant: string;
  soThat: string;
  acceptanceCriteria: string[];
  storyPoints: number;
  complexity: Complexity;
  estimatedHours: number;
  orderIndex: number;
}

export interface DevTask {
  id: string;
  userStoryId?: string | null;
  title: string;
  description: string;
  layer: string;
  estimatedHours: number;
  complexity: Complexity;
  orderIndex: number;
}

export interface TestCase {
  id: string;
  userStoryId?: string | null;
  title: string;
  kind: TestCaseKind;
  preconditions: string;
  steps: string[];
  expectedResult: string;
  orderIndex: number;
}

export interface AmbiguityFinding {
  id: string;
  excerpt: string;
  issue: string;
  suggestion: string;
  severity: Severity;
  category: string;
  orderIndex: number;
}

export interface EstimationSummary {
  totalStoryPoints: number;
  totalEstimatedHours: number;
  backendHours: number;
  frontendHours: number;
  qaHours: number;
  infraHours: number;
  storyCount: number;
  taskCount: number;
}

export interface RequirementDetail {
  id: string;
  title: string;
  sourceText: string;
  sourceFileName?: string | null;
  status: RequirementStatus;
  createdAt: string;
  updatedAt: string;
  analysis: Analysis | null;
  epics: Epic[];
  userStories: UserStory[];
  tasks: DevTask[];
  testCases: TestCase[];
  ambiguities: AmbiguityFinding[];
  estimation: EstimationSummary;
}

export interface ChatMessage {
  id: string;
  role: ChatRole;
  content: string;
  createdAt: string;
}

export interface ChatTurn {
  userMessage: ChatMessage;
  assistantMessage: ChatMessage;
}
