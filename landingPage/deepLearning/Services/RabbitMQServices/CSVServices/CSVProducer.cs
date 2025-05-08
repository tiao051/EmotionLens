using Newtonsoft.Json;
using RabbitMQ.Client;
using RabbitMQ.Client.Events;
using System.Text;

namespace deepLearning.Services.RabbitMQServices.CSVService
{
    public interface ICSVQueueProducerService
    {
        Task SendCSVFileToRabbitMQ(string filePath);
    }

    public class CSVProducer : ICSVQueueProducerService
    {   
        private readonly IConfiguration _configuration;
        private readonly ILogger<CSVProducer> _logger;
        private readonly string _csvQueueName;

        public CSVProducer(IConfiguration configuration, ILogger<CSVProducer> logger)
        {
            _configuration = configuration;
            _logger = logger;
            _csvQueueName = _configuration["RabbitMQ:CSVQueue"];
        }
        public async Task SendCSVFileToRabbitMQ(string filePath)
        {
            try
            {
                if (string.IsNullOrEmpty(filePath))
                {
                    _logger.LogError("file path is null or empty");
                    return;
                }

                var factory = new ConnectionFactory
                {
                    HostName = _configuration["RabbitMQ:HostName"],
                    UserName = _configuration["RabbitMQ:UserName"],
                    Password = _configuration["RabbitMQ:Password"],
                    Port = int.Parse(_configuration["RabbitMQ:Port"])
                };

                await using var connection = await factory.CreateConnectionAsync();
                await using var channel = await connection.CreateChannelAsync();

                await channel.QueueDeclareAsync(
                   queue: _csvQueueName,
                   durable: true,
                   exclusive: false,
                   autoDelete: false,
                   arguments: null);

                var fileInfo = new
                {
                    Id = GenerateFullTimestampId(),
                    FilePath = filePath,
                    Timestamp = DateTime.UtcNow
                };

                var message = JsonConvert.SerializeObject(fileInfo);
                var body = Encoding.UTF8.GetBytes(message);

                var properties = new BasicProperties { Persistent = true };

                await channel.BasicPublishAsync(
                   exchange: "",
                   routingKey: _csvQueueName,
                   mandatory: false,
                   basicProperties: properties,
                   body: body);

                _logger.LogInformation("Sent file info to RabbitMQ: {FilePath}, {Timestamp}", fileInfo.FilePath, DateTime.UtcNow.AddHours(7).ToString("HH:mm MM/dd/yyyy"));


            }
            catch (Exception ex)
            {
                _logger.LogError($"Error while sending file info to queue: {ex.Message}");
            }
        }
        public string GenerateFullTimestampId()
        {
            var timestamp = DateTime.Now.ToString("HHmm_ddMMyyyy");
            var random = Guid.NewGuid().ToString("N")[..3];
            return $"CSV_{timestamp}_{random}";
        }
    }
}
