import nltk
import random
import string
from nltk.corpus import wordnet as wn
import argparse

# Define vowels for pronounceability heuristics later
VOWELS = "aeiou"
CONSONANTS = "bcdfghjklmnpqrstvwxyz"

def download_nltk_data():
    """Downloads necessary NLTK data if not already present."""
    try:
        # Check if wordnet is available
        wn.ensure_loaded()
        print("WordNet data found.")
    except LookupError:
        print("WordNet data not found. Downloading... (This might take a moment)")
        try:
            nltk.download('wordnet', quiet=True)
            nltk.download('omw-1.4', quiet=True) # Open Multilingual Wordnet, often needed
            # Re-check after download
            wn.ensure_loaded()
            print("WordNet data downloaded successfully.")
        except Exception as e:
            print(f"Error downloading NLTK data: {e}")
            print("Please try running 'python -m nltk.downloader wordnet omw-1.4' manually.")
            raise

def get_related_words(keywords: list[str], max_related: int = 20) -> list[str]:
    """
    Finds words related (synonyms, hypernyms, hyponyms) to the input keywords using WordNet.

    Args:
        keywords: A list of keywords to find related words for.
        max_related: The approximate maximum number of related words to return.

    Returns:
        A list of unique related word strings (lowercase).
    """
    download_nltk_data() # Ensure data is available

    # Clean keywords first and store them for filtering later
    cleaned_keywords = {k.lower().strip() for k in keywords if k.strip()}

    related_words = set()
    for keyword in keywords:
        keyword = keyword.lower().strip()
        if not keyword:
            continue

        # Find synsets (sets of synonyms) for the keyword
        synsets = wn.synsets(keyword)
        if not synsets:
            print(f"Warning: No WordNet entries found for keyword: '{keyword}'")
            continue

        # Gather lemmas (words) from synsets and related synsets
        for syn in synsets:
            # Add lemmas from the direct synset
            for lemma in syn.lemmas():
                word = lemma.name().lower().replace('_', ' ') # Use space for multi-word lemmas initially
                if all(c in string.ascii_lowercase + ' ' for c in word): # Basic filter
                     related_words.add(word.split(' ')[0]) # Often take first word of multi-word phrase

            # Optional: Explore related concepts (hypernyms, hyponyms) for more variety
            # Add lemmas from hypernyms (more general concepts)
            for hyper in syn.hypernyms():
                 for lemma in hyper.lemmas():
                    word = lemma.name().lower().replace('_', ' ')
                    if all(c in string.ascii_lowercase + ' ' for c in word):
                         related_words.add(word.split(' ')[0])

            # Add lemmas from hyponyms (more specific concepts)
            # for hypo in syn.hyponyms():
            #     for lemma in hypo.lemmas():
            #         word = lemma.name().lower().replace('_', ' ')
            #         if all(c in string.ascii_lowercase + ' ' for c in word):
            #              related_words.add(word.split(' ')[0])


    # Filter out original keywords and ensure single words without spaces/hyphens
    filtered_words = {
        w for w in related_words
        # Check against the cleaned keywords set
        if w not in cleaned_keywords and ' ' not in w and '-' not in w and len(w) > 2 # Exclude very short words
    }

    # Limit the number of words returned
    word_list = list(filtered_words)
    random.shuffle(word_list) # Shuffle before slicing for variety
    return word_list[:max_related]

def find_longest_overlap(s1, s2):
    """Finds the longest overlapping substring between end of s1 and start of s2."""
    max_overlap = ""
    for k in range(min(len(s1), len(s2)), 0, -1):
        if s1.endswith(s2[:k]):
            return s2[:k]
    return ""

