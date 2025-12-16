using System.ComponentModel;
using Microsoft.Extensions.Logging;
using ModelContextProtocol.Server;

namespace PostgresqlMcp;

/// <summary>
/// MCP tools for PostgreSQL database introspection.
/// </summary>
[McpServerToolType]
public static class PostgresqlTools
{
    /// <summary>
    /// List all public schemas in the database.
    /// </summary>
    /// <returns>A list of schema names.</returns>
    [McpServerTool(Name = "list_schemas"), Description("List all public schemas in the database.")]
    public static async Task<List<string>> ListSchemas(
        DatabaseConfig config,
        ILogger<DatabaseManager> logger)
    {
        using var db = new DatabaseManager(config, logger);
        return await db.ListSchemasAsync();
    }

    /// <summary>
    /// List all tables in a given schema.
    /// </summary>
    /// <param name="schema">The name of the schema to list tables from.</param>
    /// <returns>A list of table names in the specified schema.</returns>
    [McpServerTool(Name = "list_tables"), Description("List all tables in a given schema.")]
    public static async Task<List<string>> ListTables(
        DatabaseConfig config,
        ILogger<DatabaseManager> logger,
        [Description("The name of the schema to list tables from.")] string schema)
    {
        using var db = new DatabaseManager(config, logger);
        return await db.ListTablesAsync(schema);
    }

    /// <summary>
    /// Get the table description (columns, types, etc.).
    /// </summary>
    /// <param name="schema">The name of the schema.</param>
    /// <param name="table">The name of the table.</param>
    /// <returns>A list of column information for the table.</returns>
    [McpServerTool(Name = "describe_table"), Description("Get the table description (columns, types, etc.).")]
    public static async Task<List<ColumnInfo>> DescribeTable(
        DatabaseConfig config,
        ILogger<DatabaseManager> logger,
        [Description("The name of the schema.")] string schema,
        [Description("The name of the table.")] string table)
    {
        using var db = new DatabaseManager(config, logger);
        return await db.DescribeTableAsync(schema, table);
    }

    /// <summary>
    /// Get the indexes for a table.
    /// </summary>
    /// <param name="schema">The name of the schema.</param>
    /// <param name="table">The name of the table.</param>
    /// <returns>A list of index information for the table.</returns>
    [McpServerTool(Name = "get_table_indexes"), Description("Get the indexes for a table.")]
    public static async Task<List<IndexInfo>> GetTableIndexes(
        DatabaseConfig config,
        ILogger<DatabaseManager> logger,
        [Description("The name of the schema.")] string schema,
        [Description("The name of the table.")] string table)
    {
        using var db = new DatabaseManager(config, logger);
        return await db.GetTableIndexesAsync(schema, table);
    }

    /// <summary>
    /// Get the constraints for a table (primary keys, foreign keys, unique constraints).
    /// </summary>
    /// <param name="schema">The name of the schema.</param>
    /// <param name="table">The name of the table.</param>
    /// <returns>A list of constraint information for the table.</returns>
    [McpServerTool(Name = "get_table_constraints"), Description("Get the constraints for a table (primary keys, foreign keys, unique constraints).")]
    public static async Task<List<ConstraintInfo>> GetTableConstraints(
        DatabaseConfig config,
        ILogger<DatabaseManager> logger,
        [Description("The name of the schema.")] string schema,
        [Description("The name of the table.")] string table)
    {
        using var db = new DatabaseManager(config, logger);
        return await db.GetTableConstraintsAsync(schema, table);
    }
}
