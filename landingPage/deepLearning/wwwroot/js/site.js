async function analyzeSentiment(endpoint, data) {
    try {
        const response = await fetch(endpoint, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(data)
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const textData = await response.text(); 
        if (textData) {
            try {
                const result = JSON.parse(textData);
                console.log("Result:", result);
                return result;
            } catch (jsonError) {
                console.error("❌ Error parsing JSON:", jsonError);
                showToast("Server returned invalid data.");
                return null;
            }
        } else {
            throw new Error("No data returned from the server.");
        }
    } catch (error) {
        console.error("❌ Error:", error);
        showToast("An error occurred during analysis.");
        return null;
    }
}
function analyzeSentimentComment() {
    const inputText = document.getElementById("input-text").value;
    console.log("Text input: ", inputText); 

    if (!validateInput(inputText, "Please enter some text for analysis."))
        return;

    console.log("Sending request to API...");
    fetch("/api/analyzeText/comment", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ text: inputText }),
    })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showToast(data.message, 'success');  
                console.log(data.fileId);
                fetchTextEmotionResultPolling(data.fileId);
            } else {
                showToast(data.message, 'error'); 
            }
        })
        .catch(error => {
            showToast("Error: " + error.message);
        });
}
function fetchTextEmotionResultPolling(fileId, maxAttempts = 10, delayMs = 2000) {
    let attempts = 0;

    const poll = () => {
        console.log("api called");
        fetch(`/api/analyzeText/get-text-emotion-result?id=${fileId}`)
            .then(response => response.json())
            .then(data => {
                console.log("Polling response:", data);

                if (data && data.success && data.data && data.data.emotion) {
                    const emotion = data.data.emotion || "No emotion detected";
                    console.log("✅ Detected Emotion:", emotion);
                    showToast(`Detected Emotion: ${emotion}`, 'success');
                } else {
                    if (attempts < maxAttempts) {
                        attempts++;
                        console.log(`⏳ Attempt ${attempts}: result not ready, retrying in ${delayMs}ms...`);
                        setTimeout(poll, delayMs);
                    } else {
                        console.log("❌ Emotion result not available after multiple attempts.");
                        showToast("Emotion result not available yet. Try again later.", 'error');
                    }
                }
            })
            .catch(error => {
                console.error("❌ Error fetching emotion result:", error);
                showToast("Error while checking emotion result.");
            });
    };

    poll();
}
function analyzeSentimentImg() {
    const fileInput = document.getElementById("file-input-image");
    if (!fileInput.files || fileInput.files.length === 0) {
        showToast("Please upload an image for analysis.");
        return;
    }

    const formData = new FormData();
    formData.append("image", fileInput.files[0]);

    // Gọi API để upload hình ảnh
    fetch("/api/analyzeImg/img", {
        method: "POST",
        body: formData,
    })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showToast(data.message, 'success');
                console.log(data.fileId);
                fetchEmotionResultPolling(data.fileId);
            } else {
                showToast(data.message, 'error'); 
            }
        })
        .catch(error => {
            showToast("Error: " + error.message);
        });
}
function fetchEmotionResultPolling(fileId, maxAttempts = 10, delayMs = 2000) {
    let attempts = 0;

    const poll = () => {
        fetch(`/api/analyzeImg/get-emotion-result?id=${fileId}`)
            .then(response => response.json())
            .then(data => {
                console.log("Polling response:", data);

                if (data && data.success && data.data && data.data.emotion) {
                    const emotion = data.data.emotion || "No emotion detected";
                    console.log("✅ Detected Emotion:", emotion);
                    showToast(`Detected Emotion: ${emotion}`, 'success');
                } else {
                    if (attempts < maxAttempts) {
                        attempts++;
                        console.log(`⏳ Attempt ${attempts}: result not ready, retrying in ${delayMs}ms...`);
                        setTimeout(poll, delayMs);
                    } else {
                        console.log("❌ Emotion result not available after multiple attempts.");
                        showToast("Emotion result not available yet. Try again later.", 'error');
                    }
                }
            })
            .catch(error => {
                console.error("❌ Error fetching emotion result:", error);
                showToast("Error while checking emotion result.");
            });
    };

    poll();
}
function analyzeSentimentAudio() {
    const fileInput = document.getElementById("audio-input");
    if (!fileInput.files || fileInput.files.length === 0) {
        showToast("Please upload an audio file for analysis.", 'error');
        return;
    }

    const formData = new FormData();
    formData.append("audioFile", fileInput.files[0]); 

    fetch("/api/analyzeAudio/upload-audio", {  
        method: "POST",
        body: formData,
    })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showToast(data.message, 'success');
                console.log(data.fileId);
                fetchAudioEmotionResultPolling(data.fileId);
            } else {
                showToast(data.message, 'error');
            }
        })
        .catch(error => {
            showToast("Error: " + error.message, 'error');
        });
}
function fetchAudioEmotionResultPolling(fileId, maxAttempts = 10, delayMs = 2000) {
    let attempts = 0;

    const poll = () => {
        fetch(`/api/analyzeAudio/get-audio-emotion-result?id=${fileId}`)
            .then(response => response.json())
            .then(data => {
                console.log("Polling response:", data);

                if (data && data.success && data.data && data.data.emotion) {
                    const emotion = data.data.emotion || "No emotion detected";
                    console.log("✅ Detected Emotion:", emotion);
                    showToast(`Detected Emotion: ${emotion}`, 'success');
                } else {
                    if (attempts < maxAttempts) {
                        attempts++;
                        console.log(`⏳ Attempt ${attempts}: result not ready, retrying in ${delayMs}ms...`);
                        setTimeout(poll, delayMs);
                    } else {
                        console.log("❌ Emotion result not available after multiple attempts.");
                        showToast("Emotion result not available yet. Try again later.", 'error');
                    }
                }
            })
            .catch(error => {
                console.error("❌ Error fetching emotion result:", error);
                showToast("Error while checking emotion result.");
            });
    };

    poll();
}
function validateInput(inputData, toastMessage) {
    if (!inputData || !inputData.trim()) {
        showToast(toastMessage);
        return false;
    }
    return true;
}
function analyzeSentimentUrl() {
    const url = document.getElementById("input-url").value.trim();

    if (!url) {
        showToast("❌ URL is required.");
        return;
    }

    if (!isValidUrl(url)) {
        showToast("❌ Invalid URL format.");
        return;
    }

    if (isYouTubeUrl(url)) {
        fetch("/api/analyzeUrl/youtube", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ url })
        })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    console.log("FileId:", data.fileId);
                    // Call the function to fetch multi-emotion data with fileId
                    fetchMultiEmotionData(data.fileId);
                } else {
                    showToast(data.message || "Error analyzing the URL.", 'error');
                }
            })
            .catch(error => {
                console.error("Error:", error);
                showToast("Error analyzing the URL: " + error.message, 'error');
            });
    } else if (isTikTokUrl(url)) {
        fetch("/api/analyzeUrl/tiktok", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ url })
        })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    console.log("FileId:", data.videoId);
                    fetchMultiEmotionData(data.videoId);
                } else {
                    showToast(data.message || "Error analyzing the URL.", 'error');
                }
            })
            .catch(error => {
                console.error("Error:", error);
                showToast("Error analyzing the URL: " + error.message, 'error');
            });
    } else {
        showToast("❌ Only YouTube or TikTok URLs are supported.");
    }
}
function isValidUrl(url) {
    const pattern = /^(https?):\/\/[^\s$.?#].[^\s]*$/i;
    return pattern.test(url);
}


function isYouTubeUrl(url) {
    try {
        const parsedUrl = new URL(url);
        const host = parsedUrl.hostname.toLowerCase();
        return host.includes("youtube.com") || host.includes("youtu.be");
    } catch (e) {
        return false;
    }
}

function isTikTokUrl(url) {
    try {
        const parsedUrl = new URL(url);
        return parsedUrl.hostname.toLowerCase().includes("tiktok.com");
    } catch (e) {
        return false;
    }
}

document.addEventListener('DOMContentLoaded', function () {
    const analyzeBtn = document.getElementById("analyze-cmt-btn");
    const analyzeUrlBtn = document.getElementById("analyze-url-btn");
    const analyzeImgBtn = document.getElementById("analyze-image-btn");
    const analyzeAudioBtn = document.getElementById("analyze-audio-btn");

    if (analyzeBtn) analyzeBtn.addEventListener("click", analyzeSentimentComment);
    if (analyzeUrlBtn) analyzeUrlBtn.addEventListener("click", analyzeSentimentUrl);
    if (analyzeImgBtn) analyzeImgBtn.addEventListener("click", analyzeSentimentImg);
    if (analyzeAudioBtn) analyzeAudioBtn.addEventListener("click", analyzeSentimentAudio);
});
const toastQueue = []; 
let isToastVisible = false; 

function showToast(message, type = 'error') {
    toastQueue.push({ message, type });

    if (!isToastVisible) {
        displayNextToast();
    }
}

function displayNextToast() {
    if (toastQueue.length === 0) {
        isToastVisible = false; 
        return;
    }

    isToastVisible = true;
    const { message, type } = toastQueue.shift();
    const toastContainer = document.getElementById('toast-container');
    const toast = document.createElement('div');
    toast.classList.add('toast');

    // Đặt màu sắc dựa trên loại thông báo
    if (type === 'success') {
        toast.style.backgroundColor = '#4CAF50'; 
    } else if (type === 'warning') {
        toast.style.backgroundColor = '#FF9800'; 
    } else {
        toast.style.backgroundColor = '#f44336'; 
    }

    toast.innerHTML = `${message}`;
    toastContainer.appendChild(toast);

    // Hiển thị toast
    setTimeout(() => toast.classList.add('show'), 100);

    // Ẩn toast sau 3 giây và hiển thị toast tiếp theo
    setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => {
            toast.remove();
            displayNextToast(); // Hiển thị toast tiếp theo trong hàng đợi
        }, 300);
    }, 3000);
}

