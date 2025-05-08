using deepLearning.Controllers.YoutubeController;
using deepLearning.Models.DTO;
using deepLearning.Services.RabbitMQServices.UrlServices.CSVServices;
using deepLearning.Services.RabbitMQServices.UrlServices.TiktokServices;
using Microsoft.AspNetCore.Mvc;

namespace deepLearning.Controllers.AnalyzeController
{
    [Route("api/[controller]")]
    [ApiController]
    public class AnalyzeUrlController : ControllerBase
    {
        private readonly YoutubeCrawlData _youtubeCrawData;
        private readonly CSVManager _csvManager;
        private readonly TiktokManager _tiktokManager;
        public AnalyzeUrlController(YoutubeCrawlData youtubeCrawData, CSVManager csvManager, TiktokManager tiktokManager)
        {
            _youtubeCrawData = youtubeCrawData;
            _csvManager = csvManager;
            _tiktokManager = tiktokManager;
        }
        [HttpPost("youtube")]
        public async Task<JsonResult> AnalyzeYoutubeUrl([FromBody] UrlRequestDTO request)
        {   
            string url = request.Url;
            var videoData = await _youtubeCrawData.GetVideoInfoAsync(url);

            if (videoData == null)
            {
                return new JsonResult(new
                {
                    success = false,
                    message = "Failed to retrieve video data."
                });
            }

            var videoObj = videoData.VideoInfo;
            var allComments = videoData.Comments;
            var videoId = videoData.VideoId;

            var filePath = await _csvManager.CreateCSVFileAsync(videoObj, allComments, videoId);

            if (string.IsNullOrEmpty(filePath))
            {
                return new JsonResult(new
                {
                    success = false,
                    message = "Failed to create CSV file."
                });
            }

            await _csvManager.PublishFilePathAsync(filePath);

            return new JsonResult(new
            {
                success = true,
                message = "CSV file created and sent successfully.",
                filePath
            });
        }
        [HttpPost("tiktok")]
        public async Task<JsonResult> AnalyzeTiktokUrl([FromBody] UrlRequestDTO request)
        {
            await _tiktokManager.PublishTiktokMessageAsync(request.Url);

            return new JsonResult(new
            {
                success = true,
                message = "Tiktok file created and sent successfully.",
                request.Url
            });
        }
    }
}
