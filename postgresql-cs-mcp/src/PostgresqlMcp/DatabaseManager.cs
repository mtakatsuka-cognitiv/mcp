using System.Text.RegularExpressions;
using Microsoft.Extensions.Logging;
using Npgsql;

namespace PostgresqlMcp;

/// <summary>
/// Manages PostgreSQL database connections and queries for schema introspection.
/// </summary>
public class DatabaseManager : IDisposable
{
    private readonly DatabaseConfig _config;
    private readonly ILogger<DatabaseManager>? _logger;
    private NpgsqlConnection? _connection;
    private bool _disposed;

    public DatabaseManager(DatabaseConfig config, ILogger<DatabaseManager>? logger = null)
    {
        _config = config;
        _logger = logger;
    }

    /// <summary>
    /// Gets the connection string for the PostgreSQL database.
    /// </summary>
    private string ConnectionString =>
        $"Host={_config.Host};Port={_config.Port};Database={_config.Database};" +
        $"Username={_config.User};Password={_config.Password}";

    /// <summary>
    /// Establishes a connection to the database if not already connected.
    /// Sets the session to read-only mode for safety.
    /// </summary>
    private async Task ConnectAsync()
    {
        if (_connection is null || _connection.State != System.Data.ConnectionState.Open)
        {
            try
            {
                _connection = new NpgsqlConnection(ConnectionString);
                await _connection.OpenAsync();

                // Enforce read-only session (equivalent to psycopg2's set_session(readonly=True))
                await using var cmd = new NpgsqlCommand(
                    "SET SESSION CHARACTERISTICS AS TRANSACTION READ ONLY", _connection);
                await cmd.ExecuteNonQueryAsync();

                _logger?.LogInformation("Connected to PostgreSQL database (read-only mode)");
            }
            catch (NpgsqlException ex)
            {
                _logger?.LogError(ex, "Error connecting to database");
                throw;
            }
        }
    }

    /// <summary>
    /// Validates a name (schema, table, etc.) to prevent potential issues.
    /// Only allows alphanumeric characters and underscores.
    /// </summary>
    private static void ValidateName(string name, string typeDesc = "name")
    {
        if (!Regex.IsMatch(name, @"^[a-zA-Z0-9_]+$"))
        {
            throw new ArgumentException($"Invalid {typeDesc}: {name}");
        }
    }

    /// <summary>
    /// List all public schemas in the database.
    /// </summary>
    public async Task<List<string>> ListSchemasAsync()
    {
        await ConnectAsync();

        const string query = """
            SELECT schema_name
            FROM information_schema.schemata
            WHERE schema_name NOT IN ('information_schema', 'pg_catalog')
            AND schema_name NOT LIKE 'pg_toast%'
            AND schema_name NOT LIKE 'pg_temp%'
            ORDER BY schema_name;
            """;

        try
        {
            await using var cmd = new NpgsqlCommand(query, _connection);
            await using var reader = await cmd.ExecuteReaderAsync();

            var schemas = new List<string>();
            while (await reader.ReadAsync())
            {
                schemas.Add(reader.GetString(0));
            }

            return schemas;
        }
        catch (NpgsqlException ex)
        {
            _logger?.LogError(ex, "Error listing schemas");
            throw;
        }
    }

    /// <summary>
    /// List all tables in a given schema.
    /// </summary>
    public async Task<List<string>> ListTablesAsync(string schema)
    {
        ValidateName(schema, "schema name");
        await ConnectAsync();

        const string query = """
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = @schema
            AND table_type = 'BASE TABLE'
            ORDER BY table_name;
            """;

        try
        {
            await using var cmd = new NpgsqlCommand(query, _connection);
            cmd.Parameters.AddWithValue("schema", schema);
            await using var reader = await cmd.ExecuteReaderAsync();

            var tables = new List<string>();
            while (await reader.ReadAsync())
            {
                tables.Add(reader.GetString(0));
            }

            return tables;
        }
        catch (NpgsqlException ex)
        {
            _logger?.LogError(ex, "Error listing tables in schema '{Schema}'", schema);
            throw;
        }
    }

    /// <summary>
    /// Get the table description (columns, types, etc.).
    /// </summary>
    public async Task<List<ColumnInfo>> DescribeTableAsync(string schema, string table)
    {
        ValidateName(schema, "schema name");
        ValidateName(table, "table name");
        await ConnectAsync();

        const string query = """
            SELECT
                column_name,
                data_type,
                is_nullable,
                column_default
            FROM information_schema.columns
            WHERE table_schema = @schema
            AND table_name = @table
            ORDER BY ordinal_position;
            """;

        try
        {
            await using var cmd = new NpgsqlCommand(query, _connection);
            cmd.Parameters.AddWithValue("schema", schema);
            cmd.Parameters.AddWithValue("table", table);
            await using var reader = await cmd.ExecuteReaderAsync();

            var columns = new List<ColumnInfo>();
            while (await reader.ReadAsync())
            {
                columns.Add(new ColumnInfo
                {
                    ColumnName = reader.GetString(0),
                    DataType = reader.GetString(1),
                    IsNullable = reader.GetString(2),
                    ColumnDefault = reader.IsDBNull(3) ? null : reader.GetString(3)
                });
            }

            return columns;
        }
        catch (NpgsqlException ex)
        {
            _logger?.LogError(ex, "Error describing table '{Schema}.{Table}'", schema, table);
            throw;
        }
    }

