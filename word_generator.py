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
    return [clipped]

# --- Reduplication --- # 

def _get_last_syllable_heuristic(word: str) -> str:
    """Heuristic to get the perceived last syllable or a significant ending part."""
    if not word or len(word) < 2:
        return word

    # Find the last vowel
    last_vowel_index = -1
    for i in range(len(word) - 1, -1, -1):
        if word[i] in VOWELS:
            last_vowel_index = i
            break
    
    if last_vowel_index == -1: # No vowels (e.g., "rhythm")
        return word[-2:] if len(word) >= 2 else word # take last two chars if possible

    # Try to capture from the last vowel onwards, or a bit before if it makes sense
    start_index = last_vowel_index
    
    # If the last vowel is not the first letter, and char before it is a consonant, include it.
    if last_vowel_index > 0 and word[last_vowel_index - 1] in CONSONANTS:
        start_index = last_vowel_index - 1
        # If that consonant is preceded by another vowel, maybe the split is at the last vowel itself.
        # Example: "example" -> last_vowel_index is 'e' (6). word[5]='l'. start_index=5. 'ple'
        # "computer" -> last_vowel_index is 'e' (5). word[4]='t'. start_index=4. 'ter'
        # "happy" -> last_vowel_index is 'y' (4). word[3]='p'. start_index=3. 'ppy'

    # If the result is too short, try to make it longer by including more from the end
    segment = word[start_index:]
    if len(segment) < 2 and len(word) >= 2:
        return word[-2:] # Fallback to last two chars
    if len(segment) == 1 and len(word) >= 3:
        return word[-3:] # Fallback to last three if segment is just one char and word is longer
    
    return segment

def reduplicate_word(word: str, mode: str = 'suffix_partial') -> list[str]:
    """
    Creates a new word by reduplicating a part of the original word.

    Args:
        word: The base word.
        mode: 'suffix_partial' (repeats a heuristic last syllable/segment), 
              'root_modified_playful' (repeats root and modifies the duplicated part playfullly).

    Returns:
        A list containing the reduplicated word, or empty if not applicable.
    """
    word = word.lower()
    if len(word) < 3: # Too short to meaningfully reduplicate
        return []

    reduplicated_words = []

    if mode == 'suffix_partial':
        # Heuristic: try to get the last syllable or a meaningful ending part
        # This is a simplification; true syllabification is complex.
        # segment_to_reduplicate = word[-2:] # Simplest: last two letters
        segment_to_reduplicate = _get_last_syllable_heuristic(word)

        if segment_to_reduplicate and len(segment_to_reduplicate) >=1 : # Ensure segment is not empty
            new_word = word + segment_to_reduplicate
            if len(new_word) < 25 : # Max length
                 reduplicated_words.append(new_word)
    
    elif mode == 'root_modified_playful':
        # Repeat the root, and modify the duplicated part by changing one letter
        # e.g., happy -> happy + modified(happy) -> happy + hoppy / happy + happa etc.
        # For simplicity, let's just append a modified version of the last letter or a short segment
        if len(word) > 0:
            last_char = word[-1]
            if last_char in VOWELS:
                possible_replacements = [v for v in VOWELS if v != last_char]
            elif last_char in CONSONANTS:
                possible_replacements = [c for c in CONSONANTS if c != last_char]
            else: # Unlikely, but handle
                possible_replacements = list(string.ascii_lowercase)
            
            if possible_replacements:
                new_ending_char = random.choice(possible_replacements)
                new_word = word + new_ending_char
            else: # Only one type of vowel/consonant, e.g. "aaaa"
                new_word = word + random.choice(string.ascii_lowercase) # add a random letter
            
            if len(new_word) < 25:
                 reduplicated_words.append(new_word)

    elif mode == 'suffix_full': # Example: not currently used by default generator
        # Full suffix reduplication (e.g., "go" -> "gogo") - this is more like "echo"
        # Might be too simplistic or create non-words often.
        # If word is short, this can be effective.
        if len(word) <= 4 : # Apply only to short words for better effect
            new_word = word + word
            if len(new_word) < 25:
                reduplicated_words.append(new_word)
    else:
        raise ValueError(f"Unknown reduplication mode: {mode}")

    return [w for w in reduplicated_words if w != word] # Ensure it's a new word


# --- Phonetic Respelling --- #

# Define rules for phonetic respelling as (pattern_to_find, replacement)
# These rules are applied sequentially. More specific rules should come first.
# Using simple string replacement for now. Regex could make it more powerful.
PHONETIC_RESPELLING_RULES = {
    # Suffixes
    "ing": "in'", # "running" -> "runnin'"
    # Whole words or common patterns
    "cool": "kewl",
    "you": "u",
    "your": "ur",
    # "the": "da", # Can be too much
    # "for": "4",
    # "to": "2", # If we want leetspeak elements
    # "ate": "8",
}

