using deepLearning.Services.EmotionServices;
using deepLearning.Services.RabbitMQServices.ImgServices;
using Microsoft.AspNetCore.Mvc;
using System.Text.Json;

namespace deepLearning.Controllers.AnalyzeController
{
    [Route("api/[controller]")]
    [ApiController]
    public class AnalyzeImgController : ControllerBase
    {
        private readonly ImgManager _imgManager;
        private readonly ILogger<AnalyzeImgController> _logger;
        private readonly IEmotionResultService _emotionResultService;

        public AnalyzeImgController(ImgManager imgManager, ILogger<AnalyzeImgController> logger, IEmotionResultService emotionResultService)
        {
            _emotionResultService = emotionResultService;
            _imgManager = imgManager;
            _logger = logger;
        }

        [HttpPost("img")]
        public async Task<IActionResult> AnalyzeImgAsync(IFormFile image)
        {
            if (image == null || image.Length == 0)
            {
                _logger.LogWarning("No image uploaded.");
                return BadRequest(new { success = false, message = "No image uploaded." });
            }

            try
            {
                var savedPath = await _imgManager.SaveImgAndGetUrlAsync(image);

                if (string.IsNullOrEmpty(savedPath))
                {
                    _logger.LogWarning("Failed to create img file.");
                    return BadRequest(new
                    {
                        success = false,
                        message = "Failed to create img file."
                    });
                }

                var fileId = await _imgManager.PublishFilePathAsync(savedPath);

                if (fileId == null)
                {
                    return BadRequest(new
                    {
                        success = false,
                        message = "Failed to send file to RabbitMQ."
                    });
                }

                _logger.LogInformation("Image file has been created and sent successfully.");

                return Ok(new
                {
                    success = true,
                    message = "We have received your request. Please wait while we process it.",
                    fileId
                });
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "An error occurred while processing the image.");

                return StatusCode(500, new
                {
                    success = false,
                    message = "An unexpected error occurred while processing the image.",
                    error = ex.Message
                });
            }
        }
        [HttpGet("get-emotion-result")]
        public IActionResult GetEmotionResult([FromQuery] string id)
        {
            if (string.IsNullOrEmpty(id))
            {
                return BadRequest(new
                {
                    success = false,
                    message = "Id is required."
                });
            }

            _logger.LogInformation("Checking for emotion result with id: {Id}", id);

            // 1. Thử lấy kết quả đơn
            var emotionResult = _emotionResultService.GetEmotionResult(id);
            if (emotionResult != null)
            {
                var singleResponse = new
                {
                    success = true,
                    message = "Success (single result)",
                    data = new
                    {
                        emotionResult.Id,
                        emotionResult.Emotion
                    }
                };

                _logger.LogInformation("Returned single emotion result: {Result}", JsonSerializer.Serialize(singleResponse));
                return Ok(singleResponse);
            }

            // 2. Nếu không có kết quả đơn, thử lấy kết quả theo video (danh sách frame)
            var videoResults = _emotionResultService.GetVideoEmotionResult(id);
            if (videoResults != null && videoResults.Count >= 2)
            {
                var batchResponse = new
                {
                    success = true,
                    message = "Success (batch result)",
                    data = new
                    {
                        VideoId = id,
                        FrameCount = videoResults.Count,
                        Results = videoResults
                    }
                };

                _logger.LogInformation("Returned batch video emotion result: {Result}", JsonSerializer.Serialize(batchResponse));
                return Ok(batchResponse);
            }

            // 3. Không tìm thấy gì
            return NotFound(new
            {
                success = false,
                message = "Emotion result not found."
            });
        }
    }
}
