using deepLearning.Models.DTO;
using deepLearning.Models.DTO.MultiImageModel;
using deepLearning.Models.DTO.MultiTextModel;

namespace deepLearning.Services.EmotionServices
{
    public interface IEmotionResultService
    {
        void SaveEmotionResult(EmotionResultDTO result);
        void SaveVideoEmotionResult(VideoEmotionRequestDTO videoRequest);
        void SaveVideoCommentEmotionResult(VideoCommentEmotionRequestDTO videoRequest);
        EmotionResultDTO GetEmotionResult(string id);
        List<FrameEmotionResult> GetVideoEmotionResult(string videoId);
        List<CommentEmotionResultDTO> GetVideoCommentEmotionResult(string videoId);
    }
    public class EmotionResultsService : IEmotionResultService
    {
        private readonly Dictionary<string, EmotionResultDTO> _results = new();
        private readonly Dictionary<string, List<FrameEmotionResult>> _videoResults = new();
        private readonly Dictionary<string, List<CommentEmotionResultDTO>> _videoCommentResults = new();

        public void SaveEmotionResult(EmotionResultDTO result)
        {
            Console.WriteLine($"Save single emotion result: Id={result.Id}, Emotion={result.Emotion}");
            _results[result.Id] = result;
        }
        public EmotionResultDTO GetEmotionResult(string id)
        {
            Console.WriteLine($"id: {id}");

            if (_results.ContainsKey(id))
            {
                var result = _results[id];
                Console.WriteLine($"Found result => Id: {result.Id}, Emotion: {result.Emotion}");
                return result;
            }

            Console.WriteLine("Result not found.");
            return null;
        }
        public void SaveVideoEmotionResult(VideoEmotionRequestDTO videoRequest)
        {
            Console.WriteLine($"Save batch emotion results for VideoId={videoRequest.VideoId}");

            if (!_videoResults.ContainsKey(videoRequest.VideoId))
            {
                _videoResults[videoRequest.VideoId] = new List<FrameEmotionResult>();
            }

            foreach (var frameResult in videoRequest.Results)
            {
                _videoResults[videoRequest.VideoId].Add(frameResult);

                Console.WriteLine($"   Frame: {frameResult.Frame}, Emotion: {frameResult.Emotion}");
            }
        }

        public List<FrameEmotionResult> GetVideoEmotionResult(string videoId)
        {
            if (_videoResults.ContainsKey(videoId))
            {
                var results = _videoResults[videoId];
                Console.WriteLine($"Found {results.Count} frame results for VideoId: {videoId}");
                return results;
            }

            Console.WriteLine("Video emotion result not found.");
            return null;
        }

        public void SaveVideoCommentEmotionResult(VideoCommentEmotionRequestDTO videoRequest)
        {
            Console.WriteLine($"Save batch comment emotion results for VideoId={videoRequest.VideoId}");

            if (!_videoCommentResults.ContainsKey(videoRequest.VideoId))
            {
                _videoCommentResults[videoRequest.VideoId] = new List<CommentEmotionResultDTO>();
            }

            foreach (var commentResult in videoRequest.Results)
            {
                _videoCommentResults[videoRequest.VideoId].Add(commentResult);

                Console.WriteLine($"Author: {commentResult.Author}, Emotion: {commentResult.Result}");
            }
        }

        public List<CommentEmotionResultDTO> GetVideoCommentEmotionResult(string videoId)
        {
            if (_videoCommentResults.ContainsKey(videoId))
            {
                var results = _videoCommentResults[videoId];
                Console.WriteLine($"Found {results.Count} comment results for VideoId: {videoId}");
                return results;
            }

            Console.WriteLine("Video comment emotion result not found.");
            return null;
        }
    }
}
