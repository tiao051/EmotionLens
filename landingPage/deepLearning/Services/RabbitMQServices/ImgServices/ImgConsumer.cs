using RabbitMQ.Client.Events;
using RabbitMQ.Client;
using System.Text;
using Newtonsoft.Json;

namespace deepLearning.Services.RabbitMQServices.ImgServices
{
    public interface IImgProcessingConsumerService
    {
        Task StartProcessing(CancellationToken stoppingToken);
    }
    public class ImgConsumer : BackgroundService, IImgProcessingConsumerService
    {
        private readonly IConfiguration _configuration;
        private readonly ILogger<ImgConsumer> _logger;
        private readonly string _imgQueue;
        public ImgConsumer(IConfiguration configuration, ILogger<ImgConsumer> logger)
        {
            _configuration = configuration;
            _logger = logger;
            _imgQueue = _configuration["RabbitMQ:ImgQueue"];
        }
        protected override async Task ExecuteAsync(CancellationToken stoppingToken)
        {
            _logger.LogInformation("Starting the CSVConsumer service.");
            await StartProcessing(stoppingToken);
        }
        public async Task StartProcessing(CancellationToken stoppingToken)
        {
            try
            {
                _logger.LogInformation("Attempting to connect to RabbitMQ for IMG...");
                var factory = new ConnectionFactory
                {
                    HostName = _configuration["RabbitMQ:HostName"],
                    UserName = _configuration["RabbitMQ:UserName"],
                    Password = _configuration["RabbitMQ:Password"],
                    Port = int.Parse(_configuration["RabbitMQ:Port"])
                };

                await using var connection = await factory.CreateConnectionAsync();
                await using var channel = await connection.CreateChannelAsync();

                await channel.QueueDeclareAsync(queue: _imgQueue, durable: true, exclusive: false, autoDelete: false, arguments: null);

                var consumer = new AsyncEventingBasicConsumer(channel);
                consumer.ReceivedAsync += async (sender, ea) =>
                {
                    try
                    {
                        var body = ea.Body.ToArray();
                        var message = Encoding.UTF8.GetString(body);

                        _logger.LogInformation($"Received message from 'excel_queue': {message}");

                        var fileMessage = JsonConvert.DeserializeObject<dynamic>(message);
                        string filePath = fileMessage?.FilePath;

                        _logger.LogInformation($"Received file path: {filePath}");
                    }
                    catch (Exception ex)
                    {
                        _logger.LogError($"Error processing file: {ex.Message}");
                    }
                    finally
                    {
                        await channel.BasicAckAsync(ea.DeliveryTag, false);
                    }
                };

                _logger.LogInformation("Waiting for file messages from RabbitMQ...");
                await channel.BasicConsumeAsync(queue: _imgQueue, autoAck: false, consumer: consumer);
            }
            catch (Exception ex)
            {
                _logger.LogError($"Error in StartProcessing: {ex.Message}");
            }
        }
    }
}
