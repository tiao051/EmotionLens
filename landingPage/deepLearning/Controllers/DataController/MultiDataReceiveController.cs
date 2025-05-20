using deepLearning.Models.DTO;
using deepLearning.Models.DTO.MultiAudioModel;
using deepLearning.Models.DTO.MultiImageModel;
using deepLearning.Models.DTO.MultiTextModel;
using deepLearning.Services.EmotionServices;
using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Mvc;

namespace deepLearning.Controllers.DataController
{
    [Route("api/[controller]")]
    [ApiController]
    public class MultiDataReceiveController : ControllerBase
    {
        private readonly IEmotionResultService _emotionResultService;
        private readonly ILogger<MultiDataReceiveController> _logger;

        public MultiDataReceiveController(IEmotionResultService emotionResultService, ILogger<MultiDataReceiveController> logger)
        {
            _emotionResultService = emotionResultService;
            _logger = logger;
        }

        [HttpPost("multi-data-img")]
        public IActionResult ReceiveDataImg([FromBody] VideoEmotionRequestDTO request)
        {
            Console.WriteLine("ReceiveData img actived");
            if (request == null || request.Results == null || request.Results.Count != request.FrameCount)
                return BadRequest("Invalid request data");

            _emotionResultService.SaveVideoEmotionResult(request);

            return Ok("Data img received.");
        }

        [HttpPost("multi-data-text")]
        public IActionResult ReceiveDataText([FromBody] VideoCommentEmotionRequestDTO data)
        {
            Console.WriteLine("ReceiveData text activated");

            if (data == null || string.IsNullOrEmpty(data.VideoId) || data.Results == null || !data.Results.Any())
            {
                return BadRequest("Invalid text data.");
            }

            if (data.Results.Any(r => string.IsNullOrEmpty(r.Author) || string.IsNullOrEmpty(r.Result)))
            {
                return BadRequest("Invalid author or emotion result in one or more items.");
            }

            _emotionResultService.SaveVideoCommentEmotionResult(data);

            _logger.LogInformation("Saved batch text emotion results for VideoId: {VideoId}", data.VideoId);
            return Ok(new { success = true, message = "Data text received.", fileId = data.VideoId });
        }

        [HttpPost("multi-data-audio")]
        public IActionResult ReceiveDataAudio([FromBody] MultiAudioEmotionResultDTO data)
        {
            Console.WriteLine("ReceiveData audio activated");

            if (data == null || string.IsNullOrEmpty(data.VideoId) || string.IsNullOrEmpty(data.Emotion))
            {
                return BadRequest("Invalid audio data.");
            }

            Console.WriteLine($"Received audio emotion result: VideoId={data.VideoId}, Section={data.Section}, Emotion={data.Emotion}");

            _emotionResultService.SaveMultiAudioEmotionResult(data);

            _logger.LogInformation("Saved audio emotion result: {VideoId} Section: {Section} => {Emotion}", data.VideoId, data.Section, data.Emotion);

            return Ok("Data audio received.");
        }
    }
}
