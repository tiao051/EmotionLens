//using deepLearning.Services.EmotionResults;
//using deepLearning.Services.RabbitMQServices.ImgServices;
//using RabbitMQ.Client.Events;
//using RabbitMQ.Client;
//using deepLearning.Models.DTO;
//using Newtonsoft.Json;
//using System.Text;

//namespace deepLearning.Services.RabbitMQServices.TextServices
//{
//    public interface ITextProcessingConsumerService
//    {
//        Task StartProcessing(CancellationToken stoppingToken);
//    }
//    public class TextConsumer : BackgroundService, ITextProcessingConsumerService
//    {
//        private readonly IConfiguration _configuration;
//        private readonly ILogger<TextConsumer> _logger;
//        private readonly string _textResultQueue;
//        private readonly IEmotionResultService _emotionTextResultService;
//        public TextConsumer(IConfiguration configuration, ILogger<TextConsumer> logger, IEmotionResultService emotionTextResultService)
//        {
//            _configuration = configuration;
//            _logger = logger;
//            _emotionTextResultService = emotionTextResultService;
//            _textResultQueue = _configuration["RabbitMQ:TextResultQueue"];
//        }
//        protected override async Task ExecuteAsync(CancellationToken stoppingToken)
//        {
//            _logger.LogInformation("Starting the TextConsumer service.");
//            Console.WriteLine("Starting the TextConsumer service.");

//            await StartProcessing(stoppingToken);

//            _logger.LogInformation("TextConsumer is now listening to RabbitMQ.");
//            Console.WriteLine("TextConsumer is now listening to RabbitMQ.");
//        }

//        public async Task StartProcessing(CancellationToken stoppingToken)
//        {
//            try
//            {
//                _logger.LogInformation("Attempting to connect to RabbitMQ for Text...");
//                var factory = new ConnectionFactory
//                {
//                    HostName = _configuration["RabbitMQ:HostName"],
//                    UserName = _configuration["RabbitMQ:UserName"],
//                    Password = _configuration["RabbitMQ:Password"],
//                    Port = int.Parse(_configuration["RabbitMQ:Port"])
//                };

//                await using var connection = await factory.CreateConnectionAsync();
//                await using var channel = await connection.CreateChannelAsync();

//                await channel.QueueDeclareAsync(queue: _textResultQueue, durable: true, exclusive: false, autoDelete: false, arguments: null);

//                var consumer = new AsyncEventingBasicConsumer(channel);
//                consumer.ReceivedAsync += async (sender, ea) =>
//                {
//                    try
//                    {
//                        var body = ea.Body.ToArray();
//                        var message = Encoding.UTF8.GetString(body);

//                        _logger.LogInformation($"Received message from '{_textResultQueue}': {message}");

//                        var fileMessage = JsonConvert.DeserializeObject<EmotionResultDTO>(message);
//                        //đẩy result đi
//                        _emotionTextResultService.SetEmotionResult(fileMessage);
//                        _logger.LogInformation($"Emotion result - Id: {fileMessage.Id}, Emotion: {fileMessage.Emotion}");

//                    }
//                    catch (Exception ex)
//                    {
//                        _logger.LogError($"Error processing file: {ex.Message}");
//                    }
//                    finally
//                    {
//                        await channel.BasicAckAsync(ea.DeliveryTag, false);
//                    }
//                };

//                _logger.LogInformation("Waiting for messages from RabbitMQ...");
//                await channel.BasicConsumeAsync(queue: _textResultQueue, autoAck: false, consumer: consumer);
//            }
//            catch (Exception ex)
//            {
//                _logger.LogError($"Error in StartProcessing: {ex.Message}");
//            }
//        }
//    }
//}
