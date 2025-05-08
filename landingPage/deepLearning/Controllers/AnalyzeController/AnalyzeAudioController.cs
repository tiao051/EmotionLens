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
        [HttpGet("get-audio-emotion-result")]
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

            var emotionResult =  _emotionAudioResultService.GetEmotionResult(id);

            _logger.LogInformation("Checking for emotion result with id: {Id}", id);

            Console.WriteLine($"emotionResult:{emotionResult}");
            if (emotionResult == null)
            {
                return NotFound(new
                {
                    success = false,
                    message = "Emotion audio result not found."
                });
            }

            var response = new
            {
                success = true,
                message = "Success",
                data = new
                {
                    emotionResult.Id,
                    emotionResult.Emotion
                }
            };

            _logger.LogInformation("Returned emotion result: {Result}", JsonSerializer.Serialize(response));
            return Ok(response);
        }
    }
}
