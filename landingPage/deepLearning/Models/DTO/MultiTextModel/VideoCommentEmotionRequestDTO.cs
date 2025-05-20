namespace deepLearning.Models.DTO.MultiTextModel
{
    public class VideoCommentEmotionRequestDTO
    {
        public string VideoId { get; set; }
        public List<CommentEmotionResultDTO> Results { get; set; }
    }
}
