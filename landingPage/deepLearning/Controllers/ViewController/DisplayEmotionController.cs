using System.Text.Json;
using deepLearning.Services.EmotionServices;
using Microsoft.AspNetCore.Mvc;

namespace deepLearning.Controllers.ViewController
{
    [Route("api/[controller]")]
    [ApiController]
    public class DisplayEmotionController : ControllerBase
    {
        private readonly ILogger<DisplayEmotionController> _logger;
        private readonly IEmotionResultService _emotionResultService;

        public DisplayEmotionController(
            ILogger<DisplayEmotionController> logger,
            IEmotionResultService emotionResultService)
        {
            _emotionResultService = emotionResultService ?? throw new ArgumentNullException(nameof(emotionResultService));
            _logger = logger ?? throw new ArgumentNullException(nameof(logger));
        }
        [HttpGet("get-multi-emotion-result")]
        public async Task<IActionResult> GetMultiEmotionResult([FromQuery] string id)
        {
            try
            {
                if (string.IsNullOrWhiteSpace(id))
                {
                    _logger.LogWarning("GetMultiEmotionResult called with invalid ID");
                    return BadRequest(new { success = false, message = "Missing or invalid ID." });
                }

                _logger.LogInformation($"Retrieving emotion results for video ID: {id}");

                // Get all emotion results in parallel
                var batchResultsTask = Task.Run(() => _emotionResultService.GetVideoCommentEmotionResult(id));
                var multiResultsTask = Task.Run(() => _emotionResultService.GetMultiAudioEmotionResult(id));
                var videoResultsTask = Task.Run(() => _emotionResultService.GetVideoEmotionResult(id));

                await Task.WhenAll(batchResultsTask, multiResultsTask, videoResultsTask);

                var batchResults = batchResultsTask.Result;
                var multiResults = multiResultsTask.Result;
                var videoResults = videoResultsTask.Result;

                // Process text emotion data
                var textData = (batchResults != null && batchResults.Any())
                    ? batchResults.Select(r => new
                    {
                        author = r.Author,
                        emotion = r.Result ?? "No emotion detected"
                    }).ToList()
                    : null;

                // Process audio emotion data
                var audioData = (multiResults != null && multiResults.Any())
                    ? multiResults.Select(r => new
                    {
                        r.VideoId,
                        r.Section,
                        r.Emotion,
                        r.Probs
                    }).ToList()
                    : null;

                // Process video frame emotion data
                var imageData = (videoResults != null && videoResults.Any())
                    ? new
                    {
                        VideoId = id,
                        FrameCount = videoResults.Count,
                        Results = videoResults.Select(r => new
                        {
                            frame = r.Frame,
                            emotion = r.Emotion
                        }).ToList()
                    }
                    : null;

                var result = new
                {
                    success = true,
                    message = "Emotion results retrieved successfully.",
                    data = new
                    {
                        text = textData,
                        audio = audioData,
                        image = imageData
                    }
                };

                // Log the count of each data type
                _logger.LogInformation($"Text data count: {(textData != null ? textData.Count : 0)}");
                _logger.LogInformation($"Audio data count: {(audioData != null ? audioData.Count : 0)}");
                _logger.LogInformation($"Image data count: {(imageData != null ? imageData.Results.Count : 0)}");

                if (_logger.IsEnabled(LogLevel.Debug))
                {
                    _logger.LogDebug("Multi emotion result: {Result}", JsonSerializer.Serialize(result));
                }
                
                return Ok(result);
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error retrieving emotion results for video ID: {VideoId}", id);
                return StatusCode(500, new { success = false, message = "An error occurred while retrieving emotion results." });
            }
        }
    }
}