function fetchMultiEmotionData(videoId) {
    showToast("Fetching emotion data...", "warning");

    fetchMultiEmotionResultPolling(videoId);
}

function fetchMultiEmotionResultPolling(videoId, maxAttempts = 20, delayMs = 3000) {
    let attempts = 0;
    let results = { text: null, audio: null, image: null };

    const poll = () => {
        console.log(`Polling attempt ${attempts + 1}: /api/DisplayEmotion/get-multi-emotion-result?id=${videoId}`);

        fetch(`/api/DisplayEmotion/get-multi-emotion-result?id=${encodeURIComponent(videoId)}`)
            .then(response => response.json())
            .then(data => {
                console.log("Polling response:", data);

                if (data && data.success && data.data) {
                    // Update results with available data
                    results.text = results.text || data.data.text;
                    results.audio = results.audio || data.data.audio;
                    results.image = results.image || data.data.image;

                    // Check if all three types of data are available
                    if (results.text && results.audio && results.image) {
                        console.log("✅ All multi-emotion results are ready");
                        showToast("All emotion analysis results retrieved successfully!", "success");
                        return;
                    }
                }

                if (attempts < maxAttempts) {
                    attempts++;
                    console.log(`⏳ Attempt ${attempts}: result not ready, retrying in ${delayMs}ms...`);
                    setTimeout(poll, delayMs);
                } else {
                    console.log("❌ Emotion result not fully available after multiple attempts.");
                    showToast("Emotion analysis results are partially available. Please check the available data.", "warning");
                    console.log("Available results:", results);
                }
            })
            .catch(error => {
                console.error("❌ Error fetching multi-emotion result:", error);
                showToast("Error while retrieving emotion analysis results: " + error.message, "error");
            });
    };
    poll();
}
