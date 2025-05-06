using deepLearning.Controllers.YoutubeController;
using deepLearning.Services.DataPreprocessing;
using deepLearning.Services.Interfaces;
using deepLearning.Services.RabbitMQServices.ExcelService;
using deepLearning.Services.RabbitMQServices.ImgServices;
using deepLearning.Services.SentimentService;
using DocumentFormat.OpenXml.Office2016.Drawing.ChartDrawing;

var builder = WebApplication.CreateBuilder(args);

// Setup logging
builder.Logging.ClearProviders();
builder.Logging.AddConsole();
builder.Logging.AddDebug();
builder.Logging.SetMinimumLevel(LogLevel.Trace);

// Đăng ký DI
builder.Services.AddScoped<TextSentimentAnalyzer>(); 
builder.Services.AddScoped<AudioSentimentAnalyzer>(); 
builder.Services.AddScoped<ImageSentimentAnalyzer>(); 

// Đăng ký Func để sử dụng Factory Injection
builder.Services.AddScoped<Func<string, IAnalysisService>>(serviceProvider => key =>
{
    switch (key)
    {
        case "text":
            return serviceProvider.GetRequiredService<TextSentimentAnalyzer>();
        case "audio":
            return serviceProvider.GetRequiredService<AudioSentimentAnalyzer>();
        case "image":
            return serviceProvider.GetRequiredService<ImageSentimentAnalyzer>();
        default:
            throw new ArgumentException($"Unknown analysis type: {key}");
    }
});

builder.Services.AddScoped<ProcessingData>();
builder.Services.AddScoped<YoutubeCrawlData>();

// đăng ký rabbitMQ services cho csv

builder.Services.AddHostedService<CSVConsumer>();
builder.Services.AddScoped<ICSVQueueProducerService, CSVProducer>();
builder.Services.AddScoped<ICSVExportService, CSVExport>();
builder.Services.AddTransient<CSVManager>();

// đăng ký rabbtiMQ services cho img

builder.Services.AddHostedService<ImgConsumer>();
builder.Services.AddScoped<IImgQueueProducerService,ImgProducer>();
builder.Services.AddScoped<IImgExportService ,ImgExport>();
builder.Services.AddTransient<ImgManager>();
// Add services to the container
builder.Services.AddControllersWithViews();

var app = builder.Build();

// Configure the HTTP request pipeline.
if (!app.Environment.IsDevelopment())
{
    app.UseExceptionHandler("/Home/Error");
    app.UseHsts();
}

app.UseHttpsRedirection();
app.UseStaticFiles();

app.UseRouting();

app.UseAuthorization();

app.MapControllerRoute(
    name: "default",
    pattern: "{controller=Home}/{action=Index}/{id?}");

var logger = app.Services.GetRequiredService<ILogger<Program>>();
Console.WriteLine("App is starting...");
logger.LogInformation(">>> App is starting!");

app.Run();
