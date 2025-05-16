from flask import Flask, render_template, request, jsonify
from word_generator import generate_new_words # Assuming word_generator.py is in the same directory

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/generate', methods=['POST'])
def api_generate_words():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No input data provided"}), 400

        keywords = data.get('keywords')
        num_to_generate = data.get('num_to_generate')

        if not keywords or not isinstance(keywords, list):
            return jsonify({"error": "Keywords must be provided as a list of strings"}), 400
        
        validated_keywords = []
        for kw in keywords:
            if not isinstance(kw, str) or not kw.strip() or not kw.isalpha():
                # Silently ignore invalid keywords on server-side after client-side has warned,
                # or return an error if strictness is preferred.
                # For now, we filter them out. If after filtering, no keywords remain, it's an issue.
                continue 
            validated_keywords.append(kw.strip())

        if not validated_keywords:
            return jsonify({"error": "No valid keywords provided. Keywords must be alphabetic and non-empty."}), 400

        if num_to_generate is None or not isinstance(num_to_generate, int) or num_to_generate <= 0:
            return jsonify({"error": "Number to generate must be a positive integer"}), 400
        
        MAX_WORDS = 10 # Updated MAX_WORDS to 10
        if num_to_generate > MAX_WORDS:
            # Client-side should prevent this, but as a safeguard:
            num_to_generate = MAX_WORDS 
            # Optionally, inform via a custom header or a modified response if necessary,
            # but for now, just cap it.

        generated_data = generate_new_words(validated_keywords, num_to_generate)
        return jsonify(generated_data)

    except Exception as e:
        # Log the exception for debugging
        app.logger.error(f"Error in /api/generate: {str(e)}")
        return jsonify({"error": "An internal server error occurred"}), 500

if __name__ == '__main__':
    # For development, you can run it with debug=True
    # For production, use a proper WSGI server like Gunicorn or Waitress
    app.run(debug=True) 