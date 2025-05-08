using deepLearning.Models.DTO;

namespace deepLearning.Services.EmotionServices
{
    public interface IEmotionResultService
    {
        void SaveEmotionResult(EmotionResultDTO result);
        EmotionResultDTO GetEmotionResult(string id);
    }
    public class EmotionResultsService : IEmotionResultService
    {
        private readonly Dictionary<string, EmotionResultDTO> _results = new();

        public void SaveEmotionResult(EmotionResultDTO result)
        {
            Console.WriteLine($"Save emotion results: {result}");
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
    }
}