    /// <summary>
    /// Get the indexes for a table.
    /// </summary>
    public async Task<List<IndexInfo>> GetTableIndexesAsync(string schema, string table)
    {
        ValidateName(schema, "schema name");
        ValidateName(table, "table name");
        await ConnectAsync();

        const string query = """
            SELECT indexname, indexdef
            FROM pg_indexes
            WHERE schemaname = @schema AND tablename = @table
            ORDER BY indexname;
            """;

        try
        {
            await using var cmd = new NpgsqlCommand(query, _connection);
            cmd.Parameters.AddWithValue("schema", schema);
            cmd.Parameters.AddWithValue("table", table);
            await using var reader = await cmd.ExecuteReaderAsync();

            var indexes = new List<IndexInfo>();
            while (await reader.ReadAsync())
            {
                indexes.Add(new IndexInfo
                {
                    IndexName = reader.GetString(0),
                    IndexDef = reader.GetString(1)
                });
            }

            return indexes;
        }
        catch (NpgsqlException ex)
        {
            _logger?.LogError(ex, "Error getting indexes for table '{Schema}.{Table}'", schema, table);
            throw;
        }
    }

    /// <summary>
    /// Get the constraints for a table (primary keys, foreign keys, unique constraints).
    /// </summary>
    public async Task<List<ConstraintInfo>> GetTableConstraintsAsync(string schema, string table)
    {
        ValidateName(schema, "schema name");
        ValidateName(table, "table name");
        await ConnectAsync();

        const string query = """
            SELECT conname as constraint_name, pg_get_constraintdef(c.oid) as constraint_def
            FROM pg_constraint c
            JOIN pg_namespace n ON n.oid = c.connamespace
            JOIN pg_class t ON t.oid = c.conrelid
            WHERE n.nspname = @schema AND t.relname = @table
            ORDER BY conname;
            """;

        try
        {
            await using var cmd = new NpgsqlCommand(query, _connection);
            cmd.Parameters.AddWithValue("schema", schema);
            cmd.Parameters.AddWithValue("table", table);
            await using var reader = await cmd.ExecuteReaderAsync();

            var constraints = new List<ConstraintInfo>();
            while (await reader.ReadAsync())
            {
                constraints.Add(new ConstraintInfo
                {
                    ConstraintName = reader.GetString(0),
                    ConstraintDef = reader.GetString(1)
                });
            }

            return constraints;
        }
        catch (NpgsqlException ex)
        {
            _logger?.LogError(ex, "Error getting constraints for table '{Schema}.{Table}'", schema, table);
            throw;
        }
    }

    public void Dispose()
    {
        Dispose(true);
        GC.SuppressFinalize(this);
    }

    protected virtual void Dispose(bool disposing)
    {
        if (!_disposed)
        {
            if (disposing)
            {
                _connection?.Dispose();
            }
            _disposed = true;
        }
    }
}

/// <summary>
/// Configuration for connecting to a PostgreSQL database.
/// </summary>
public record DatabaseConfig
{
    public required string Host { get; init; }
    public int Port { get; init; } = 5432;
    public required string User { get; init; }
    public required string Password { get; init; }
    public required string Database { get; init; }

    /// <summary>
    /// Creates a DatabaseConfig from environment variables.
    /// </summary>
    public static DatabaseConfig FromEnvironment()
    {
        var host = Environment.GetEnvironmentVariable("POSTGRES_HOST") ?? "localhost";
        var portStr = Environment.GetEnvironmentVariable("POSTGRES_PORT") ?? "5432";
        var user = Environment.GetEnvironmentVariable("POSTGRES_USER") ?? "";
        var password = Environment.GetEnvironmentVariable("POSTGRES_PASSWORD") ?? "";
        var database = Environment.GetEnvironmentVariable("POSTGRES_DATABASE") ?? "";

        if (string.IsNullOrEmpty(user) || string.IsNullOrEmpty(password) || string.IsNullOrEmpty(database))
        {
            throw new InvalidOperationException(
                "Database credentials (POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_DATABASE) are required");
        }

        return new DatabaseConfig
        {
            Host = host,
            Port = int.TryParse(portStr, out var port) ? port : 5432,
            User = user,
            Password = password,
            Database = database
        };
    }
}

/// <summary>
/// Represents column information from a table description.
/// </summary>
public record ColumnInfo
{
    public required string ColumnName { get; init; }
    public required string DataType { get; init; }
    public required string IsNullable { get; init; }
    public string? ColumnDefault { get; init; }
}

/// <summary>
/// Represents index information for a table.
/// </summary>
public record IndexInfo
{
    public required string IndexName { get; init; }
    public required string IndexDef { get; init; }
}

/// <summary>
/// Represents constraint information for a table.
/// </summary>
public record ConstraintInfo
{
    public required string ConstraintName { get; init; }
    public required string ConstraintDef { get; init; }
}
