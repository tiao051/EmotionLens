namespace deepLearning.Services.RabbitMQServices.AudioServices
{
    public interface IAudioExportService
    {
        Task<string> SaveAudioAndGetUrl(IFormFile audioFile);
    }

    public class AudioExport : IAudioExportService
    {
        private readonly string _saveDirectory;
        private readonly ILogger<AudioExport> _logger;

        public AudioExport(IConfiguration configuration, ILogger<AudioExport> logger)
        {
            _saveDirectory = configuration.GetValue<string>("AudioFileSettings:AudioFileSaveDirectory");
            _logger = logger;
        }

        public async Task<string> SaveAudioAndGetUrl(IFormFile audioFile)
        {
            try
            {
                var fileExtension = Path.GetExtension(audioFile.FileName);
                var fileName = GenerateFullTimestampId() + fileExtension;
                var filePath = Path.Combine(_saveDirectory, fileName);

                var directory = Path.GetDirectoryName(filePath);
                if (!Directory.Exists(directory))
                {
                    Directory.CreateDirectory(directory);
                }

                using (var stream = new FileStream(filePath, FileMode.Create))
                {
                    await audioFile.CopyToAsync(stream);
                }

                return filePath;
            }
            catch (Exception ex)
            {
                _logger.LogError($"[AudioExport] Error saving audio file: {ex.Message} at {ex.StackTrace}");
                return null;
            }
        }

        private string GenerateFullTimestampId()
        {
            var timestamp = DateTime.Now.ToString("HHmm_ddMMyyyy");
            var random = Guid.NewGuid().ToString("N")[..3];
            return $"AUDIO_{timestamp}_{random}";
        }
    }
}
