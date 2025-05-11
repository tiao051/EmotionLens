using Newtonsoft.Json.Linq;

namespace deepLearning.Services.RabbitMQServices.UrlServices.CSVServices
{
    public class CSVManager
    {
        private readonly ICSVQueueProducerService _csvQueueProducerService;
        private readonly ICSVExportService _exportService;

        public CSVManager(
            ICSVExportService csvExportService,
            ICSVQueueProducerService csvQueueProducerService)
        {
            _exportService = csvExportService;
            _csvQueueProducerService = csvQueueProducerService;
        }

        public async Task<string> CreateCSVFileAsync(JObject videoObj, List<Tuple<string, string>> comments, string videoId)
        {
            return await _exportService.CreateCSVFile(videoObj, comments, videoId);
        }

        public async Task PublishFilePathAsync(string filePath, string channelName, string channelDes)
        {
            await _csvQueueProducerService.SendCSVFileToRabbitMQ(filePath, channelName, channelDes);
        }
    }
}
