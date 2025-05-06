using deepLearning.Models.DTO;
using Microsoft.AspNetCore.Mvc;

namespace deepLearning.Controllers.AnalyzeFolder
{
    [Route("api/[controller]")]
    [ApiController]
    public class AnalyzeTextController : Controller
    {   
        public AnalyzeTextController()
        {
        }
        [HttpPost("comment")]
        public ActionResult<object> AnalyzeText([FromBody] TextRequest request)
        {
            Console.WriteLine("12312312312");
            if (request == null || string.IsNullOrWhiteSpace(request.Text))
            {
                return BadRequest(new { success = false, message = "Input text cannot be empty." });
            }

            return Ok(new
            {
                success = true,
                message = "Text analysis completed."
            });
        }
    }
}
