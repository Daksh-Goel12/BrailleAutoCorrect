# from flask import Flask, render_template_string, request
# from braille_autocorrect import load_dictionary, suggest_word

# app = Flask(__name__)
# dictionary = load_dictionary()

# TEMPLATE = """
# <!doctype html>
# <title>Braille Auto-Correct</title>
# <h2>Braille Auto-Correct System</h2>
# <form method="POST">
#   <input name="word" placeholder="Type QWERTY Braille" required>
#   <input type="submit" value="Correct">
# </form>
# {% if corrected %}
# <p><strong>Suggested:</strong> {{ corrected }}</p>
# {% endif %}
# """

# @app.route("/", methods=["GET", "POST"])
# def home():
#     corrected = None
#     if request.method == "POST":
#         word = request.form["word"]
#         corrected = suggest_word(word, dictionary)
#     return render_template_string(TEMPLATE, corrected=corrected)

# if __name__ == "__main__":
#     app.run(debug=True)


from flask import Flask, render_template_string, request, jsonify
from braille_autocorrect import BrailleAutoCorrect
import time

app = Flask(__name__)

# Initialize the enhanced corrector
corrector = BrailleAutoCorrect()

TEMPLATE = """
<!doctype html>
<html>
<head>
    <title>Enhanced Braille Auto-Correct</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 800px; margin: 50px auto; padding: 20px; }
        .container { background: #f5f5f5; padding: 30px; border-radius: 10px; }
        input[type="text"] { width: 300px; padding: 10px; font-size: 16px; border: 2px solid #ddd; border-radius: 5px; }
        input[type="submit"] { padding: 10px 20px; font-size: 16px; background: #007bff; color: white; border: none; border-radius: 5px; cursor: pointer; margin-left: 10px; }
        input[type="submit"]:hover { background: #0056b3; }
        .suggestions { margin-top: 20px; }
        .suggestion-item { background: white; padding: 15px; margin: 10px 0; border-radius: 5px; border-left: 4px solid #007bff; }
        .confidence { color: #666; font-size: 0.9em; }
        .stats { background: #e9ecef; padding: 15px; border-radius: 5px; margin-top: 20px; }
        .learning-section { margin-top: 20px; padding: 15px; background: #d4edda; border-radius: 5px; }
        .processing-time { color: #28a745; font-weight: bold; }
        .error { color: #dc3545; }
    </style>
</head>
<body>
    <div class="container">
        <h2>🔤 Enhanced Braille Auto-Correct System</h2>
        <p>Enter text using QWERTY-style Braille input to get intelligent suggestions.</p>
        
        <form method="POST">
            <input name="word" type="text" placeholder="Type QWERTY Braille (e.g., 'cak' for 'cap')" value="{{ input_word or '' }}" required>
            <input type="submit" value="Get Suggestions">
        </form>
        
        {% if suggestions %}
        <div class="suggestions">
            <h3>📋 Suggestions <span class="processing-time">({{ processing_time }}ms)</span></h3>
            {% for word, distance, confidence in suggestions %}
            <div class="suggestion-item">
                <strong>{{ loop.index }}. {{ word }}</strong>
                <div class="confidence">
                    Confidence: {{ "%.1f" | format(confidence * 100) }}% 
                    | Edit Distance: {{ distance }}
                </div>
            </div>
            {% endfor %}
            
            {% if suggestions %}
            <div class="learning-section">
                <p><strong>💡 Learning Feature:</strong> 
                Was "{{ suggestions[0][0] }}" the correct word you meant?</p>
                <form method="POST" style="display: inline;">
                    <input type="hidden" name="word" value="{{ input_word }}">
                    <input type="hidden" name="confirm_word" value="{{ suggestions[0][0] }}">
                    <input type="hidden" name="learn" value="true">
                    <input type="submit" value="✅ Yes, Remember This" style="background: #28a745;">
                </form>
            </div>
            {% endif %}
        </div>
        {% elif input_word %}
        <div class="suggestions">
            <p class="error">❌ No suggestions found for "{{ input_word }}". Try a different input.</p>
        </div>
        {% endif %}
        
        <div class="stats">
            <h4>📊 System Statistics</h4>
            <p><strong>Dictionary Size:</strong> {{ stats.dictionary_size }} words</p>
            <p><strong>Learned Corrections:</strong> {{ stats.learned_corrections }}</p>
            <p><strong>Cached Patterns:</strong> {{ stats.braille_patterns_cached }}</p>
        </div>
        
        <div style="margin-top: 20px; padding: 15px; background: #fff3cd; border-radius: 5px;">
            <h4>💡 How to Use</h4>
            <p><strong>Examples to try:</strong></p>
            <ul>
                <li><code>cak</code> → should suggest "can"</li>
                <li><code>dg</code> → should suggest "dog"</li>
                <li><code>helllo</code> → should suggest "hello"</li>
            </ul>
        </div>
    </div>
</body>
</html>
"""