def phonetic_respell(word: str) -> list[str]:
    """
    Applies phonetic respelling rules to a word.
    Currently applies at most one rule that matches.

    Args:
        word: The word to respell.

    Returns:
        A list containing the respelled word if a rule applied, else empty list.
    """
    word_lower = word.lower()
    
    # Check for whole word direct replacements first
    if word_lower in PHONETIC_RESPELLING_RULES:
        respelled = PHONETIC_RESPELLING_RULES[word_lower]
        if respelled != word_lower: # Ensure it's a change
            return [respelled]
        # If replacement is same as original (e.g. rule to normalize), treat as no change by this rule

    # Check for suffix rules (currently only "-ing")
    if word_lower.endswith("ing") and "ing" in PHONETIC_RESPELLING_RULES:
        # Ensure it's not a very short word that happens to end in "ing" like "sing"
        # Let's say the part before "ing" must be at least 2 chars, so word len > 4
        if len(word_lower) > 4:
            base = word_lower[:-3]
            respelled = base + PHONETIC_RESPELLING_RULES["ing"]
            if respelled != word_lower:
                return [respelled]
    
    # Add other types of rules here (e.g., regex-based, internal changes)
    
    return [] # No rule applied or no change made

# --- Phonetic Modification (Vowel/Consonant Swap) --- #

def modify_word_phonetically(word: str) -> list[str]:
    """
    Modifies a word by changing one vowel to another or one consonant to another.

    Args:
        word: The word to modify.

    Returns:
        A list of modified words (or empty list if no modification is suitable).
    """
    word = word.lower()
    if len(word) < 2: # Too short to modify meaningfully
        return []

    modified_versions = set()
    num_modifications_to_try = 1 # Try to make one distinct modification

    for _ in range(10): # Try a few times to find a modification
        if len(modified_versions) >= num_modifications_to_try:
            break

        char_index = random.randrange(len(word))
        original_char = word[char_index]
        new_char = original_char

        if original_char in VOWELS:
            possible_new_chars = [v for v in VOWELS if v != original_char]
            if possible_new_chars:
                new_char = random.choice(possible_new_chars)
        elif original_char in CONSONANTS:
            possible_new_chars = [c for c in CONSONANTS if c != original_char]
            if possible_new_chars:
                new_char = random.choice(possible_new_chars)
        
        if new_char != original_char:
            modified_word = list(word)
            modified_word[char_index] = new_char
            modified_word_str = "".join(modified_word)
            # Basic pronounceability/quality checks can be added here if needed
            if len(modified_word_str) > 2: # Keep it reasonably long
                modified_versions.add(modified_word_str)
    
    return list(modified_versions)

# --- Wildcard Word Generation --- #

QUIRKY_WORDS = [
    "kerfuffle", "flummox", "hullabaloo", "bamboozle", "gobbledygook", "malarkey", 
    "wobegone", "snollygoster", "collywobbles", "nincompoop", "rambunctious", 
    "skulduggery", "persnickety", "codswallop", "hornswoggle", "cantankerous",
    "lollygag", "flibbertigibbet", "whatchamacallit", "thingamajig", "doohickey",
    "discombobulate", "finagle", "shenanigans", "cattywampus", "rigmarole"
]

def generate_wildcard_word(user_keywords: list[str], quirky_inspiration_list: list[str]) -> str | None:
    """
    Generates a single "wildcard" word by combining a user keyword with a quirky inspirational word.
    Primarily tries blending, falls back to affixing if blending yields no results.
    """
    if not user_keywords or not quirky_inspiration_list:
        return None

    chosen_user_keyword = random.choice(user_keywords)
    chosen_quirky_word = random.choice(quirky_inspiration_list)

    # Attempt 1: Blend the user keyword with the quirky word
    blended_wildcards = blend_words(chosen_user_keyword, chosen_quirky_word)
    if not blended_wildcards: # Try blending the other way if first failed
        blended_wildcards = blend_words(chosen_quirky_word, chosen_user_keyword)
    
    if blended_wildcards:
        return random.choice(blended_wildcards)

    # Fallback 1: Try to affix the user keyword (playfully if possible)
    affixed_user_key = add_affixes(chosen_user_keyword, playful_prob=0.7)
    if affixed_user_key:
        return random.choice(affixed_user_key)
    
    # Fallback 2: Try to affix the quirky word
    affixed_quirky = add_affixes(chosen_quirky_word, playful_prob=0.7)
    if affixed_quirky:
        return random.choice(affixed_quirky)
        
    # Fallback 3: If all else fails, return a slightly modified quirky word or user keyword
    # (e.g., simple phonetic modification)
    modified_quirky = modify_word_phonetically(chosen_quirky_word)
    if modified_quirky:
        return random.choice(modified_quirky)
    
    modified_user_key = modify_word_phonetically(chosen_user_keyword)
    if modified_user_key:
        return random.choice(modified_user_key)

    return chosen_user_keyword + chosen_quirky_word[:3] # Last resort crude concat

# --- Main Generation Orchestration --- #

