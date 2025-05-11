using deepLearning.Configurations;
using deepLearning.Services.DataPreprocessing;
using deepLearning.Services.EmotionServices;
using deepLearning.Services.RabbitMQServices.AudioServices;
using deepLearning.Services.RabbitMQServices.ImgServices;
using deepLearning.Services.RabbitMQServices.TextServices;
using deepLearning.Services.RabbitMQServices.UrlServices.CSVServices;
using deepLearning.Services.RabbitMQServices.UrlServices.TiktokServices;
using deepLearning.Services.RabbitMQServices.UrlServices.TikTokServices;
using deepLearning.Services.YoutubeServices;

var builder = WebApplication.CreateBuilder(args);

// Setup logging
builder.Logging.AddConsole();
builder.Logging.AddDebug();
builder.Logging.AddFilter("Microsoft", LogLevel.Warning);
builder.Logging.AddFilter("System", LogLevel.Warning);
builder.Logging.SetMinimumLevel(LogLevel.Information);

// Đăng ký DI
builder.Services.Configure<SecretKeyConfig>(builder.Configuration.GetSection("SecretKey"));
builder.Services.AddSingleton<IEmotionResultService, EmotionResultsService>();
builder.Services.AddScoped<ProcessingData>();
builder.Services.AddScoped<YoutubeCrawlDataServices>();

// đăng ký rabbitMQ services cho csv
//builder.Services.AddHostedService<CSVConsumer>();
builder.Services.AddScoped<ICSVQueueProducerService, CSVProducer>();
builder.Services.AddScoped<ICSVExportService, CSVExport>();
builder.Services.AddTransient<CSVManager>();

// đăng ký rabbtiMQ services cho img
//builder.Services.AddHostedService<ImgConsumer>();
builder.Services.AddScoped<IImgQueueProducerService,ImgProducer>();
builder.Services.AddScoped<IImgExportService ,ImgExport>();
builder.Services.AddTransient<ImgManager>();

//đăng ký rabbitMQ services cho text
//builder.Services.AddHostedService<TextConsumer>();
builder.Services.AddScoped<ITextQueueProducerService, TextProducer>();
builder.Services.AddTransient<TextManager>();

//đăng ký rabbitMQ services cho audio
builder.Services.AddScoped<IAudioQueueProducerService, AudioProducer>();
builder.Services.AddScoped<IAudioExportService, AudioExport>();
builder.Services.AddTransient<AudioManager>();

//đăng ký rabbitMQ services cho tiktok 
builder.Services.AddScoped<ITiktokQueueProducerService, TiktokProducer>();
builder.Services.AddTransient<TiktokManager>();

// Add services to the container
builder.Services.AddControllersWithViews();

// Add CORS services
builder.Services.AddCors(options =>
{
    options.AddPolicy("AllowAllOrigins", policy =>
    {
        policy.AllowAnyOrigin()
              .AllowAnyMethod() 
              .AllowAnyHeader();
    });
});

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
app.UseCors("AllowAllOrigins");
app.UseAuthorization();
app.MapControllerRoute(
    name: "default",
    pattern: "{controller=Home}/{action=Index}/{id?}");
app.Run();
