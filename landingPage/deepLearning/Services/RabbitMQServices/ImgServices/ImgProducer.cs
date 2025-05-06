using deepLearning.Services.RabbitMQServices.ExcelService;
using Newtonsoft.Json;
using RabbitMQ.Client;
using System.Text;

namespace deepLearning.Services.RabbitMQServices.ImgServices
{
    public interface IImgQueueProducerService
    {
        Task SendImgFileToRabbitMQ(string filePath);
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
        public async Task SendImgFileToRabbitMQ(string filePath)
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
                   queue: _imgQueue,
                   durable: true,
                   exclusive: false,
                   autoDelete: false,
                   arguments: null);

                var fileInfo = new
                {
                    Id = Guid.NewGuid(),
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

                _logger.LogInformation("Sent file info to RabbitMQ: {FilePath}, {Timestamp}", fileInfo.FilePath, DateTime.UtcNow.AddHours(7).ToString("HH:mm MM/dd/yyyy"));
            }
            catch (Exception ex)
            {
                _logger.LogError($"Error while sending file info to queue: {ex.Message}");
            }
        }
    }
}
