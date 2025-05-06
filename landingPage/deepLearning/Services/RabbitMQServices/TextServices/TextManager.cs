using deepLearning.Services.RabbitMQServices.ImgServices;

namespace deepLearning.Services.RabbitMQServices.TextServices
{
    public class TextManager
    {
        private readonly ITextQueueProducerService _textQueueProducerService;
        public TextManager(ITextQueueProducerService textQueueProducerService)
        {
            _textQueueProducerService = textQueueProducerService;
        }
        public async Task PublishFilePathAsync(string filePath)
        {
            await _textQueueProducerService.SendTextFileToRabbitMQ(filePath);
        }
    }
}
