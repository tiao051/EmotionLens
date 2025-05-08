using deepLearning.Models.DTO;
using deepLearning.Services.EmotionServices;
using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Mvc;

namespace deepLearning.Controllers.DataController
{
    [Route("api/[controller]")]
    [ApiController]
    public class DataReceiveController : ControllerBase
    {
        private readonly IEmotionResultService _emotionResultService;
        private readonly ILogger<DataReceiveController> _logger;

        public DataReceiveController(IEmotionResultService emotionResultService, ILogger<DataReceiveController> logger)
        {
            _emotionResultService = emotionResultService;
            _logger = logger;
        }

        [HttpPost("data-img")]
        public IActionResult ReceiveDataImg([FromBody] EmotionResultDTO data)
        {
            Console.WriteLine("ReceiveData img actived");
            if (data == null || string.IsNullOrEmpty(data.Id) || string.IsNullOrEmpty(data.Emotion))
            {
                return BadRequest("Invalid img data.");
            }

            _emotionResultService.SaveEmotionResult(data);

            _logger.LogInformation("Saved img emotion result: {Id} => {Emotion}", data.Id, data.Emotion);
            return Ok("Data img received.");
        }
        [HttpPost("data-text")]
        public IActionResult ReceiveDataText([FromBody] EmotionResultDTO data)
        {
            Console.WriteLine("ReceiveData text actived");
            if (data == null || string.IsNullOrEmpty(data.Id) || string.IsNullOrEmpty(data.Emotion))
            {
                return BadRequest("Invalid text data.");
            }

            _emotionResultService.SaveEmotionResult(data);

            _logger.LogInformation("Saved text emotion result: {Id} => {Emotion}", data.Id, data.Emotion);
            return Ok("Data text received.");
        }

    }
}
