using Newtonsoft.Json;
using RabbitMQ.Client;
using System.Text;

namespace deepLearning.Services.RabbitMQServices.TextServices
{
    public interface ITextQueueProducerService
    {
        Task<string> SendTextFileToRabbitMQ(string messageText);
    }
    public class TextProducer : ITextQueueProducerService
    {
        private readonly IConfiguration _configuration;
        private readonly ILogger<TextProducer> _logger;
        private readonly string _textQueue;
        public TextProducer(IConfiguration configuration, ILogger<TextProducer> logger)
        {
            _configuration = configuration;
            _logger = logger;
            _textQueue = _configuration["RabbitMQ:TextQueue"];
        }
        public async Task<string> SendTextFileToRabbitMQ(string messageText)
        {
            try
            {
                if (string.IsNullOrEmpty(messageText))
                {
                    _logger.LogError("text is null or empty.");
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
                    queue: _textQueue,
                    durable: true,
                    exclusive: false,
                    autoDelete: false,
                    arguments: null);

                var textInfo = new
                {
                    Id = GenerateTextMessageId(),
                    Text = messageText,
                    Timestamp = DateTime.UtcNow
                };

                var jsonPayload = JsonConvert.SerializeObject(textInfo);
                var body = Encoding.UTF8.GetBytes(jsonPayload);

                var properties = new BasicProperties { Persistent = true };

                await channel.BasicPublishAsync(
                    exchange: "",
                    routingKey: _textQueue,
                    mandatory: false,
                    basicProperties: properties,
                    body: body);

                _logger.LogInformation("Published text message to RabbitMQ: {Id}", textInfo.Id);
                return textInfo.Id;
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error while sending text file info to RabbitMQ.");
                return null;
            }
        }

        public string GenerateTextMessageId()
        {
            var timestamp = DateTime.Now.ToString("HHmm_ddMMyyyy");
            var random = Guid.NewGuid().ToString("N")[..3];
            return $"TEXT_{timestamp}_{random}";
        }
    }
}
