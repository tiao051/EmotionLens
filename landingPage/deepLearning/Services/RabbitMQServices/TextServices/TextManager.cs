namespace deepLearning.Services.RabbitMQServices.TextServices
{
    public class TextManager
    {
        private readonly ITextQueueProducerService _textQueueProducerService;
        public TextManager(ITextQueueProducerService textQueueProducerService)
        {
            _textQueueProducerService = textQueueProducerService;
        }
        public async Task<string> PublishTextMessageAsync(string messageText)
        {
            var fileId = await _textQueueProducerService.SendTextFileToRabbitMQ(messageText);
            return fileId;
        }
    }
}
