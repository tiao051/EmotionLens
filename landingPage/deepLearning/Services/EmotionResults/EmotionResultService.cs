using deepLearning.Models.DTO;

namespace deepLearning.Services.EmotionResults
{
    public interface IEmotionResultService
    {
        void SetEmotionResult(EmotionResultDTO emotionResult);
        EmotionResultDTO GetEmotionResult();
    }
    public class EmotionResultService : IEmotionResultService
    {
        private EmotionResultDTO _emotionResult;
        public void SetEmotionResult(EmotionResultDTO emotionResult)
        {
            _emotionResult = emotionResult;
        }
        public EmotionResultDTO GetEmotionResult()
        {
            return _emotionResult;
        }
    }
}
