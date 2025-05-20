document.addEventListener('DOMContentLoaded', () => {
    const keywordsInput = document.getElementById('keywords');
    const numWordsInput = document.getElementById('numWords');
    const numWordsValueDisplay = document.getElementById('numWordsValue');
    const generateBtn = document.getElementById('generateBtn');
    const rerollBtn = document.getElementById('rerollBtn');
    const copyAllBtn = document.getElementById('copyAllBtn');
    const regularWordsOutput = document.getElementById('regularWordsOutput');
    const wildcardWordOutput = document.getElementById('wildcardWordOutput');
    const loadingSpinner = document.getElementById('loadingSpinner');

    let lastKeywords = [];
    let lastNumToGenerate = 5;

    // Update number display when slider changes
    if (numWordsInput && numWordsValueDisplay) {
        numWordsValueDisplay.textContent = numWordsInput.value;
        numWordsInput.addEventListener('input', () => {
            numWordsValueDisplay.textContent = numWordsInput.value;
        });
    }

    // Function to clean and validate keywords
    function getValidKeywords() {
        const rawKeywords = keywordsInput.value.trim();
        if (!rawKeywords) {
            alert('Please enter at least one keyword.');
            return null;
        }
        // Split by comma, trim, filter out empty and non-alphabetic strings
        const keywordsArray = rawKeywords.split(',')
            .map(kw => kw.trim().toLowerCase())
            .filter(kw => kw.length > 0 && /^[a-zA-Z]+$/.test(kw));
        
        if (keywordsArray.length === 0) {
            alert('Invalid keywords. Please use only letters and commas to separate multiple keywords.');
            return null;
        }
        return keywordsArray;
    }

    async function fetchGeneratedWords(keywords, numToGenerate) {
        loadingSpinner.style.display = 'block';
        generateBtn.disabled = true;
        rerollBtn.style.display = 'none';
        copyAllBtn.style.display = 'none';
        regularWordsOutput.innerHTML = '';
        wildcardWordOutput.innerHTML = '';

        try {
            const response = await fetch('/api/generate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ keywords, num_to_generate: numToGenerate }),
            });

            if (!response.ok) {
                const errorData = await response.json().catch(() => null);
                throw new Error(errorData?.error || `HTTP error! Status: ${response.status}`);
            }

            const data = await response.json();
            displayResults(data);
            lastKeywords = keywords;
            lastNumToGenerate = numToGenerate;
            rerollBtn.style.display = 'inline-block'; // Show re-roll button after successful generation

        } catch (error) {
            console.error('Error generating words:', error);
            regularWordsOutput.innerHTML = `<p style="color: red;">Error: ${error.message}</p>`;
        } finally {
            loadingSpinner.style.display = 'none';
            generateBtn.disabled = false;
        }
    }

    function displayResults(data) {
        regularWordsOutput.innerHTML = ''; // Clear previous regular words
        if (data.regular_words && data.regular_words.length > 0) {
            const ul = document.createElement('ul');
            data.regular_words.forEach(word => {
                const li = document.createElement('li');
                li.textContent = word;
                ul.appendChild(li);
            });
            regularWordsOutput.appendChild(ul);
        } else {
            regularWordsOutput.innerHTML = '<p>No regular words generated. Try different keywords!</p>';
        }

        wildcardWordOutput.innerHTML = ''; // Clear previous wildcard word
        if (data.wildcard_word) {
            wildcardWordOutput.innerHTML = `<p><strong>Wildcard:</strong> ${data.wildcard_word}</p>`;
        } else {
            wildcardWordOutput.innerHTML = '<p>No wildcard generated this time.</p>';
        }
        
        if ((data.regular_words && data.regular_words.length > 0) || data.wildcard_word) {
            copyAllBtn.style.display = 'inline-block';
        } else {
            copyAllBtn.style.display = 'none';
        }
    }

    if (generateBtn) {
        generateBtn.addEventListener('click', () => {
            const keywords = getValidKeywords();
            if (!keywords) return;
            const numToGenerate = parseInt(numWordsInput.value, 10);
            fetchGeneratedWords(keywords, numToGenerate);
        });
    }

    if (rerollBtn) {
        rerollBtn.addEventListener('click', () => {
            if (lastKeywords.length > 0) {
                fetchGeneratedWords(lastKeywords, lastNumToGenerate);
            } else {
                alert('Generate some words first before re-rolling!');
            }
        });
    }
    
    if (copyAllBtn) {
        copyAllBtn.addEventListener('click', () => {
            let textToCopy = [];
            regularWordsOutput.querySelectorAll('li').forEach(li => textToCopy.push(li.textContent));
            const wildcardText = wildcardWordOutput.querySelector('p')?.textContent;
            if (wildcardText && wildcardText.startsWith('Wildcard:')) {
                textToCopy.push(wildcardText.replace('Wildcard:', '').trim());
            }

            if (textToCopy.length > 0) {
                navigator.clipboard.writeText(textToCopy.join(', '))
                    .then(() => alert('All generated words copied to clipboard!'))
                    .catch(err => {
                        console.error('Failed to copy words: ', err);
                        alert('Failed to copy words. See console for details.');
                    });
            } else {
                alert('No words to copy.');
            }
        });
    }
});
