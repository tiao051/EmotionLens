using deepLearning.Services.Interfaces;
using Microsoft.AspNetCore.Mvc;

namespace deepLearning.Controllers.AnalyzeController
{
    public class AnalyzeAudioController : Controller
    {
        private readonly IAnalysisService _sentimentAnalyzer;
        public AnalyzeAudioController(IAnalysisService sentimentAnalyzer)
        {
            _sentimentAnalyzer = sentimentAnalyzer;
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
