FROM mcr.microsoft.com/dotnet/sdk:8.0 AS build
WORKDIR /src
COPY TodoApi.csproj ./
RUN dotnet restore TodoApi.csproj
COPY . ./
RUN dotnet publish TodoApi.csproj -c Release -o /app/publish /p:UseAppHost=false

FROM mcr.microsoft.com/dotnet/aspnet:8.0 AS runtime
WORKDIR /app
COPY --from=build /app/publish ./
ENV ASPNETCORE_ENVIRONMENT=Production
# Hosts (Render, Fly, etc.) set $PORT at runtime. Fall back to 8080 for local runs.
EXPOSE 8080
ENTRYPOINT ["/bin/sh", "-c", "ASPNETCORE_URLS=http://+:${PORT:-8080} exec dotnet TodoApi.dll"]
