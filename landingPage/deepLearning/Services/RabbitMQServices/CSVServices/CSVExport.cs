using deepLearning.Models.DTO;
using deepLearning.Services.DataPreprocessing;
using Newtonsoft.Json.Linq;
using System.Globalization;
using System.Text;

namespace deepLearning.Services.RabbitMQServices.ExcelService
{
    public interface ICSVExportService
    {
        Task<string> CreateCSVFile(JObject videoObj, List<Tuple<string, string>> comments, string videoId);
    }

    public class CSVExport : ICSVExportService
    {
        private readonly ProcessingData _processingData;
        private readonly string _saveDirectory;
        private readonly ILogger<CSVExport> _logger;

        public CSVExport(IConfiguration configuration, ILogger<CSVExport> logger, ProcessingData processingData)
        {
            _saveDirectory = configuration.GetValue<string>("CSVFileSettings:CSVFileSaveDirectory");
            _processingData = processingData;  
            _logger = logger;
        }

        public async Task<string> CreateCSVFile(JObject videoObj, List<Tuple<string, string>> comments, string videoId)
        {
            var filePath = Path.Combine(_saveDirectory, "YouTubeComments.csv");

            try
            {
                var directory = Path.GetDirectoryName(filePath);
                if (!Directory.Exists(directory))
                {
                    Directory.CreateDirectory(directory);
                }

                var lines = new List<string>();

                // Video Info Section
                //if (videoObj["items"] != null && videoObj["items"].HasValues)
                //{
                //    var snippet = videoObj["items"][0]["snippet"];
                //    var statistics = videoObj["items"][0]["statistics"];

                //    lines.Add($"Tiêu đề:,{EscapeCsv(snippet["title"]?.ToString())}");
                //    lines.Add($"Mô tả:,{EscapeCsv(snippet["description"]?.ToString())}");
                //    lines.Add($"Views:,{EscapeCsv(statistics["viewCount"]?.ToString())}");
                //    lines.Add($"Likes:,{EscapeCsv(statistics["likeCount"]?.ToString())}");
                //}

                //lines.Add(""); // Empty line between sections

                // Comments Section
                lines.Add("Tên người dùng,Nội dung bình luận");
                foreach (var comment in comments)
                {
                    string cleanedComment = _processingData.NormalizeComment(comment.Item2);
                    if (!string.IsNullOrEmpty(cleanedComment))
                    {
                        var line = $"{EscapeCsv(comment.Item1)},{EscapeCsv(cleanedComment)}";
                        lines.Add(line);
                    }
                }

                // Write to file
                await File.WriteAllLinesAsync(filePath, lines, Encoding.UTF8);

                _logger.LogInformation($"CSV file created successfully at {filePath}");
                return filePath;
            }
            catch (Exception ex)
            {
                _logger.LogError($"Error creating CSV file: {ex.Message} at {ex.StackTrace}");
                return null;
            }
        }

        private string EscapeCsv(string field)
        {
            if (string.IsNullOrEmpty(field))
                return "";

            if (field.Contains(",") || field.Contains("\"") || field.Contains("\n"))
            {
                field = $"\"{field.Replace("\"", "\"\"")}\"";
            }
            return field;
        }
    }
}
