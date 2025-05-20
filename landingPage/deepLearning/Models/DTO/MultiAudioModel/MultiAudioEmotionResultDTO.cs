namespace deepLearning.Models.DTO.MultiAudioModel
{
    public class MultiAudioEmotionResultDTO
    {
        public string VideoId { get; set; }
        public int Section { get; set; }
        public string Emotion { get; set; }
        public Dictionary<string, float> Probs { get; set; }
    }
}
