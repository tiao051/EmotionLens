using deepLearning.Services.Interfaces;
using Microsoft.AspNetCore.Mvc;

namespace deepLearning.Controllers.AnalyzeController
{
    public class AnalyzeImgController : Controller
    {
        private readonly IAnalysisService _sentimentAnalyzer;
        public AnalyzeImgController(IAnalysisService sentimentAnalyzer)
        {
            _sentimentAnalyzer = sentimentAnalyzer;
        }
        [HttpPost("img")]
        public JsonResult AnalyzeImg()
        {
            var data = new
            {
                success = true,
                message = "Received image data",
                sample = new { id = 3, title = "test image!" }
            };

            return new JsonResult(data);
        }
    }
}
