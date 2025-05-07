using deepLearning.Services.DataPreprocessing;
using deepLearning.Services.RabbitMQServices.ExcelService;
using DocumentFormat.OpenXml.Office2010.Excel;
using Newtonsoft.Json.Linq;
using System.Text;

namespace deepLearning.Services.RabbitMQServices.ImgServices
{
    public interface IImgExportService
    {
        Task<string> SaveImageAndGetUrl(IFormFile image);
    }
    public class ImgExport : IImgExportService
    {
        private readonly string _saveDirectory;
        private readonly ILogger<ImgExport> _logger;
        public ImgExport(IConfiguration configuration, ILogger<ImgExport> logger)
        {
            _saveDirectory = configuration.GetValue<string>("ImgFileSettings:ImgFileSaveDirectory");
            _logger = logger;
        }
        public async Task<string> SaveImageAndGetUrl(IFormFile image)
        {
            try
            {
                var fileExtension = Path.GetExtension(image.FileName);
                var fileName = GenerateFullTimestampId() + fileExtension;
                var filePath = Path.Combine(_saveDirectory, fileName);
                var directory = Path.GetDirectoryName(filePath);
                if (!Directory.Exists(directory))
                {
                    Directory.CreateDirectory(directory);
                }

                using (var stream = new FileStream(filePath, FileMode.Create))
                {
                    await image.CopyToAsync(stream);
                }

                return filePath; 
            }
            catch (Exception ex)
            {
                _logger.LogError($"Error saving image: {ex.Message} at {ex.StackTrace}");
                return null;
            }
        }
        public string GenerateFullTimestampId()
        {
            var timestamp = DateTime.Now.ToString("HHmm_ddMMyyyy");
            var random = Guid.NewGuid().ToString("N")[..3];
            return $"IMG_{timestamp}_{random}";
        }
    }
}
