using deepLearning.Models.DTO;
using deepLearning.Services.RabbitMQServices.UrlServices.CSVServices;
using deepLearning.Services.RabbitMQServices.UrlServices.TiktokServices;
using deepLearning.Services.TiktokServices;
using deepLearning.Services.YoutubeServices;
using Microsoft.AspNetCore.Mvc;
using Newtonsoft.Json.Linq;

namespace deepLearning.Controllers.AnalyzeController
{
    [Route("api/[controller]")]
    [ApiController]
    public class AnalyzeUrlController : ControllerBase
    {
        private readonly CSVManager _csvManager;
        private readonly YoutubeCrawlDataServices _youtubeCrawlDataServices;
        private readonly TiktokManager _tiktokManager;
        private readonly TiktokHelper _tiktokHelper;
        public AnalyzeUrlController(
            CSVManager csvManager,
            TiktokManager tiktokManager,
            YoutubeCrawlDataServices youtubeCrawlDataServices,
            TiktokHelper tiktokHelper
            )
        {
            _csvManager = csvManager;
            _tiktokManager = tiktokManager;
            _youtubeCrawlDataServices = youtubeCrawlDataServices;
            _tiktokHelper = tiktokHelper;
        }
        [HttpPost("youtube")]
        public async Task<JsonResult> AnalyzeYoutubeUrl([FromBody] UrlRequestDTO request)
        {
            if (string.IsNullOrWhiteSpace(request?.Url))
            {
                return new JsonResult(new
                {
                    success = false,
                    message = "URL is required."
                });
            }

            var videoData = await _youtubeCrawlDataServices.GetVideoDataAsync(request.Url);

            if (videoData == null)
            {
                return new JsonResult(new
                {
                    success = false,
                    message = "Failed to retrieve video data."
                });
            }

            string videoId = videoData.VideoId;
            string channelName = videoData.EntityInfo.EntityName;
            string channelDes = videoData.EntityInfo.Description;
            var comments = videoData.Comments;

            var filePath = await _csvManager.CreateCSVFileAsync(videoData.VideoInfo as JObject, comments, videoId);

            if (string.IsNullOrEmpty(filePath))
            {
                return new JsonResult(new
                {
                    success = false,
                    message = "Failed to create CSV file."
                });
            }

            await _csvManager.PublishFilePathAsync(filePath, channelName, channelDes);

            return new JsonResult(new
            {
                success = true,
                message = "CSV file created and sent successfully.",
                filePath,
                entity = videoData.EntityInfo
            });
        }

        [HttpPost("tiktok")]
        public async Task<JsonResult> AnalyzeTiktokUrl([FromBody] UrlRequestDTO request)
        {
            if (string.IsNullOrEmpty(request.Url))
            {
                return new JsonResult(new
                {
                    success = false,
                    message = "URL is required."
                });
            }

            await _tiktokManager.PublishTiktokMessageAsync(request.Url);

            string videoId = _tiktokHelper.ExtractVideoId(request.Url);

            if (string.IsNullOrEmpty(videoId))
            {
                return new JsonResult(new
                {
                    success = false,
                    message = "Invalid TikTok URL. Could not extract video ID."
                });
            }

            return new JsonResult(new
            {
                success = true,
                message = "Tiktok file created and sent successfully.",
                videoId, 
                url = request.Url
            });
        }
    }
}
