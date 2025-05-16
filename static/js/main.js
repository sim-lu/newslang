// Static JS file for Newslang Word Generator

document.addEventListener('DOMContentLoaded', () => {
    console.log("Newslang Word Generator JS Loaded");

    const generateBtn = document.getElementById('generateBtn');
    const keywordsInput = document.getElementById('keywordsInput');
    const numWordsSlider = document.getElementById('numWordsSlider');
    const numWordsValueDisplay = document.getElementById('numWordsValue');
    const regularWordsOutput = document.getElementById('regularWordsOutput');
    const wildcardWordOutput = document.getElementById('wildcardWordOutput');

    function updateSliderValue() {
        if (numWordsSlider && numWordsValueDisplay) {
            numWordsValueDisplay.textContent = numWordsSlider.value;
        }
    }

    if (numWordsSlider) {
        updateSliderValue();
        numWordsSlider.addEventListener('input', updateSliderValue);
    }

    // Helper function to validate a single keyword (alphabetic)
    function isValidKeyword(keyword) {
        return /^[a-zA-Z]+$/.test(keyword);
    }

    // Helper function to clean a single keyword segment
    function cleanKeyword(segment) {
        // Trim whitespace
        let cleaned = segment.trim();
        // Remove all non-alphabetic characters
        cleaned = cleaned.replace(/[^a-zA-Z]/g, '');
        return cleaned;
    }

    if (generateBtn) {
        generateBtn.addEventListener('click', async () => {
            const rawKeywordSegments = keywordsInput.value.split(',');
            const cleanedKeywords = rawKeywordSegments.map(cleanKeyword);
            const validKeywords = cleanedKeywords.filter(k => k && isValidKeyword(k)); // isValidKeyword ensures it's not empty and purely alpha
            
            // Feedback logic based on comparison between raw segments and valid final keywords
            let userAlertMessage = "";
            if (rawKeywordSegments.map(s => s.trim()).filter(s => s).length > 0 && validKeywords.length === 0) {
                userAlertMessage = "Please enter valid keywords (letters only). All input was invalid.";
                keywordsInput.value = ""; 
            } else if (cleanedKeywords.length !== validKeywords.length || 
                       rawKeywordSegments.map(s=>s.trim()).join(',') !== validKeywords.join(',')) {
                        // This condition is a bit broad, but catches cases where cleaning/validation changed something
                if (validKeywords.length > 0) {
                    userAlertMessage = "Some input was adjusted or removed to ensure valid keywords (letters only).";
                    keywordsInput.value = validKeywords.join(', ');
                } else { // Handles cases like "b4d, 3!c" becoming empty after cleaning
                    userAlertMessage = "Please enter valid keywords (letters only). All input was invalid after cleaning.";
                    keywordsInput.value = ""; 
                }
            }

            if (userAlertMessage) {
                alert(userAlertMessage);
                if (validKeywords.length === 0) return; // Stop if no valid keywords after alert
            }
            
            if (validKeywords.length === 0) { // Final check if somehow bypassed previous alerts
                alert("Please enter at least one valid keyword (letters only, comma-separated).");
                return;
            }

            const numWords = parseInt(numWordsSlider.value, 10);
            const maxWords = parseInt(numWordsSlider.max, 10); // Use slider's max attribute

            if (isNaN(numWords) || numWords < parseInt(numWordsSlider.min, 10) || numWords > maxWords) {
                alert(`Please select a number of words between ${numWordsSlider.min} and ${maxWords}.`);
                return;
            }

            regularWordsOutput.innerHTML = '<p>Generating...</p>';
            wildcardWordOutput.innerHTML = '';

            try {
                const payload = {
                    keywords: validKeywords, // Send only valid keywords
                    num_to_generate: numWords
                };

                const response = await fetch('/api/generate', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(payload)
                });
                
                if (!response.ok) {
                    let errorMsg = `HTTP error! status: ${response.status}`;
                    try {
                        const errorData = await response.json();
                        errorMsg = errorData.error || errorMsg;
                    } catch (e) {
                        errorMsg = response.statusText || errorMsg;
                    }
                    throw new Error(errorMsg);
                }

                const data = await response.json();

                if (data.regular_words && data.regular_words.length > 0) {
                    let html = '<ul>';
                    data.regular_words.forEach(word => {
                        html += `<li>${escapeHTML(word)}</li>`;
                    });
                    html += '</ul>';
                    regularWordsOutput.innerHTML = html;
                } else {
                    regularWordsOutput.innerHTML = '<p>(No regular words generated)</p>';
                }

                if (data.wildcard_word) {
                    wildcardWordOutput.innerHTML = `<p><strong>Wildcard:</strong> ${escapeHTML(data.wildcard_word)}</p>`;
                } else {
                    wildcardWordOutput.innerHTML = '';
                }

            } catch (error) {
                console.error('Error generating words:', error);
                regularWordsOutput.innerHTML = `<p style="color: red;">Error: ${escapeHTML(error.message)}</p>`;
                wildcardWordOutput.innerHTML = '';
            }
        });
    }
});

function escapeHTML(str) {
    if (str === null || str === undefined) return '';
    return str.toString()
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#039;');
} 