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
                var emotionResult =  _emotionTextResultService.GetEmotionResult(id);

                if (emotionResult == null)
                {
                    return NotFound(new
                    {
                        success = false,
                        message = "No emotion result found for the provided ID."
                    });
                }

                var response = new
                {
                    success = true,
                    message = "Success",
                    data = new
                    {
                        id = emotionResult.Id,
                        emotion = emotionResult.Emotion ?? "No emotion detected"
                    }
                };

                _logger.LogInformation($"Trả kết quả: {JsonSerializer.Serialize(response)}");

                return Ok(response);
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