@app.route("/", methods=["GET", "POST"])
def home():
    suggestions = None
    input_word = None
    processing_time = 0
    
    if request.method == "POST":
        input_word = request.form.get("word", "").strip()
        
        # Handle learning confirmation
        if request.form.get("learn") == "true":
            confirm_word = request.form.get("confirm_word")
            if input_word and confirm_word:
                corrector.remember_choice(input_word, confirm_word)
                # Show a success message by redirecting with the same word
                input_word = input_word  # Keep the input for display
        
        if input_word:
            start_time = time.time()
            suggestion_results = corrector.suggest_words(input_word, max_suggestions=5)
            end_time = time.time()
            
            processing_time = round((end_time - start_time) * 1000, 1)
            suggestions = suggestion_results if suggestion_results else None
    
    stats = corrector.get_stats()
    
    return render_template_string(
        TEMPLATE, 
        suggestions=suggestions, 
        input_word=input_word,
        processing_time=processing_time,
        stats=stats
    )

@app.route("/api/suggest", methods=["POST"])
def api_suggest():
    """API endpoint for programmatic access"""
    data = request.get_json()
    if not data or 'word' not in data:
        return jsonify({"error": "Missing 'word' parameter"}), 400
    
    input_word = data['word'].strip()
    max_suggestions = data.get('max_suggestions', 5)
    
    start_time = time.time()
    suggestions = corrector.suggest_words(input_word, max_suggestions=max_suggestions)
    end_time = time.time()
    
    result = {
        "input": input_word,
        "suggestions": [
            {
                "word": word,
                "distance": distance,
                "confidence": round(confidence, 3)
            }
            for word, distance, confidence in suggestions
        ],
        "processing_time_ms": round((end_time - start_time) * 1000, 1),
        "stats": corrector.get_stats()
    }
    
    return jsonify(result)

@app.route("/api/learn", methods=["POST"])
def api_learn():
    """API endpoint to add user corrections"""
    data = request.get_json()
    if not data or 'typed' not in data or 'corrected' not in data:
        return jsonify({"error": "Missing 'typed' or 'corrected' parameters"}), 400
    
    corrector.remember_choice(data['typed'], data['corrected'])
    return jsonify({"success": True, "message": "Correction learned successfully"})

if __name__ == "__main__":
    print("Starting Enhanced Braille Auto-Correct Web Server...")
    print("Features:")
    print("- Multiple suggestions with confidence scores")
    print("- Learning mechanism with user feedback")
    print("- Performance timing")
    print("- REST API endpoints")
    print("\nWeb Interface: http://127.0.0.1:5000")
    print("API Example: POST to /api/suggest with JSON: {'word': 'cak'}")
    print("Learning API: POST to /api/learn with JSON: {'typed': 'cak', 'corrected': 'cap'}")
    
    app.run(debug=True)