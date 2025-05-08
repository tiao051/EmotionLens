using deepLearning.Models.DTO;
using Microsoft.AspNetCore.Mvc;
using Newtonsoft.Json.Linq;

namespace deepLearning.Controllers.YoutubeController
{
    [Route("api/[controller]")]
    [ApiController]
    public class YoutubeCrawlData : ControllerBase
    {   
        private readonly string apiKey = "AIzaSyArSNYq41lHEnMzzI62FHXNa5pB8SboQs4";
        public async Task<VideoDataDTO> GetVideoInfoAsync(string link)
        {
            if (string.IsNullOrEmpty(link))
                return null; 

            string videoId = ExtractVideoId(link);

            if (string.IsNullOrEmpty(videoId))
                return null;

            using (HttpClient client = new HttpClient())
            {
                // Gọi API lấy video info
                string videoUrl = $"https://www.googleapis.com/youtube/v3/videos?part=snippet,statistics&id={videoId}&key={apiKey}";
                var videoResponse = await client.GetAsync(videoUrl);
                var videoJson = await videoResponse.Content.ReadAsStringAsync();
                var videoObj = JObject.Parse(videoJson);

                // Gọi API lấy comment và replies
                List<Tuple<string, string>> allComments = new List<Tuple<string, string>>();
                string nextPageToken = null;

                do
                {
                    string commentUrl = $"https://www.googleapis.com/youtube/v3/commentThreads?part=snippet,replies&videoId={videoId}&key={apiKey}&maxResults=100";
                    if (!string.IsNullOrEmpty(nextPageToken))
                    {
                        commentUrl += $"&pageToken={nextPageToken}";
                    }

                    var commentResponse = await client.GetAsync(commentUrl);
                    var commentJson = await commentResponse.Content.ReadAsStringAsync();
                    var commentObj = JObject.Parse(commentJson);

                    if (commentObj["items"] != null && commentObj["items"].HasValues)
                    {
                        foreach (var item in commentObj["items"])
                        {
                            var topComment = item["snippet"]["topLevelComment"]["snippet"];
                            var comment = topComment["textDisplay"]?.ToString();
                            var authorName = topComment["authorDisplayName"]?.ToString();
                            if (!string.IsNullOrEmpty(comment))
                            {
                                allComments.Add(Tuple.Create(authorName, comment));
                            }

                            if (item["replies"] != null && item["replies"]["comments"] != null)
                            {
                                foreach (var reply in item["replies"]["comments"])
                                {
                                    var replySnippet = reply["snippet"];
                                    var replyText = replySnippet["textDisplay"]?.ToString();
                                    var replyAuthorName = replySnippet["authorDisplayName"]?.ToString();

                                    if (!string.IsNullOrEmpty(replyText))
                                    {
                                        allComments.Add(Tuple.Create(replyAuthorName, replyText));
                                    }
                                }
                            }
                        }
                    }

                    nextPageToken = commentObj["nextPageToken"]?.ToString();
                }
                while (!string.IsNullOrEmpty(nextPageToken));

                return new VideoDataDTO
                {
                    VideoInfo = videoObj,
                    Comments = allComments,
                    VideoId = videoId
                };
            }
        }

        private string ExtractVideoId(string link)
        {
            try
            {
                Uri uri = new Uri(link);
                var query = System.Web.HttpUtility.ParseQueryString(uri.Query);
                return query.Get("v");
            }
            catch
            {
                return null;
            }
        }
    }
}
