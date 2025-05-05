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
            } catch (jsonError) {
                console.error("❌ Error parsing JSON:", jsonError);
                showToast("Server returned invalid data.");
            }
        } else {
            throw new Error("No data returned from the server.");
        }
    } catch (error) {
        console.error("❌ Error:", error);
        showToast("An error occurred during analysis.");
    }
}


function validateInput(inputData, toastMessage) {
    if (!inputData || !inputData.trim()) {
        showToast(toastMessage);
        return false;
    }
    return true;
}

function analyzeSentimentComment() {
    const inputText = document.getElementById("input-text").value;
    console.log("Text input: ", inputText);  // Kiểm tra đầu vào

    if (!validateInput(inputText, "Please enter some text for analysis.")) return;

    console.log("Sending request to API...");
    analyzeSentiment("/api/analyzeText/comment", { text: inputText });
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

    if (!isSupportedUrl(url)) {
        showToast("❌ Only YouTube or Facebook URLs are supported.");
        return;
    }

    analyzeSentiment("/api/analyzeUrl/url", { url });
}

function isValidUrl(url) {
    // Kiểm tra định dạng URL
    const regex = /^(https?|ftp):\/\/[^\s/$.?#].[^\s]*$/i;
    return regex.test(url);
}

function isSupportedUrl(url) {
    try {
        const parsedUrl = new URL(url);
        const hostname = parsedUrl.hostname.toLowerCase();

        return hostname.includes("youtube.com") ||
            hostname.includes("youtu.be") ||
            hostname.includes("facebook.com") ||
            hostname.includes("fb.watch");
    } catch (error) {
        return false; 
    }
}

function analyzeSentimentImg() {
    const fileInput = document.getElementById("file-input-image");
    if (!fileInput.files || fileInput.files.length === 0) {
        showToast("Please upload an image for analysis.");
        return;
    }

    const imgData = { image: "Base64 image data or file path here" };

    analyzeSentiment("/api/analyzeImg/img", imgData);
}

function analyzeSentimentAudio() {
    const fileInput = document.getElementById("audio-input");
    if (!fileInput.files || fileInput.files.length === 0) {
        showToast("Please upload an audio file for analysis.");
        return;
    }

    const audioData = { audio: "Base64 audio data or file path here" };

    analyzeSentiment("/api/analyzeAudio/audio", audioData);
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

function showToast(message) {
    const toastContainer = document.getElementById('toast-container');
    const toast = document.createElement('div');
    toast.classList.add('toast');
    toast.innerHTML = `${message} <span class="close-btn" onclick="closeToast(this)">X</span>`;

    toastContainer.appendChild(toast);

    setTimeout(() => toast.classList.add('show'), 100);
    setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

function closeToast(toastElement) {
    const toast = toastElement.parentElement;
    toast.classList.remove('show');
    setTimeout(() => toast.remove(), 300);
}
