using deepLearning.Services.RabbitMQServices.ImgServices;
using Newtonsoft.Json;
using RabbitMQ.Client;
using System.Text;

namespace deepLearning.Services.RabbitMQServices.AudioServices
{
    public interface IAudioQueueProducerService
    {
        Task<string> SendAudioFileToRabbitMQ(string filePath);
        string GenerateFullTimestampId();
    }
    public class AudioProducer : IAudioQueueProducerService
    {
        private readonly IConfiguration _configuration;
        private readonly ILogger<AudioProducer> _logger;
        private readonly string _audioQueue;
        public AudioProducer(IConfiguration configuration, ILogger<AudioProducer> logger)
        {
            _configuration = configuration;
            _logger = logger;
            _audioQueue = _configuration["RabbitMQ:AudioQueue"];
        }
        public async Task<string> SendAudioFileToRabbitMQ(string filePath)
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
                    queue: _audioQueue,
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
                    routingKey: _audioQueue,
                    mandatory: false,
                    basicProperties: properties,
                    body: body);

                _logger.LogInformation("Sent audio file info to RabbitMQ: {FilePath}, {Timestamp}, {FileId}", fileInfo.FilePath, DateTime.UtcNow.AddHours(7).ToString("HH:mm dd/MM/yyyy"), fileInfo.Id);

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
            return $"AUDIO_{timestamp}_{random}";
        }
    }
}
