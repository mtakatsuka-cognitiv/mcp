using DotNetEnv;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Hosting;
using Microsoft.Extensions.Logging;
using ModelContextProtocol.Server;

namespace PostgresqlMcp;

public class Program
{
    public static async Task Main(string[] args)
    {
        // Load .env file if it exists (does not override existing environment variables)
        Env.TraversePath().Load();

        var builder = Host.CreateApplicationBuilder(args);

        builder.Logging.AddConsole(options =>
        {
            options.LogToStandardErrorThreshold = LogLevel.Trace;
        });

        builder.Services.AddSingleton<DatabaseConfig>(_ => DatabaseConfig.FromEnvironment());

        builder.Services
            .AddMcpServer()
            .WithStdioServerTransport()
            .WithToolsFromAssembly();

        var app = builder.Build();

        await app.RunAsync();
    }
}
