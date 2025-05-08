using deepLearning.Services.RabbitMQServices.ImgServices;

namespace deepLearning.Services.RabbitMQServices.AudioServices
{
    public class AudioManager
    {
        private readonly IAudioQueueProducerService _audioQueueProducerService;
        private readonly IAudioExportService _audioExportService;
        public AudioManager(
          IAudioExportService audioExportService,
          IAudioQueueProducerService audioQueueProducerService)
        {
            _audioExportService = audioExportService;
            _audioQueueProducerService = audioQueueProducerService;
        }
        public async Task<string> SaveAudioAndGetUrlAsync(IFormFile audioFile)
        {
            return await _audioExportService.SaveAudioAndGetUrl(audioFile);
        }

        public async Task<string> PublishAudioPathAsync(string filePath)
        {
            var fileId = await _audioQueueProducerService.SendAudioFileToRabbitMQ(filePath);

            return fileId;
        }
    }
}
