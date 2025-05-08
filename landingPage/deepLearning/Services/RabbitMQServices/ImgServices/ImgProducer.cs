using Newtonsoft.Json;
using RabbitMQ.Client;
using System.Text;

namespace deepLearning.Services.RabbitMQServices.ImgServices
{
    public interface IImgQueueProducerService
    {
        Task<string> SendImgFileToRabbitMQ(string filePath);
    }

    public class ImgProducer : IImgQueueProducerService
    {
        private readonly IConfiguration _configuration;
        private readonly ILogger<ImgProducer> _logger;
        private readonly string _imgQueue;

        public ImgProducer(IConfiguration configuration, ILogger<ImgProducer> logger)
        {
            _configuration = configuration;
            _logger = logger;
            _imgQueue = _configuration["RabbitMQ:ImgQueue"];
        }

        public async Task<string> SendImgFileToRabbitMQ(string filePath)
        {
            try
            {
                if (string.IsNullOrEmpty(filePath))
                {
                    _logger.LogError("File path is null or empty.");
                    return null;
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
                    queue: _imgQueue,
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
                    routingKey: _imgQueue,
                    mandatory: false,
                    basicProperties: properties,
                    body: body);

                _logger.LogInformation("Sent img file info to RabbitMQ: {FilePath}, {Timestamp}, {FileId}", fileInfo.FilePath, DateTime.UtcNow.AddHours(7).ToString("HH:mm dd/MM/yyyy"), fileInfo.Id);

                return fileInfo.Id;
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error while sending file info to RabbitMQ.");
                return null;
            }
        }

        public string GenerateFullTimestampId()
        {
            var timestamp = DateTime.Now.ToString("HHmm_ddMMyyyy");
            var random = Guid.NewGuid().ToString("N")[..3];
            return $"IMG_{timestamp}_{random}";
        }
    }
}
