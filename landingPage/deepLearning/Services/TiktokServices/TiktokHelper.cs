using System.Text.RegularExpressions;

namespace deepLearning.Services.TiktokServices
{
    public class TiktokHelper
    {
        public string ExtractVideoId(string tiktokUrl)
        {
            if (string.IsNullOrEmpty(tiktokUrl))
            {
                return null; 
            }

            var videoMatch = Regex.Match(tiktokUrl, @"/video/(\d+)");
            if (videoMatch.Success)
            {
                return videoMatch.Groups[1].Value; 
            }

            var photoMatch = Regex.Match(tiktokUrl, @"/photo/(\d+)");
            if (photoMatch.Success)
            {
                return photoMatch.Groups[1].Value; 
            }

            return null;
        }
    }
}
