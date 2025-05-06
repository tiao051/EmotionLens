using deepLearning.Services.Interfaces;
using deepLearning.Services.RabbitMQServices.ImgServices;
using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Mvc;
using Microsoft.Extensions.Logging;

namespace deepLearning.Controllers.AnalyzeController
{
    [Route("api/[controller]")]
    [ApiController]
    public class AnalyzeImgController : ControllerBase
    {
        private readonly Func<string, IAnalysisService> _analysisServiceFactory;
        private readonly ImgManager _imgManager;
        private readonly ILogger<AnalyzeImgController> _logger;

        public AnalyzeImgController(Func<string, IAnalysisService> sentimentAnalyzer, ImgManager imgManager, ILogger<AnalyzeImgController> logger)
        {
            _analysisServiceFactory = sentimentAnalyzer;
            _imgManager = imgManager;
            _logger = logger;
            _logger.LogInformation(">>> AnalyzeImgController initialized");
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

                await _imgManager.PublishFilePathAsync(savedPath);
                _logger.LogInformation("Image file has been created and sent successfully.");

                return Ok(new
                {
                    success = true,
                    message = "Image file created and sent successfully.",
                    savedPath = savedPath
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
    }
}
