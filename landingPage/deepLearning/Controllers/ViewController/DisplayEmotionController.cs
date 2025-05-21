using System.Text.Json;
using deepLearning.Services.EmotionServices;
using Microsoft.AspNetCore.Mvc;
using System.Collections.Generic;
using System.Linq;

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

                // Define emotion categories
                var emotions = new[] { "happy", "sad", "angry", "fear", "surprise", "disgust", "neutral" };

                // Calculate text emotions (from comments)
                var textEmotionCounts = new Dictionary<string, int>();
                foreach (var emotion in emotions)
                {
                    textEmotionCounts[emotion] = 0;
                }
                if (batchResults != null && batchResults.Any())
                {
                    foreach (var item in batchResults)
                    {
                        string emotion = (item.Result ?? "No emotion detected").ToLower();
                        if (emotions.Contains(emotion))
                        {
                            textEmotionCounts[emotion] = textEmotionCounts.GetValueOrDefault(emotion) + 1;
                        }
                    }
                }
                var textEmotions = CalculatePercentages(textEmotionCounts, batchResults?.Count() ?? 0);
                var topTextEmotions = textEmotions
                    .Where(x => x.Value > 0)
                    .OrderByDescending(x => x.Value)
                    .Take(4)
                    .ToDictionary(x => x.Key, x => x.Value);

                // Calculate audio emotions (from sections)
                var audioEmotionCounts = new Dictionary<string, int>();
                foreach (var emotion in emotions)
                {
                    audioEmotionCounts[emotion] = 0;
                }
                if (multiResults != null && multiResults.Any())
                {
                    foreach (var item in multiResults)
                    {
                        string emotion = item.Emotion.ToLower();
                        if (emotions.Contains(emotion))
                        {
                            audioEmotionCounts[emotion] = audioEmotionCounts.GetValueOrDefault(emotion) + 1;
                        }
                    }
                }
                var audioEmotions = CalculatePercentages(audioEmotionCounts, multiResults?.Count() ?? 0);
                var topAudioEmotions = audioEmotions
                    .Where(x => x.Value > 0)
                    .OrderByDescending(x => x.Value)
                    .Take(4)
                    .ToDictionary(x => x.Key, x => x.Value);

                // Calculate video emotions (from frames)
                var videoEmotionCounts = new Dictionary<string, int>();
                foreach (var emotion in emotions)
                {
                    videoEmotionCounts[emotion] = 0;
                }
                if (videoResults != null && videoResults.Any())
                {
                    foreach (var item in videoResults)
                    {
                        string emotion = item.Emotion.ToLower();
                        if (emotions.Contains(emotion))
                        {
                            videoEmotionCounts[emotion] = videoEmotionCounts.GetValueOrDefault(emotion) + 1;
                        }
                    }
                }
                var videoEmotions = CalculatePercentages(videoEmotionCounts, videoResults?.Count() ?? 0);
                var topVideoEmotions = videoEmotions
                    .Where(x => x.Value > 0)
                    .OrderByDescending(x => x.Value)
                    .Take(4)
                    .ToDictionary(x => x.Key, x => x.Value);

                // Log only the top emotions
                _logger.LogInformation($"Emotion Analysis Results for Video ID: {id}");
                _logger.LogInformation("Top Text Emotions (excluding 0%):");
                foreach (var emotion in topTextEmotions)
                {
                    _logger.LogInformation($"  {emotion.Key}: {emotion.Value}%");
                }

                _logger.LogInformation("Top Audio Emotions (excluding 0%):");
                foreach (var emotion in topAudioEmotions)
                {
                    _logger.LogInformation($"  {emotion.Key}: {emotion.Value}%");
                }

                _logger.LogInformation("Top Video Emotions (excluding 0%):");
                foreach (var emotion in topVideoEmotions)
                {
                    _logger.LogInformation($"  {emotion.Key}: {emotion.Value}%");
                }

                // Process original data for API response
                var textData = (batchResults != null && batchResults.Any())
                    ? batchResults.Select(r => new
                    {
                        author = r.Author,
                        emotion = r.Result ?? "No emotion detected"
                    }).ToList()
                    : null;

                var audioData = (multiResults != null && multiResults.Any())
                    ? multiResults.Select(r => new
                    {
                        r.VideoId,
                        r.Section,
                        r.Emotion,
                        r.Probs
                    }).ToList()
                    : null;

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
                        topTextEmotions,
                        topAudioEmotions,
                        topVideoEmotions
                    }
                };

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

        private Dictionary<string, double> CalculatePercentages(Dictionary<string, int> emotionCounts, int totalCount)
        {
            var emotions = new[] { "happy", "sad", "angry", "fear", "surprise", "disgust", "neutral" };
            var percentages = new Dictionary<string, double>();
            foreach (var emotion in emotions)
            {
                percentages[emotion] = 0.0;
            }
            if (totalCount > 0)
            {
                foreach (var emotion in emotionCounts.Keys)
                {
                    if (emotions.Contains(emotion))
                    {
                        percentages[emotion] = Math.Round((double)emotionCounts[emotion] / totalCount * 100, 2);
                    }
                }
            }
            return percentages;
        }
    }
}