using deepLearning.Services.Interfaces;

namespace deepLearning.Services.SentimentService
{
    public class TextSentimentAnalyzer : IAnalysisService
    {
        public string Analyze(string text)
        {   
            Console.WriteLine("text");
            if (text.Contains("happy") || text.Contains("good")) return "Positive";
            if (text.Contains("sad") || text.Contains("bad")) return "Negative";
            return "Neutral";
        }
    }
}
