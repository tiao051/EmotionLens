namespace deepLearning.Models.DTO.MultiImageModel
{
    public class VideoEmotionRequestDTO
    {
        public string VideoId { get; set; }
        public int FrameCount { get; set; }
        public List<FrameEmotionResult> Results { get; set; }
    }
}