def blend_words(word1: str, word2: str) -> list[str]:
    """
    Attempts to blend two words into potential portmanteaus.
    Tries simple start/end concatenation and overlap blending.

    Args:
        word1: The first word.
        word2: The second word.

    Returns:
        A list of potential blended words (lowercase).
    """
    word1 = word1.lower()
    word2 = word2.lower()
    blends = set()

    # --- Strategy 1: Overlap Blending --- #
    overlap12 = find_longest_overlap(word1, word2)
    overlap21 = find_longest_overlap(word2, word1)

    # Blend based on overlap from word1 to word2
    if len(overlap12) >= 2: # Require a reasonable overlap
        blends.add(word1 + word2[len(overlap12):])

    # Blend based on overlap from word2 to word1
    if len(overlap21) >= 2:
        blends.add(word2 + word1[len(overlap21):])

    # --- Strategy 2: Simple Half/Half Blending (Fallback/Additional) --- #
    len1 = len(word1)
    len2 = len(word2)

    if len1 > 1 and len2 > 1:
        # Blend 1: Start of word1 + End of word2
        split1 = max(1, len1 // 2 + random.randint(-1, 1)) # Add some randomness to split point
        split2 = max(1, len2 // 2 + random.randint(-1, 0))
        blends.add(word1[:split1] + word2[split2:])

        # Blend 2: Start of word2 + End of word1
        split1 = max(1, len1 // 2 + random.randint(-1, 0))
        split2 = max(1, len2 // 2 + random.randint(-1, 1))
        blends.add(word2[:split2] + word1[split1:])

    # TODO: Add more sophisticated blending (e.g., find vowel overlaps)?
    # Remove blends that are just one of the original words (can happen with full overlap)
    blends.discard(word1)
    blends.discard(word2)

    # Basic filtering of results
    valid_blends = [b for b in blends if len(b) > 3]
    # Return unique blends
    return list(set(valid_blends))

# --- Affixation --- #

COMMON_PREFIXES = ["re", "un", "in", "im", "pre", "post", "mis", "dis", "pro", "anti", "non"]
COMMON_SUFFIXES = ["ing", "ed", "er", "est", "ly", "able", "ible", "ness", "ment", "tion", "sion", "ify", "ize"]

# Playful additions (can be prefixes or suffixes)
PLAYFUL_AFFIXES = [
    "mega", "uber", "hyper", "giga", # Prefixes
    # Suffixes (handle hyphen)
    "-tastic", "-erific", "-inator", "-izzle", "-core", "-wave", "-punk", "-ish", "-y", 
    "-o-rama", "-apalooza", "-erino", "-arino", "-zilla", "-meister", "-licious", 
    "-tude", "-scape", "-omatic"
]

def add_affixes(word: str, playful_prob: float = 0.3) -> list[str]:
    """
    Adds common or playful prefixes or suffixes to a word.

    Args:
        word: The base word.
        playful_prob: Probability of choosing a playful affix over a common one.

    Returns:
        A list of new words with affixes added.
    """
    word = word.lower()
    affixed_words = set()
    added_prefix = False
    added_suffix = False

    # --- Try adding Prefix --- #
    if len(word) > 2 and not any(word.startswith(p) for p in COMMON_PREFIXES + [pa for pa in PLAYFUL_AFFIXES if not pa.startswith('-')]) :
        use_playful = random.random() < playful_prob
        if use_playful:
            # Filter for playful prefixes
            playful_prefixes = [p for p in PLAYFUL_AFFIXES if not p.startswith('-')]
            if playful_prefixes:
                prefix = random.choice(playful_prefixes)
                affixed_words.add(prefix + word)
                added_prefix = True
        # If not using playful or no playful prefixes available, try common
        if not added_prefix:
            prefix = random.choice(COMMON_PREFIXES)
            affixed_words.add(prefix + word)
            added_prefix = True

    # --- Try adding Suffix --- #
    if len(word) > 3 and not any(word.endswith(s) for s in COMMON_SUFFIXES + [pa.strip('-') for pa in PLAYFUL_AFFIXES if pa.startswith('-')]) :
        use_playful = random.random() < playful_prob
        suffix_candidate = None
        if use_playful:
            playful_suffixes = [s for s in PLAYFUL_AFFIXES if s.startswith('-')]
            if playful_suffixes:
                 suffix_candidate = random.choice(playful_suffixes).lstrip('-') # Remove leading hyphen
                 added_suffix = True # Tentatively mark as added

        # If not using playful or no playful suffixes available, try common
        if not added_suffix:
            suffix_candidate = random.choice(COMMON_SUFFIXES)
            added_suffix = True # Tentatively mark as added

        if added_suffix and suffix_candidate:
            # Apply suffix rules (simplified)
            if word.endswith('e') and suffix_candidate in ["ing", "ed", "able", "ible", "er", "est", "ish", "y", "ize"]:
                 affixed_words.add(word[:-1] + suffix_candidate)
            elif len(word) > 1 and word[-1] in CONSONANTS and word[-2] in VOWELS and suffix_candidate in ["ing", "ed", "er", "est"] and word[-1] not in 'wx':
                 affixed_words.add(word + word[-1] + suffix_candidate)
            else:
                 affixed_words.add(word + suffix_candidate)

    # Filter out originals and ensure reasonable length
    valid_affixed = [w for w in affixed_words if w != word and 3 < len(w) < 25] # Allow slightly longer playful words
    return valid_affixed

# --- Clipping --- #

def clip_word(word: str) -> list[str]:
    """
    Clips a word, keeping the beginning.
    Mimics slang like 'middle' -> 'mid'.

    Args:
        word: The word to clip.

    Returns:
        A list containing the clipped word, or empty list if too short.
    """
    word = word.lower()
    if len(word) <= 4: # Don't clip very short words
        return []

    # Simple clipping: keep first 3 or 4 characters, randomly
    clip_len = random.choice([3, 4])
    clipped = word[:clip_len]

    # Avoid returning original word if it was already short
    if clipped == word:
        return []

    # Ensure the clipped word is not just one or two characters if original was longer
    if len(clipped) <= 2 and len(word) > 2:
        return []

    return [clipped]

# --- Reduplication --- #

def reduplicate_word(word: str) -> list[str]:
    """
    Creates a new word by reduplicating the suffix of the original word.
    e.g., "happy" -> "happyappy" (if VOWELS="aeiou"), "wonder" -> "wonderer"

    Args:
        word: The word to reduplicate.

    Returns:
        A list containing the reduplicated word, or an empty list if criteria not met.
    """
    word = word.lower()
    # --- REMOVING DEBUGGING STEP FOR "cat" --- #
    # if word == "cat":
    #     return ["catat"]
    # --- END DEBUGGING STEP --- #

    if len(word) < 3: # Ensure this is < 3
        return []

    segment_to_reduplicate = ""
    last_vowel_index = -1
    # Find the last vowel in the word
    for i in range(len(word) -1, -1, -1):
        if word[i] in VOWELS:
            last_vowel_index = i
            break

    if last_vowel_index != -1:
        # If the vowel is one of the last two characters, segment is the last two characters
        # Otherwise, segment is from the last vowel to the end of the word
        if last_vowel_index >= len(word) - 2 :
            segment_to_reduplicate = word[-2:]
        else:
            segment_to_reduplicate = word[last_vowel_index:]
    
    # Fallback: if no vowel found or segment is too short, try last 2 chars if word is long enough
    if not segment_to_reduplicate or len(segment_to_reduplicate) < 2:
        if len(word) > 4: # Ensure word is long enough for a 2-char segment
            segment_to_reduplicate = word[-2:]
        else:
            return [] # Not enough to make a meaningful reduplication
    
    if not segment_to_reduplicate: # Still nothing?
        return []

    # Avoid nonsensical single-character reduplications or if segment is same as word
    if len(segment_to_reduplicate) < 2 or segment_to_reduplicate == word:
        return []

    new_word = word + segment_to_reduplicate

    # Prevent overly long words
    if len(new_word) > 20:
        return []

    return [new_word]

# --- Phonetic Respelling --- #

def phonetic_respell(word: str) -> list[str]:
    """
    Applies common phonetic respellings to a word.
    e.g., "running" -> "runnin'"

    Args:
        word: The word to respell.

    Returns:
        A list containing the respelled word if a change was made, otherwise an empty list.
    """
    word_lower = word.lower()
    original_word = word_lower # Keep a copy for comparison
    respelled_variations = set()

    # Rule 1: -ing -> -in'
    # Apply rules sequentially. word_modified will hold the current state.
    word_modified = word_lower
    changed_by_rule = False

    if word_modified.endswith("ing") and len(word_modified) > 3:
        word_modified = word_modified[:-3] + "in'"
        changed_by_rule = True

    # Rule 2: Specific substitutions
    # These apply to the potentially already modified word.
    # We should be careful if a word can be modified by multiple rules to avoid chaos.
    # For now, let's assume only one major respelling rule applies or the first one wins.
    # Let's re-think: apply rules to original_word and collect variations.

    # --- Attempt 2: Apply rules to original and collect distinct variations --- # 
    potential_respellings = set() # Store results of rules

    # Rule 1: -ing -> -in' (applied to original word)
    if original_word.endswith("ing") and len(original_word) > 3:
        potential_respellings.add(original_word[:-3] + "in'")

    # Rule 2: "cool" -> "kewl" (substring replacement on original)
    if "cool" in original_word:
        potential_respellings.add(original_word.replace("cool", "kewl", 1)) # Replace only first for now

    # Rule 3: "you" -> "u" (substring replacement on original)
    # This is broad. Consider if it should only apply if word IS "you".
    # For now, simple replacement of first instance.
    if "you" in original_word:
        potential_respellings.add(original_word.replace("you", "u", 1))

    # Filter out unchanged words and select one if changes were made
    valid_new_words = [v for v in potential_respellings if v != original_word and v]

    if not valid_new_words:
        return []
    
    return [random.choice(valid_new_words)] # Return one random valid respelling

# --- Phonetic Modification --- #

def modify_word_phonetically(word: str) -> list[str]:
    """
    Creates slight phonetic variations of a word by substituting
    a single vowel or consonant.

    Args:
        word: The base word.

    Returns:
        A list containing one modified word (or empty if modification fails).
    """
    word = word.lower()
    if len(word) < 3: # Too short to modify meaningfully
        return []

    modified_word = list(word)
    indices = list(range(len(word)))
    random.shuffle(indices)

    for index in indices:
        char = modified_word[index]

        if char in VOWELS:
            # Substitute with a different vowel
            new_vowel = random.choice(VOWELS)
            while new_vowel == char:
                new_vowel = random.choice(VOWELS)
            modified_word[index] = new_vowel
            # Simple pronounceability check: avoid triple vowels/consonants
            mod_str = "".join(modified_word)
            if not (any(c*3 in mod_str for c in VOWELS) or any(c*3 in mod_str for c in CONSONANTS)):
                 return [mod_str]
            else:
                 modified_word[index] = char # Revert if bad

        elif char in CONSONANTS:
            # Substitute with a different consonant
            new_consonant = random.choice(CONSONANTS)
            while new_consonant == char:
                new_consonant = random.choice(CONSONANTS)
            modified_word[index] = new_consonant
            # Simple pronounceability check
            mod_str = "".join(modified_word)
            if not (any(c*3 in mod_str for c in VOWELS) or any(c*3 in mod_str for c in CONSONANTS)):
                 return [mod_str]
            else:
                 modified_word[index] = char # Revert

    return [] # Return empty if no successful modification found after trying all indices

# --- Main Generation Logic --- #

def generate_new_words(keywords: list[str], num_to_generate: int = 10) -> list[str]:
    """
    Generates new words based on keywords using various techniques.

    Args:
        keywords: List of keywords to seed the generation.
        num_to_generate: The target number of new words to generate.

    Returns:
        A list of generated words.
    """
    print(f"\nGenerating {num_to_generate} words based on: {keywords}...")
    related_words = get_related_words(keywords, max_related=50) # Get a larger pool
    if not related_words:
        print("Warning: No related words found for keywords. Cannot generate new words.")
        return []

    available_related_words = list(related_words) # Mutable copy for selection

    generated_words = set()
    cleaned_keywords = {k.lower().strip() for k in keywords if k.strip()}
    related_words_set = set(related_words)
    max_attempts = num_to_generate * 20 # Safety break to avoid infinite loops
    attempts = 0

    while len(generated_words) < num_to_generate and attempts < max_attempts:
        attempts += 1
        strategy = random.choice(['blend', 'affix', 'modify', 'clip', 'reduplicate', 'respell'])

        base_word = None
        if not available_related_words:
            available_related_words = list(related_words) # Refresh if empty
            if not available_related_words: # Still no words (shouldn't happen if initial check passed)
                break 

        try:
            if strategy == 'blend':
                if len(available_related_words) >= 2:
                    w1, w2 = random.sample(available_related_words, 2)
                    # For blending, we don't necessarily remove them as they are a pair
                    new_candidates = blend_words(w1, w2)
                else:
                    new_candidates = [] # Not enough words to blend
            elif strategy in ['affix', 'modify', 'clip', 'reduplicate', 'respell']:
                if available_related_words:
                    base_word = random.choice(available_related_words)
                    if base_word in available_related_words: # Check if it's still there (it should be)
                        try:
                            available_related_words.remove(base_word) # Try to use each base word less often
                        except ValueError: # Should not happen if logic is correct
                            pass 
                    
                    if strategy == 'affix':
                        new_candidates = add_affixes(base_word)
                    elif strategy == 'modify':
                        new_candidates = modify_word_phonetically(base_word)
                    elif strategy == 'clip':
                        new_candidates = clip_word(base_word)
                    elif strategy == 'reduplicate':
                        new_candidates = reduplicate_word(base_word)
                    elif strategy == 'respell': # New strategy
                        new_candidates = phonetic_respell(base_word)
                else:
                    new_candidates = [] # No base words left in current available pool
            else:
                new_candidates = []

            for word in new_candidates:
                # Final check: not a keyword, not a related word, and not already generated
                if word not in cleaned_keywords and word not in related_words_set and word not in generated_words:
                    generated_words.add(word)
                    if len(generated_words) >= num_to_generate:
                        break # Exit inner loop if target reached
        except Exception as e:
            # Catch potential errors in generation functions
            print(f"Warning: Error during '{strategy}' generation: {e}")
            continue # Try next attempt

        if len(generated_words) >= num_to_generate:
             break # Exit outer loop

    if attempts >= max_attempts:
        print(f"Warning: Reached max attempts ({max_attempts}) before generating {num_to_generate} words.")

    print(f"Successfully generated {len(generated_words)} unique words.")
    return list(generated_words)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Generate new words based on keywords.")
    parser.add_argument('keywords', nargs='+', help='One or more keywords to base generation on.')
    parser.add_argument('-n', '--num', type=int, default=10, help='Number of words to generate.')

    args = parser.parse_args()

    # Ensure NLTK data is available before proceeding
    download_nltk_data()

    # Generate words using the main function
    generated_words_list = generate_new_words(args.keywords, args.num)

    # Print results
    print("\n--- Generated Words ---:")
    if generated_words_list:
        for i, word in enumerate(generated_words_list):
            print(f"{i+1}. {word}")
    else:
        print("(No words generated for the given keywords)")

    # Old example code removed

    # Example usage (will be replaced by argparse)
    # download_nltk_data() # Ensure WordNet is ready

    # keywords_main = ["computer", "network", "fast"]
    # generated = generate_new_words(keywords_main, 15)
    # print("\n--- Generated Words ---:")
    # if generated:
    #     for i, word in enumerate(generated):
    #         print(f"{i+1}. {word}")
    # else:
    #     print("(No words generated)")

    # Old examples (commented out or removed if argparse is added)
    # test_keywords = ["fast", "message", "digital"]
    # print(f"Keywords: {test_keywords}")
    # related = get_related_words(test_keywords)
    # print(f"\nFound {len(related)} related words (sample):\n{related[:10]}")
    # ... rest of old examples ... 