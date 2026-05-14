FROM mcr.microsoft.com/dotnet/sdk:8.0 AS build
WORKDIR /src

# copy solution and project files first for better layer caching
COPY SdlcCopilot.sln ./
COPY src/SdlcCopilot.Domain/SdlcCopilot.Domain.csproj src/SdlcCopilot.Domain/
COPY src/SdlcCopilot.Application/SdlcCopilot.Application.csproj src/SdlcCopilot.Application/
COPY src/SdlcCopilot.Infrastructure/SdlcCopilot.Infrastructure.csproj src/SdlcCopilot.Infrastructure/
COPY src/SdlcCopilot.Api/SdlcCopilot.Api.csproj src/SdlcCopilot.Api/
RUN dotnet restore SdlcCopilot.sln

COPY . .
RUN dotnet publish src/SdlcCopilot.Api/SdlcCopilot.Api.csproj -c Release -o /app/publish /p:UseAppHost=false

FROM mcr.microsoft.com/dotnet/aspnet:8.0 AS runtime
WORKDIR /app
COPY --from=build /app/publish ./
ENV ASPNETCORE_URLS=http://+:8080 \
    ASPNETCORE_ENVIRONMENT=Production
EXPOSE 8080
ENTRYPOINT ["dotnet", "SdlcCopilot.Api.dll"]
