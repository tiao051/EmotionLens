using System.Text.RegularExpressions;
using System.Web;

namespace deepLearning.Services.DataPreprocessing
{
    public class ProcessingData
    {
        private string Clean_icon(string comment)
        {
            if (string.IsNullOrEmpty(comment))
                return comment;

            // 1. Xóa emoji Unicode
            string noEmoji = Regex.Replace(comment, @"[\uD800-\uDBFF][\uDC00-\uDFFF]", "");

            // 2. Xóa các ký tự symbol unicode: trái tim, ngôi sao, tia chớp, v.v...
            noEmoji = Regex.Replace(noEmoji, @"[\u2600-\u27BF]", ""); // Symbol như ♥️ ✨ ⚡ ★ ...

            // 3. Xóa các ký tự đặc biệt khác nếu cần (bổ sung thêm các block unicode khác)
            noEmoji = Regex.Replace(noEmoji, @"[\uFE00-\uFE0F]", ""); // emoji variation selectors
            noEmoji = Regex.Replace(noEmoji, @"[\u2000-\u206F]", ""); // dấu câu, ký tự điều khiển

            // 4. Chuẩn hóa khoảng trắng
            string cleaned = Regex.Replace(noEmoji, @"\s+", " ").Trim();

            return cleaned;
        }

        // Xoá thẻ HTML
        // Xoá khoảng trắng thừa (bao gồm khoảng trắng ở đầu, cuối và giữa các từ)
        private string Clean_HTML_Space(string comment)
        {
            if (string.IsNullOrEmpty(comment))
                return comment;

            // Xoá thẻ HTML
            string noHtmlTags = Regex.Replace(comment, "<.*?>", string.Empty);

            // Xoá khoảng trắng thừa (bao gồm khoảng trắng ở đầu, cuối và giữa các từ)
            string cleanedString = Regex.Replace(noHtmlTags, @"\s+", " ").Trim();

            return cleanedString;
        }

        public string clean_TagTime(string comment)
        {
            // Xoá các chuỗi thời gian dạng "mm:ss" hoặc "hh:mm:ss"
            // Biểu thức chính quy tìm các chuỗi như "5:30", "10:45", "12:05:30"
            string noTimeTags = Regex.Replace(comment, @"(\b\d{1,2}(:\d{2}){1,2}\b)", string.Empty);

            return noTimeTags;
        }

        public string Clean_UserTag(string comment)
        {
            if (string.IsNullOrEmpty(comment))
                return comment;

            // Biểu thức chính quy để tìm tất cả các chuỗi bắt đầu với "@", tiếp theo là chữ cái, số hoặc dấu gạch dưới, bao gồm cả trường hợp @@
            string noUserTags = Regex.Replace(comment, @"@+\w+", string.Empty);

            return noUserTags;
        }

        public string NormalizeComment(string comment)
        {
            string cleanedComment = Clean_icon(comment);

            cleanedComment = cleanedComment.ToLower();
            cleanedComment = clean_TagTime(cleanedComment); // clear tag thời gian trong video (VD: "5:30 ôi anh đẹp quá")
            cleanedComment = Clean_UserTag(cleanedComment); // clear tag ID (VD: @@duongvietthang4094 khen trước xem sau)
            cleanedComment = HttpUtility.HtmlDecode(cleanedComment);
            cleanedComment = Clean_HTML_Space(cleanedComment); // Xoá thẻ HTML // Xoá khoảng trắng thừa (bao gồm khoảng trắng ở đầu, cuối và giữa các từ)
            return cleanedComment;
        }
    }
}
