namespace SdlcCopilot.Domain.Enums;

public enum Severity
{
    Low = 0,
    Medium = 1,
    High = 2,
    Critical = 3
}

public enum Complexity
{
    Trivial = 0,
    Low = 1,
    Medium = 2,
    High = 3,
    VeryHigh = 4
}

public enum TestCaseKind
{
    Positive = 0,
    Negative = 1,
    Edge = 2
}

public enum ChatRole
{
    User = 0,
    Assistant = 1,
    System = 2
}