def generate_new_words(keywords: list[str], num_to_generate: int = 10) -> dict:
    """
    Generates a specified number of new words based on keywords and various strategies.
    Ensures one "wildcard" word is part of the output if num_to_generate >= 1.

    Args:
        keywords: A list of base keywords.
        num_to_generate: The total number of words desired (including the wildcard).

    Returns:
        A dictionary: {"regular_words": list_of_strings, "wildcard_word": string_or_None}
    """
    if not keywords or num_to_generate <= 0:
        return {"regular_words": [], "wildcard_word": None}

    related_words_pool = get_related_words(keywords, max_related=30) # Get a larger pool
    # If no related words found, use the original keywords as the pool
    if not related_words_pool:
        related_words_pool = [k.lower().strip() for k in keywords if k.strip() and len(k) > 2] 

    if not related_words_pool: # Still no words to work with (e.g. keywords were too short or invalid)
         return {"regular_words": [], "wildcard_word": generate_wildcard_word(keywords, QUIRKY_WORDS) if num_to_generate >=1 else None}


    generated_words = set() # Use a set to ensure uniqueness for regular words
    
    # Determine number of regular words to generate
    # Wildcard is always generated if num_to_generate >= 1
    num_regular_to_generate = num_to_generate - 1 if num_to_generate >= 1 else 0

    # Strategies to apply (functions themselves)
    strategies = [
        blend_words, 
        add_affixes, 
        clip_word, 
        modify_word_phonetically,
        reduplicate_word, # Add new strategy
        phonetic_respell  # Add new strategy
    ]

    attempts = 0
    max_attempts = num_regular_to_generate * 20 + 20 # Allow more attempts to find unique words

    while len(generated_words) < num_regular_to_generate and attempts < max_attempts:
        attempts += 1
        
        # Pick one or two base words from the pool for this iteration
        # Varying this more can increase diversity
        if len(related_words_pool) >= 2 and random.random() < 0.6: # 60% chance to use two words for blending
            base1, base2 = random.sample(related_words_pool, 2)
        elif related_words_pool: # Use one word
            base1 = random.choice(related_words_pool)
            base2 = None # Indicate only one base word is primary for this round
        else: # Should not happen if pool was validated, but as a fallback
            break

        strategy_func = random.choice(strategies)
        new_potentials = []

        try:
            if strategy_func == blend_words:
                if base2: # Requires two words
                    new_potentials = strategy_func(base1, base2)
                else: # Try blending base1 with another random word from pool if available
                    if len(related_words_pool) >=2:
                        temp_base2 = random.choice([w for w in related_words_pool if w != base1])
                        if temp_base2:
                            new_potentials = strategy_func(base1, temp_base2)
                    elif keywords: # Fallback: blend with an original keyword
                         temp_base2 = random.choice([k for k in keywords if k.lower().strip() != base1])
                         if temp_base2:
                            new_potentials = strategy_func(base1, temp_base2.lower().strip())
            
            elif strategy_func in [add_affixes, clip_word, modify_word_phonetically, reduplicate_word, phonetic_respell]:
                # These strategies take one word
                new_potentials = strategy_func(base1)
            
        except Exception as e:
            print(f"Error during strategy {strategy_func.__name__} with '{base1}', '{base2 if base2 else ''}': {e}")
            continue # Skip to next attempt if a strategy fails

        for word in new_potentials:
            if word and word not in keywords and len(word) > 2 and len(word) < 20: # Basic quality filter
                # More sophisticated pronounceability check could go here
                generated_words.add(word)
                if len(generated_words) >= num_regular_to_generate:
                    break
        if len(generated_words) >= num_regular_to_generate:
            break
            
    # Generate the wildcard word
    wildcard = None
    if num_to_generate >= 1:
        wildcard = generate_wildcard_word(keywords, QUIRKY_WORDS)
        # Ensure wildcard is not already in regular generated words
        if wildcard and wildcard in generated_words:
            # If conflict, try to generate a different wildcard or just let it be (it's a small chance)
            # For simplicity, we might allow it, or try one re-generation for wildcard.
            pass # Current: allow potential duplicate between wildcard and regular if it happens.

    final_regular_words = list(generated_words)
    random.shuffle(final_regular_words) # Shuffle for varied output order

    return {
        "regular_words": final_regular_words[:num_regular_to_generate],
        "wildcard_word": wildcard
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate new words based on keywords.")
    parser.add_argument("keywords", nargs='+', help="One or more base keywords.")
    parser.add_argument("-n", "--num", type=int, default=10, help="Number of words to generate (default: 10, min: 1).")
    args = parser.parse_args()

    if args.num < 1:
        print("Number of words to generate must be at least 1.")
    else:
        # Ensure NLTK data is ready before first generation call via CLI
        download_nltk_data() 
        
        print(f"\nGenerating {args.num} word(s) based on: {args.keywords}\n")
        output = generate_new_words(args.keywords, args.num)
        
        if output["regular_words"]:
            print("Generated Words:")
            for i, word in enumerate(output["regular_words"]):
                print(f"  {i+1}. {word}")
        
        if output["wildcard_word"]:
            print(f"\nWildcard: {output["wildcard_word"]}")
        
        if not output["regular_words"] and not output["wildcard_word"]:
            print("No words could be generated with the given inputs and settings.")
```