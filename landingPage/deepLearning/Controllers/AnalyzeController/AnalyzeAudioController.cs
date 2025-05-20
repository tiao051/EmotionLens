using deepLearning.Services.EmotionServices;
using deepLearning.Services.RabbitMQServices.AudioServices;
using Microsoft.AspNetCore.Mvc;
using System.Text.Json;

namespace deepLearning.Controllers.AnalyzeController
{
    [Route("api/[controller]")]
    [ApiController]
    public class AnalyzeAudioController : ControllerBase
    {
        private readonly AudioManager _audioManager;
        private readonly ILogger<AnalyzeAudioController> _logger;
        private readonly IEmotionResultService _emotionAudioResultService;
        public AnalyzeAudioController(AudioManager audioManager, ILogger<AnalyzeAudioController> logger, IEmotionResultService emotionAudioResultService)
        {
            _emotionAudioResultService = emotionAudioResultService;
            _audioManager = audioManager;
            _logger = logger;
        }
        [HttpPost("upload-audio")]
        public async Task<IActionResult> AnalyzeAudioAsync(IFormFile audioFile)
        {
            if (audioFile == null || audioFile.Length == 0)
            {
                _logger.LogWarning("No audioFile uploaded.");
                return BadRequest(new { success = false, message = "No audioFile uploaded." });
            }

            try
            {   
                // tạo file
                var savedPath = await _audioManager.SaveAudioAndGetUrlAsync(audioFile);

                if (string.IsNullOrEmpty(savedPath))
                {
                    _logger.LogWarning("Failed to create audio file.");
                    return BadRequest(new
                    {
                        success = false,
                        message = "Failed to create audio file."
                    });
                }

                var fileId = await _audioManager.PublishAudioPathAsync(savedPath);

                if (fileId == null)
                {
                    return BadRequest(new
                    {
                        success = false,
                        message = "Failed to send audio file to RabbitMQ."
                    });
                }

                _logger.LogInformation("Audio file has been created and sent successfully.");

                return Ok(new
                {
                    success = true,
                    message = "We have received your request. Please wait while we process it.",
                    fileId
                });
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "An error occurred while processing the audio.");

                return StatusCode(500, new
                {
                    success = false,
                    message = "An unexpected error occurred while processing the audio.",
                    error = ex.Message
                });
            }
        }
        public IActionResult GetAudioEmotionResult([FromQuery] string id)
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

            // 1. Check single audio result
            var singleResult = _emotionAudioResultService.GetEmotionResult(id);

            if (singleResult != null)
            {
                var response = new
                {
                    success = true,
                    message = "Single audio emotion result found.",
                    data = new
                    {
                        Id = singleResult.Id,
                        Emotion = singleResult.Emotion
                    }
                };

                _logger.LogInformation("Returned single audio result: {Result}", JsonSerializer.Serialize(response));
                return Ok(response);
            }

            // 2. Check multi audio result
            var multiResults = _emotionAudioResultService.GetMultiAudioEmotionResult(id);

            if (multiResults != null && multiResults.Any())
            {
                var response = new
                {
                    success = true,
                    message = "Multiple audio section emotion results found.",
                    data = multiResults.Select(r => new
                    {
                        r.VideoId,
                        r.Section,
                        r.Emotion,
                        r.Probs // optional, will be null if not present
                    }).ToList()
                };

                _logger.LogInformation("Returned multi audio results: {Result}", JsonSerializer.Serialize(response));
                return Ok(response);
            }

            // Not found
            return NotFound(new
            {
                success = false,
                message = "No audio emotion result found for the provided ID."
            });
        }
    }
}
