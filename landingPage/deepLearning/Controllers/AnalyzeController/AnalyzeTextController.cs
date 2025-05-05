using deepLearning.Models.DTO;
using deepLearning.Services.Interfaces;
using Microsoft.AspNetCore.Mvc;

namespace deepLearning.Controllers.AnalyzeFolder
{
    [Route("api/[controller]")]
    [ApiController]
    public class AnalyzeTextController : Controller
    {   
        private readonly Func<string, IAnalysisService> _analysisServiceFactory;
        public AnalyzeTextController(Func<string, IAnalysisService> analysisServiceFactory)
        {
            _analysisServiceFactory = analysisServiceFactory;
        }
        [HttpPost("comment")]
        public ActionResult<object> AnalyzeText([FromBody] TextRequest request)
        {
            Console.WriteLine("12312312312");
            if (request == null || string.IsNullOrWhiteSpace(request.Text))
            {
                return BadRequest(new { success = false, message = "Input text cannot be empty." });
            }

            var analysisService = _analysisServiceFactory("text");

            var result = analysisService.Analyze(request.Text);

            return Ok(new
            {
                success = true,
                message = "Text analysis completed.",
                sentiment = result
            });
        }
    }
}
