using Newtonsoft.Json.Linq;

namespace deepLearning.Models.DTO
{
    public class VideoDataDTO
    {
        public JObject VideoInfo { get; set; }
        public List<Tuple<string, string>> Comments { get; set; }
        public string VideoId { get; set; }
    }
}
