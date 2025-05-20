using deepLearning.Models.DTO;
using deepLearning.Services.EmotionServices;
using deepLearning.Services.RabbitMQServices.TextServices;
using Microsoft.AspNetCore.Mvc;
using System.Text.Json;

namespace deepLearning.Controllers.AnalyzeFolder
{
    [Route("api/[controller]")]
    [ApiController]
    public class AnalyzeTextController : Controller
    {
        private readonly TextManager _textManager;
        private readonly ILogger<AnalyzeTextController> _logger;
        private readonly IEmotionResultService _emotionTextResultService;
        public AnalyzeTextController(TextManager textManager, ILogger<AnalyzeTextController> logger, IEmotionResultService emotionTextResultService)
        {
            _emotionTextResultService = emotionTextResultService;
            _textManager = textManager;
            _logger = logger;
        }
        [HttpPost("comment")]
        public async Task<IActionResult> AnalyzeTextAsync([FromBody] TextRequest request)
        {
            if (request == null || string.IsNullOrWhiteSpace(request.Text))
            {
                return BadRequest(new { success = false, message = "Input text cannot be empty." });
            }
            var fileId = await _textManager.PublishTextMessageAsync(request.Text);
            _logger.LogInformation("Text message has been sent successfully.");

            return Ok(new
            {
                success = true,
                message = "We have received your request. Please wait while we process it.",
                fileId
            });
        }
        [HttpGet("get-text-emotion-result")]
        public async Task<IActionResult> GetTextEmotionResult([FromQuery] string id)
        {
            if (string.IsNullOrWhiteSpace(id))
            {
                return BadRequest(new
                {
                    success = false,
                    message = "Missing or invalid ID."
                });
            }

            try
            {
                // Lấy kết quả batch (list)
                var batchResults = _emotionTextResultService.GetVideoCommentEmotionResult(id);

                if (batchResults != null && batchResults.Any())
                {
                    // Trả về dạng batch
                    var responseBatch = new
                    {
                        success = true,
                        message = "Success - batch results",
                        data = batchResults.Select(r => new
                        {
                            author = r.Author,
                            emotion = r.Result ?? "No emotion detected"
                        })
                    };

                    _logger.LogInformation($"Trả kết quả batch: {JsonSerializer.Serialize(responseBatch)}");

                    return Ok(responseBatch);
                }
                else
                {
                    // Nếu không có batch thì lấy đơn lẻ
                    var singleResult = _emotionTextResultService.GetEmotionResult(id);

                    if (singleResult == null)
                    {
                        return NotFound(new
                        {
                            success = false,
                            message = "No emotion result found for the provided ID."
                        });
                    }

                    var responseSingle = new
                    {
                        success = true,
                        message = "Success - single result",
                        data = new
                        {
                            id = singleResult.Id,
                            emotion = singleResult.Emotion ?? "No emotion detected"
                        }
                    };

                    _logger.LogInformation($"Trả kết quả đơn lẻ: {JsonSerializer.Serialize(responseSingle)}");

                    return Ok(responseSingle);
                }
            }
            catch (TaskCanceledException)
            {
                return NotFound(new
                {
                    success = false,
                    message = "Timeout: No text emotion result received within the expected time."
                });
            }
        }
    }
}
