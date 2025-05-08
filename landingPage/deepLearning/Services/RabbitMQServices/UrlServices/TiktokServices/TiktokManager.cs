using deepLearning.Services.RabbitMQServices.UrlServices.TikTokServices;

namespace deepLearning.Services.RabbitMQServices.UrlServices.TiktokServices
{
    public class TiktokManager
    {
        private readonly ITiktokQueueProducerService _tiktokQueueProducerService;

        public TiktokManager(
            ITiktokQueueProducerService tiktokQueueProducerService)
        {
            _tiktokQueueProducerService = tiktokQueueProducerService;
        }
        public async Task<string> PublishTiktokMessageAsync(string messageText)
        {
            var fileId = await _tiktokQueueProducerService.SendTiktokUrlToRabbitMQ(messageText);
            return fileId;
        }
    }
}
