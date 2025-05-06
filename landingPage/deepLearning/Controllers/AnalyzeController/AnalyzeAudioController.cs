using Microsoft.AspNetCore.Mvc;

namespace deepLearning.Controllers.AnalyzeController
{
    public class AnalyzeAudioController : Controller
    {
        public AnalyzeAudioController()
        {
        }
        [HttpPost("audio")]
        public JsonResult AnalyzeAudio()
        {
            var data = new
            {
                success = true,
                message = "Received image data",
                sample = new { id = 3, title = "test audio!" }
            };

            return new JsonResult(data);
        }
    }
}
