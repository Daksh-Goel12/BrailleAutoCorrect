#!/usr/bin/env python3
"""
Quick test to see what the current system actually returns
"""

from braille_autocorrect import BrailleAutoCorrect

def quick_test():
    print("🔬 QUICK TEST - What does the system actually suggest?")
    print("=" * 55)
    
    corrector = BrailleAutoCorrect()
    
    test_cases = [
        "cak",
        "dg", 
        "helllo",
        "baat"
    ]
    
    for word in test_cases:
        print(f"\nInput: '{word}'")
        try:
            suggestions = corrector.suggest_words(word, max_suggestions=3)
            if suggestions:
                for i, (suggested_word, distance, confidence) in enumerate(suggestions, 1):
                    print(f"  {i}. {suggested_word} (dist: {distance}, conf: {confidence:.2f})")
            else:
                print("  No suggestions found!")
        except Exception as e:
            print(f"  ERROR: {e}")
    
    print(f"\nDictionary contains: {corrector.dictionary}")
    print(f"Dictionary size: {len(corrector.dictionary)}")

if __name__ == "__main__":
    quick_test()