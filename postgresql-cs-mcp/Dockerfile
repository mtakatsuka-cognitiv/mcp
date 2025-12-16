# Build stage
FROM mcr.microsoft.com/dotnet/sdk:8.0 AS build
WORKDIR /src

# Copy solution and project files
COPY Cognitiv.PostgresqlMcp.sln .
COPY src/PostgresqlMcp/PostgresqlMcp.csproj src/PostgresqlMcp/

# Restore dependencies
RUN dotnet restore

# Copy source code
COPY src/ src/

# Build and publish
RUN dotnet publish src/PostgresqlMcp/PostgresqlMcp.csproj -c Release -o /app/publish

# Runtime stage
FROM mcr.microsoft.com/dotnet/runtime:8.0 AS runtime
WORKDIR /app

# Copy published output
COPY --from=build /app/publish .

# Run the MCP server
ENTRYPOINT ["dotnet", "PostgresqlMcp.dll"]
