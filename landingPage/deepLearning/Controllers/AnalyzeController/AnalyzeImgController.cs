using deepLearning.Services.EmotionServices;
using deepLearning.Services.RabbitMQServices.ImgServices;
using DocumentFormat.OpenXml.Office2010.Excel;
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
                    message = "Image file created and sent successfully.",
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

            var emotionResult = _emotionResultService.GetEmotionResult(id);

            _logger.LogInformation("Checking for emotion result with id: {Id}", id);

            Console.WriteLine($"emotionResult:{emotionResult}");
            if (emotionResult == null)
            {
                return NotFound(new
                {
                    success = false,
                    message = "Emotion img 123 result not found."
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
