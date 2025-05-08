//using RabbitMQ.Client.Events;
//using RabbitMQ.Client;
//using System.Text;
//using Newtonsoft.Json;

//namespace deepLearning.Services.RabbitMQServices.ExcelService
//{
//    public interface ICSVProcessingConsumerService
//    {
//        Task StartProcessing(CancellationToken stoppingToken);
//    }

//    public class CSVConsumer : BackgroundService, ICSVProcessingConsumerService
//    {
//        private readonly IConfiguration _configuration;
//        private readonly ILogger<CSVConsumer> _logger;
//        private readonly string _excelQueueName;

//        public CSVConsumer(IConfiguration configuration, ILogger<CSVConsumer> logger)
//        {
//            _configuration = configuration;
//            _logger = logger;
//            _excelQueueName = _configuration["RabbitMQ:ExcelQueue"];
//        }
//        protected override async Task ExecuteAsync(CancellationToken stoppingToken)
//        {
//            _logger.LogInformation("Starting the CSVConsumer service.");
//            Console.WriteLine("Starting the CSVConsumer service.");

//            await StartProcessing(stoppingToken);

//            _logger.LogInformation("CSVConsumer is now listening to RabbitMQ.");
//            Console.WriteLine("CSVConsumer is now listening to RabbitMQ.");
//        }

//        public async Task StartProcessing(CancellationToken stoppingToken)
//        {
//            while (!stoppingToken.IsCancellationRequested)
//            {
//                try
//                {
//                    _logger.LogInformation("Attempting to connect to RabbitMQ...");
//                    var factory = new ConnectionFactory
//                    {
//                        HostName = _configuration["RabbitMQ:HostName"],
//                        UserName = _configuration["RabbitMQ:UserName"],
//                        Password = _configuration["RabbitMQ:Password"],
//                        Port = int.Parse(_configuration["RabbitMQ:Port"])
//                    };

//                    await using var connection = await factory.CreateConnectionAsync();
//                    await using var channel = await connection.CreateChannelAsync();

//                    await channel.QueueDeclareAsync(queue: _excelQueueName, durable: true, exclusive: false, autoDelete: false, arguments: null);

//                    var consumer = new AsyncEventingBasicConsumer(channel);
//                    consumer.ReceivedAsync += async (sender, ea) =>
//                    {
//                        try
//                        {
//                            var body = ea.Body.ToArray();
//                            var message = Encoding.UTF8.GetString(body);

//                            _logger.LogInformation($"Received message from 'excel_queue': {message}");

//                            var fileMessage = JsonConvert.DeserializeObject<dynamic>(message);
//                            string filePath = fileMessage?.FilePath;

//                            _logger.LogInformation($"Received file path: {filePath}");
//                        }
//                        catch (Exception ex)
//                        {
//                            _logger.LogError($"Error processing file: {ex.Message}");
//                        }
//                        finally
//                        {
//                            await channel.BasicAckAsync(ea.DeliveryTag, false);
//                        }
//                    };

//                    _logger.LogInformation("Waiting for file messages from RabbitMQ...");
//                    await channel.BasicConsumeAsync(queue: _excelQueueName, autoAck: false, consumer: consumer);

//                    // Chờ một chút trước khi kết nối lại nếu có sự cố
//                    await Task.Delay(5000);  // Delay 5s giữa các lần tái kết nối nếu có sự cố
//                }
//                catch (Exception ex)
//                {
//                    _logger.LogError($"Error in StartProcessing: {ex.Message}");
//                    await Task.Delay(5000);  // Delay trước khi thử lại
//                }
//            }
//        }
//    }
//}
