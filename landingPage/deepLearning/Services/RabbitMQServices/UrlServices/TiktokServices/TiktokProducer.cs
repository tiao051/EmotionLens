using Newtonsoft.Json;
using RabbitMQ.Client;
using System.Text;

namespace deepLearning.Services.RabbitMQServices.UrlServices.TikTokServices
{
    public interface ITiktokQueueProducerService
    {
        Task<string> SendTiktokUrlToRabbitMQ(string url);
    }

    public class TiktokProducer : ITiktokQueueProducerService
    {
        private readonly IConfiguration _configuration;
        private readonly ILogger<TiktokProducer> _logger;
        private readonly string _tiktokQueueName;

        public TiktokProducer(IConfiguration configuration, ILogger<TiktokProducer> logger)
        {
            _configuration = configuration;
            _logger = logger;
            _tiktokQueueName = _configuration["RabbitMQ:TiktokQueue"];
        }

        public async Task<string> SendTiktokUrlToRabbitMQ(string url)
        {
            if (string.IsNullOrEmpty(url))
            {
                _logger.LogError("URL is null or empty.");
                return null;
            }

            try
            {
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
                    queue: _tiktokQueueName,
                    durable: true,
                    exclusive: false,
                    autoDelete: false,
                    arguments: null);

                var urlInfo = new
                {
                    Id = GenerateFullTimestampId(),
                    Url = url,
                    Timestamp = DateTime.UtcNow
                };

                var message = JsonConvert.SerializeObject(urlInfo);
                var body = Encoding.UTF8.GetBytes(message);

                var properties = new BasicProperties { Persistent = true };

                await channel.BasicPublishAsync(
                    exchange: "",
                    routingKey: _tiktokQueueName,
                    mandatory: false,
                    basicProperties: properties,
                    body: body);

                _logger.LogInformation("Sent TikTok URL to RabbitMQ: {Url}, {Timestamp}, {FileId}", urlInfo.Url, DateTime.UtcNow.AddHours(7).ToString("HH:mm dd/MM/yyyy"), urlInfo.Id);

                return urlInfo.Id;
            }
            catch (Exception ex)
            {
                _logger.LogError($"Error while sending TikTok URL to queue: {ex.Message}");
                return null;
            }
        }

        public string GenerateFullTimestampId()
        {
            var timestamp = DateTime.Now.ToString("HHmm_ddMMyyyy");
            var random = Guid.NewGuid().ToString("N")[..3];
            return $"TIKTOK_{timestamp}_{random}";
        }
    }
}
