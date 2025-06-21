#!/usr/bin/env python3
"""
Debug version to see what's happening with the suggestions
"""

from braille_autocorrect import BrailleAutoCorrect

def debug_suggestion(input_word, expected_word=None):
    """Debug a specific suggestion to see what's happening"""
    print(f"\n🔍 DEBUGGING: '{input_word}' -> expected: '{expected_word}'")
    print("=" * 50)
    
    corrector = BrailleAutoCorrect()
    
    # Show input braille pattern
    input_braille = corrector.word_to_braille(input_word)
    print(f"Input '{input_word}' -> Braille: {input_braille}")
    
    if expected_word:
        expected_braille = corrector.word_to_braille(expected_word)
        print(f"Expected '{expected_word}' -> Braille: {expected_braille}")
        distance = corrector.levenshtein_optimized(input_braille, expected_braille)
        print(f"Distance between them: {distance}")
    
    # Show all dictionary words and their distances
    print(f"\nAll dictionary words with distances:")
    print("-" * 40)
    
    all_results = []
    for word in corrector.dictionary:
        word_braille = corrector.word_to_braille(word)
        distance = corrector.levenshtein_optimized(input_braille, word_braille)
        confidence = 1.0 - (distance / max(len(input_braille), len(word_braille)))
        all_results.append((word, distance, confidence, word_braille))
    
    # Sort by distance, then by confidence
    all_results.sort(key=lambda x: (x[1], -x[2]))
    
    for word, distance, confidence, braille in all_results[:10]:  # Show top 10
        print(f"{word:8} | dist: {distance:2} | conf: {confidence:.2f} | braille: {braille}")
    
    # Get actual suggestions
    print(f"\nActual suggestions from system:")
    print("-" * 30)
    suggestions = corrector.suggest_words(input_word, max_suggestions=5)
    for i, (word, dist, conf) in enumerate(suggestions, 1):
        print(f"{i}. {word} (distance: {dist}, confidence: {conf:.2f})")
    
    print("=" * 50)

def test_all_examples():
    """Test all the examples from the documentation"""
    examples = [
        ("cak", "cap"),
        ("dg", "dog"), 
        ("helllo", "hello"),
        ("baat", "bat")
    ]
    
    print("🧪 TESTING ALL EXAMPLES FROM DOCUMENTATION")
    print("=" * 60)
    
    for input_word, expected in examples:
        debug_suggestion(input_word, expected)
        
        # Quick test
        corrector = BrailleAutoCorrect()
        suggestions = corrector.suggest_words(input_word, max_suggestions=1)
        actual = suggestions[0][0] if suggestions else "NO_SUGGESTION"
        
        status = "✅ PASS" if actual == expected else "❌ FAIL"
        print(f"{status}: '{input_word}' -> got '{actual}', expected '{expected}'")
        print("\n" + "="*60 + "\n")

def show_braille_mappings():
    """Show the braille mappings being used"""
    print("🔤 BRAILLE CHARACTER MAPPINGS")
    print("=" * 40)
    
    corrector = BrailleAutoCorrect()
    
    # Show mappings for letters in our test words
    test_chars = set('cakdghellobat')
    for char in sorted(test_chars):
        braille = corrector.braille_map.get(char, '000000')
        print(f"'{char}' -> {braille}")
    
    print("\n🔤 WORD -> BRAILLE CONVERSIONS")
    print("=" * 40)
    
    test_words = ['cak', 'cap', 'dg', 'dog', 'helllo', 'hello', 'baat', 'bat']
    for word in test_words:
        braille = corrector.word_to_braille(word)
        print(f"'{word}' -> {braille}")

if __name__ == "__main__":
    print("🐛 BRAILLE AUTO-CORRECT DEBUG TOOL")
    print("This will help identify why suggestions aren't working as expected\n")
    
    choice = input("What would you like to debug?\n1. Test all examples\n2. Show braille mappings\n3. Debug specific word\nChoice (1-3): ").strip()
    
    if choice == "1":
        test_all_examples()
    elif choice == "2":
        show_braille_mappings()
    elif choice == "3":
        word = input("Enter word to debug: ").strip()
        expected = input("Expected result (optional): ").strip() or None
        debug_suggestion(word, expected)
    else:
        print("Invalid choice. Running all tests...")
        test_all_examples()