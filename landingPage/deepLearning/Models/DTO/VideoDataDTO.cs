using Newtonsoft.Json.Linq;

namespace deepLearning.Models.DTO
{
    public class VideoDataDTO
    {
        public string VideoId { get; set; }
        public object VideoInfo { get; set; }
        public List<Tuple<string, string>> Comments { get; set; }
        public EntityInfoDTO EntityInfo { get; set; }

    }
}
