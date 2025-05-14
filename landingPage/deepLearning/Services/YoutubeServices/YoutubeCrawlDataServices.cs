using deepLearning.Configurations;
using deepLearning.Models.DTO;
using Microsoft.Extensions.Options;
using Newtonsoft.Json.Linq;
using System.Text.RegularExpressions;
using System.Web;

namespace deepLearning.Services.YoutubeServices
{
    public class YoutubeCrawlDataServices
    {
        private readonly string _apiKey;
        private readonly string _kgApiKey;

        public YoutubeCrawlDataServices(IOptions<SecretKeyConfig> config)
        {
            _apiKey = config.Value.ApiKey;
            _kgApiKey = config.Value.Knowledge_Graph_Search_API;
        }

        public async Task<VideoDataDTO> GetVideoDataAsync(string link)
        {
            if (string.IsNullOrEmpty(link)) 
                return null;

            string videoId = ExtractVideoId(link);

            if (string.IsNullOrEmpty(videoId)) 
                return null;

            using (HttpClient client = new HttpClient())
            {
                // Lấy thông tin video
                string videoUrl = $"https://www.googleapis.com/youtube/v3/videos?part=snippet,statistics&id={videoId}&key={_apiKey}";
                var videoResponse = await client.GetAsync(videoUrl);

                if (!videoResponse.IsSuccessStatusCode)
                    return null;

                var videoJson = await videoResponse.Content.ReadAsStringAsync();
                var videoObj = JObject.Parse(videoJson);

                string rawChannelTitle = videoObj["items"]?[0]?["snippet"]?["channelTitle"]?.ToString();

                Console.WriteLine($"Raw channel title: {rawChannelTitle}");

                string cleanedChannelTitle = CleanChannelTitle(rawChannelTitle);

                Console.WriteLine($"Cleaned channel title: {cleanedChannelTitle}");

                // Gọi Knowledge Graph API để phân loại
                var entityInfo = await GetEntityCategoryAsync(cleanedChannelTitle);

                //Lấy comment và replies
                List<Tuple<string, string>> allComments = new List<Tuple<string, string>>();
                string nextPageToken = null;

                do
                {
                    string commentUrl = $"https://www.googleapis.com/youtube/v3/commentThreads?part=snippet,replies&videoId={videoId}&key={_apiKey}&maxResults=100";

                    if (!string.IsNullOrEmpty(nextPageToken))
                    {
                        commentUrl += $"&pageToken={nextPageToken}";
                    }

                    var commentResponse = await client.GetAsync(commentUrl);
                    if (!commentResponse.IsSuccessStatusCode)
                        break;

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

                Console.WriteLine("Entity Info: ");
                if (entityInfo != null)
                {
                    Console.WriteLine($"Entity Name: {entityInfo.EntityName}");
                    Console.WriteLine($"Entity Description: {entityInfo.Description}");
                }
                else
                {
                    Console.WriteLine("Entity Info is null.");
                }
                return new VideoDataDTO
                {
                    VideoId = videoId,
                    VideoInfo = videoObj,
                    Comments = allComments,
                    EntityInfo = entityInfo ?? new EntityInfoDTO
                    {
                        EntityName = "Unknown",
                        Description = "No entity found"
                    }
                };
            }
        }
        //public async Task<List<Tuple<string, string>>> GetYouTubeCommentsAsync(string videoId, string apiKey)
        //{
        //    List<Tuple<string, string>> allComments = new List<Tuple<string, string>>();
        //    string nextPageToken = null;

        //    using (HttpClient client = new HttpClient())
        //    {
        //        do
        //        {
        //            // Tạo URL để gọi API
        //            string commentUrl = $"https://www.googleapis.com/youtube/v3/commentThreads?part=snippet,replies&videoId={videoId}&key={apiKey}&maxResults=100";

        //            // Nếu có nextPageToken, thêm vào URL để lấy trang tiếp theo
        //            if (!string.IsNullOrEmpty(nextPageToken))
        //            {
        //                commentUrl += $"&pageToken={nextPageToken}";
        //            }

        //            // Gửi yêu cầu GET tới API
        //            var commentResponse = await client.GetAsync(commentUrl);
        //            if (!commentResponse.IsSuccessStatusCode)
        //                break;

        //            var commentJson = await commentResponse.Content.ReadAsStringAsync();
        //            var commentObj = JObject.Parse(commentJson);

        //            // Xử lý các comment chính (top-level comments)
        //            if (commentObj["items"] != null && commentObj["items"].HasValues)
        //            {
        //                foreach (var item in commentObj["items"])
        //                {
        //                    var topComment = item["snippet"]["topLevelComment"]["snippet"];
        //                    var comment = topComment["textDisplay"]?.ToString();
        //                    var authorName = topComment["authorDisplayName"]?.ToString();
        //                    if (!string.IsNullOrEmpty(comment))
        //                    {
        //                        allComments.Add(Tuple.Create(authorName, comment));
        //                    }

        //                    // Xử lý các replies nếu có
        //                    if (item["replies"] != null && item["replies"]["comments"] != null)
        //                    {
        //                        foreach (var reply in item["replies"]["comments"])
        //                        {
        //                            var replySnippet = reply["snippet"];
        //                            var replyText = replySnippet["textDisplay"]?.ToString();
        //                            var replyAuthorName = replySnippet["authorDisplayName"]?.ToString();

        //                            if (!string.IsNullOrEmpty(replyText))
        //                            {
        //                                allComments.Add(Tuple.Create(replyAuthorName, replyText));
        //                            }
        //                        }
        //                    }
        //                }
        //            }

        //            // Lấy nextPageToken để tiếp tục gọi API nếu còn trang tiếp theo
        //            nextPageToken = commentObj["nextPageToken"]?.ToString();
        //        }
        //        while (!string.IsNullOrEmpty(nextPageToken));
        //    }

        //    return allComments;
        //}

        private async Task<EntityInfoDTO> GetEntityCategoryAsync(string entityName)
        {
            Console.WriteLine("Chay vao day roi");
            if (string.IsNullOrEmpty(entityName)) return null;

            string baseUrl = "https://kgsearch.googleapis.com/v1/entities:search";
            string url = $"{baseUrl}?query={Uri.EscapeDataString(entityName)}&key={_kgApiKey}&limit=1";

            using (HttpClient client = new HttpClient())
            {
                var response = await client.GetAsync(url);

                // Check if the request was successful
                if (!response.IsSuccessStatusCode)
                {
                    Console.WriteLine("Error in Knowledge Graph API request: " + response.StatusCode);
                    return null;
                }

                string responseBody = await response.Content.ReadAsStringAsync();

                var jsonResponse = JObject.Parse(responseBody);

                var item = jsonResponse["itemListElement"]?.FirstOrDefault()?["result"];
                if (item == null)
                {
                    Console.WriteLine("No entity found for: " + entityName);
                    return null;
                }
                Console.WriteLine("Ra kq ne");
                // Return the parsed entity data
                return new EntityInfoDTO
                {
                    EntityName = item["name"]?.ToString(),
                    Description = item["description"]?.ToString()
                };
            }
        }
        public string CleanChannelTitle(string rawTitle)
        {
            if (string.IsNullOrWhiteSpace(rawTitle)) return rawTitle;

            string noVevo = rawTitle.Replace("VEVO", "", StringComparison.OrdinalIgnoreCase).Trim();

            if (noVevo.Contains(" "))
                return noVevo;

            string withSpaces = Regex.Replace(noVevo, @"(?<!^)([A-Z])", " $1").Trim();

            return withSpaces;
        }

        private string ExtractVideoId(string link)
        {
            try
            {
                Uri uri = new Uri(link);
                var query = HttpUtility.ParseQueryString(uri.Query);
                return query.Get("v");
            }
            catch
            {
                return null;
            }
        }
    }
}
