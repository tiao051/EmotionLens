using RabbitMQ.Client.Events;
using RabbitMQ.Client;
using System.Text;
using Newtonsoft.Json;
using deepLearning.Models.DTO;
using deepLearning.Services.EmotionResults;

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
        private readonly string _imgResultQueue;
        private readonly IEmotionResultService _emotionResultService;
        public ImgConsumer(IConfiguration configuration, ILogger<ImgConsumer> logger, IEmotionResultService emotionResultService)
        {
            _configuration = configuration;
            _logger = logger;
            _emotionResultService = emotionResultService;
            _imgResultQueue = _configuration["RabbitMQ:ImgResultQueue"];
        }
        protected override async Task ExecuteAsync(CancellationToken stoppingToken)
        {
            _logger.LogInformation("Starting the ImgConsumer service.");
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

                await channel.QueueDeclareAsync(queue: _imgResultQueue, durable: true, exclusive: false, autoDelete: false, arguments: null);

                var consumer = new AsyncEventingBasicConsumer(channel);
                consumer.ReceivedAsync += async (sender, ea) =>
                {
                    try
                    {
                        var body = ea.Body.ToArray();
                        var message = Encoding.UTF8.GetString(body);

                        _logger.LogInformation($"Received message from '{_imgResultQueue}': {message}");

                        var fileMessage = JsonConvert.DeserializeObject<EmotionResultDTO>(message);
                        //đẩy result đi
                        _emotionResultService.SetEmotionResult(fileMessage);
                        _logger.LogInformation($"Emotion result - Id: {fileMessage.Id}, Emotion: {fileMessage.Emotion}");

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

                _logger.LogInformation("Waiting for messages from RabbitMQ...");
                await channel.BasicConsumeAsync(queue: _imgResultQueue, autoAck: false, consumer: consumer);
            }
            catch (Exception ex)
            {
                _logger.LogError($"Error in StartProcessing: {ex.Message}");
            }
        }
    }
}
