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

        [HttpPost("data")]
        public IActionResult ReceiveData([FromBody] EmotionResultDTO data)
        {
            Console.WriteLine("ReceiveData actived");
            if (data == null || string.IsNullOrEmpty(data.Id) || string.IsNullOrEmpty(data.Emotion))
            {
                return BadRequest("Invalid data.");
            }

            _emotionResultService.SaveEmotionResult(data);

            _logger.LogInformation("Saved emotion result: {Id} => {Emotion}", data.Id, data.Emotion);
            return Ok("Data received.");
        }
    }
}
