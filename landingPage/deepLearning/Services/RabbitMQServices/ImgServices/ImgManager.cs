using deepLearning.Services.RabbitMQServices.ExcelService;
using Newtonsoft.Json.Linq;

namespace deepLearning.Services.RabbitMQServices.ImgServices
{
    public class ImgManager
    {
        private readonly IImgQueueProducerService _imgQueueProducerService;
        private readonly IImgExportService _imgExportService;
        public ImgManager(
          IImgExportService imgExportService,
          IImgQueueProducerService imgQueueProducerService)
        {
            _imgExportService = imgExportService;
            _imgQueueProducerService = imgQueueProducerService;
        }
        public async Task<string> SaveImgAndGetUrlAsync(IFormFile image)
        {
            return await _imgExportService.SaveImageAndGetUrl(image);
        }

        public async Task<string> PublishFilePathAsync(string filePath)
        {
            var fileId = await _imgQueueProducerService.SendImgFileToRabbitMQ(filePath);
            
            return fileId;
        }
    }
}
