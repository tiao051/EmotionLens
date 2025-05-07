using deepLearning.Controllers.AnalyzeController;
using deepLearning.Models.DTO;
using deepLearning.Services.EmotionServices;
using deepLearning.Services.RabbitMQServices.ImgServices;
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
        public AnalyzeTextController(TextManager textManager, ILogger<AnalyzeTextController> logger)
        {
            _textManager = textManager;
            _logger = logger;
        }
        [HttpPost("comment")]
        public async Task<IActionResult> AnalyzeTextAsync([FromBody] TextRequest request)
        {
            Console.WriteLine("12312312312");
            if (request == null || string.IsNullOrWhiteSpace(request.Text))
            {
                return BadRequest(new { success = false, message = "Input text cannot be empty." });
            }
            await _textManager.PublishTextMessageAsync(request.Text);
            _logger.LogInformation("Text message has been sent successfully.");

            return Ok(new
            {
                success = true,
                message = "Text analysis completed."
            });
        }
        [HttpGet("get-text-emotion-result")]
        public async Task<IActionResult> GetTextEmotionResult([FromQuery] string id)
        {
            if (string.IsNullOrWhiteSpace(id))
            {
                return BadRequest("Missing or invalid ID.");
            }

            try
            {
                var emotionResult = _emotionTextResultService.GetEmotionResult(id);

                var response = new
                {
                    Message = "Success",
                    Data = new
                    {
                        emotionResult.Id,
                        emotionResult.Emotion
                    }
                };

                _logger.LogInformation($"Tra ket qua: {JsonSerializer.Serialize(response)}");

                return Ok(response);
            }
            catch (TaskCanceledException)
            {
                return NotFound("Timeout: No text emotion result received within the expected time.");
            }
        }
    }
}
