# Newslang Word Generator

A simple Python tool to generate new words based on keywords.

## Overview

This script uses NLTK's WordNet to find words related to user-provided keywords. It then applies several techniques to generate new word candidates:

*   **Blending:** Combines parts of two related words.
*   **Affixation:** Adds common English prefixes or suffixes.
*   **Phonetic Modification:** Makes small, random vowel/consonant substitutions.

## Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/sim-lu/newslang.git
    cd newslang
    ```
2.  **Create and activate a virtual environment:**
    ```bash
    python3 -m venv venv
    source venv/bin/activate 
    # On Windows use `venv\Scripts\activate`
    ```
3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
4.  **Download NLTK data:** The script will attempt to download the necessary WordNet data on first run. If you encounter SSL issues on macOS, you may need to run the `Install Certificates.command` script typically located in your Python application folder (`/Applications/Python X.Y/`).

## Usage

Run the script from the command line, providing one or more keywords:

```bash
python word_generator.py keyword1 [keyword2 ...] [-n NUMBER]
```

*   `keyword1 [keyword2 ...]` : One or more base keywords.
*   `-n NUMBER` or `--num NUMBER`: (Optional) The desired number of words to generate (default: 10).

**Examples:**

```bash
# Generate 10 words based on "playful", "fun", "game"
python word_generator.py playful fun game

# Generate 5 words based on "technology", "network", "speed"
python word_generator.py technology network speed -n 5
```

## Testing

To run the included tests:

```bash
pip install pytest # If not already installed
pytest
``` 