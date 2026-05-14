namespace SdlcCopilot.Application.Common;

public class Result<T>
{
    public bool IsSuccess { get; }
    public T? Value { get; }
    public string? Error { get; }
    public int? StatusCode { get; }

    private Result(bool isSuccess, T? value, string? error, int? statusCode)
    {
        IsSuccess = isSuccess;
        Value = value;
        Error = error;
        StatusCode = statusCode;
    }

    public static Result<T> Success(T value) => new(true, value, null, 200);
    public static Result<T> NotFound(string message = "Not found") => new(false, default, message, 404);
    public static Result<T> Failure(string message, int statusCode = 400) => new(false, default, message, statusCode);
}
