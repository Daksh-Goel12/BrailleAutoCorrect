#!/usr/bin/env python3
"""
Comprehensive test suite for the Braille Auto-Correct System
This demonstrates system effectiveness with various test cases
"""

import time
import json
from braille_autocorrect import BrailleAutoCorrect

def run_accuracy_tests():
    """Test accuracy with various error types"""
    print("=" * 60)
    print("ACCURACY TESTS - Testing Different Error Types")
    print("=" * 60)
    
    corrector = BrailleAutoCorrect()
    
    test_categories = {
        "Single Character Errors": [
            ("cag", "cat"),    # substitution
            ("ca", "cat"),     # deletion
            ("catt", "cat"),   # insertion
        ],
        "Multiple Character Errors": [
            ("cak", "cap"),
            ("baat", "bat"),
            ("helllo", "hello"),
        ],
        "Transposition Errors": [
            ("tac", "cat"),
            ("atr", "rat"),
        ],
        "Length Variations": [
            ("dg", "dog"),
            ("cn", "can"),
            ("hp", "help"),
        ],
        "Complex Cases": [
            ("hoppe", "hope"),
            ("helo", "hello"),
            ("carr", "car"),
        ]
    }
    
    total_tests = 0
    total_correct = 0
    category_results = {}
    
    for category, test_cases in test_categories.items():
        print(f"\n📋 {category}")
        print("-" * 40)
        
        category_correct = 0
        for input_word, expected in test_cases:
            suggestions = corrector.suggest_words(input_word, max_suggestions=1)
            top_suggestion = suggestions[0][0] if suggestions else "NO_SUGGESTION"
            
            is_correct = top_suggestion == expected
            status = "✅" if is_correct else "❌"
            
            print(f"{status} '{input_word}' → '{top_suggestion}' (expected: '{expected}')")
            
            if is_correct:
                category_correct += 1
                total_correct += 1
            total_tests += 1
        
        accuracy = (category_correct / len(test_cases)) * 100
        category_results[category] = accuracy
        print(f"Category Accuracy: {category_correct}/{len(test_cases)} ({accuracy:.1f}%)")
    
    print(f"\n" + "=" * 40)
    print(f"OVERALL ACCURACY: {total_correct}/{total_tests} ({total_correct/total_tests*100:.1f}%)")
    print("=" * 40)
    
    return category_results, total_correct/total_tests

def run_performance_tests():
    """Test system performance with various dictionary sizes"""
    print("\n" + "=" * 60)
    print("PERFORMANCE TESTS - Speed and Scalability")
    print("=" * 60)
    
    corrector = BrailleAutoCorrect()
    
    test_words = ["cak", "helllo", "dg", "baat", "hoppe"]
    
    print(f"Testing with {len(corrector.dictionary)} words in dictionary")
    print("-" * 40)
    
    total_time = 0
    for word in test_words:
        start_time = time.time()
        suggestions = corrector.suggest_words(word, max_suggestions=3)
        end_time = time.time()
        
        processing_time = (end_time - start_time) * 1000
        total_time += processing_time
        
        print(f"'{word}' → {processing_time:.2f}ms ({len(suggestions)} suggestions)")
    
    avg_time = total_time / len(test_words)
    print(f"\nAverage processing time: {avg_time:.2f}ms")
    
    # Test with repeated queries (caching effect)
    print("\n📊 Repeated Query Performance:")
    test_word = "cak"
    times = []
    for i in range(10):
        start_time = time.time()
        corrector.suggest_words(test_word)
        end_time = time.time()
        times.append((end_time - start_time) * 1000)
    
    print(f"First query: {times[0]:.2f}ms")
    print(f"Subsequent queries avg: {sum(times[1:])/len(times[1:]):.2f}ms")
    
    return avg_time

def test_learning_mechanism():
    """Test the learning and memory functionality"""
    print("\n" + "=" * 60)
    print("LEARNING MECHANISM TESTS")
    print("=" * 60)
    
    # Create a temporary corrector for testing
    corrector = BrailleAutoCorrect(memory_file="test_memory.json")
    
    # Test initial suggestion
    print("🧪 Testing learning capability...")
    
    # Before learning
    suggestions_before = corrector.suggest_words("xyz", max_suggestions=3)
    print(f"Before learning 'xyz': {[s[0] for s in suggestions_before[:3]]}")
    
    # Teach the system
    corrector.remember_choice("xyz", "cat")
    print("📚 Taught system: 'xyz' → 'cat'")
    
    # After learning
    suggestions_after = corrector.suggest_words("xyz", max_suggestions=3)
    print(f"After learning 'xyz': {[s[0] for s in suggestions_after[:3]]}")
    
    # Check if learning worked
    if suggestions_after and suggestions_after[0][0] == "cat":
        print("✅ Learning mechanism working correctly!")
    else:
        print("❌ Learning mechanism needs improvement")
    
    # Clean up test file
    import os
    if os.path.exists("test_memory.json"):
        os.remove("test_memory.json")
    
    return suggestions_after[0][0] == "cat" if suggestions_after else False

def test_edge_cases():
    """Test edge cases and error handling"""
    print("\n" + "=" * 60)
    print("EDGE CASE TESTS")
    print("=" * 60)
    
    corrector = BrailleAutoCorrect()
    
    edge_cases = [
        ("", "Empty string"),
        ("a", "Single character"),
        ("aaaaaa", "Repeated character"),
        ("123", "Numbers (should map to unknown)"),
        ("!@#", "Special characters"),
        ("verylongwordthatdoesntexist", "Very long non-existent word"),
    ]
    
    for test_input, description in edge_cases:
        try:
            suggestions = corrector.suggest_words(test_input, max_suggestions=1)
            result = suggestions[0][0] if suggestions else "NO_SUGGESTIONS"
            print(f"✅ {description}: '{test_input}' → '{result}'")
        except Exception as e:
            print(f"❌ {description}: '{test_input}' → ERROR: {e}")

def generate_report():
    """Generate a comprehensive test report"""
    print("\n" + "🔍" * 20)
    print("GENERATING COMPREHENSIVE TEST REPORT")
    print("🔍" * 20)
    
    # Run all tests
    start_time = time.time()
    
    accuracy_results, overall_accuracy = run_accuracy_tests()
    avg_performance = run_performance_tests()
    learning_works = test_learning_mechanism()
    test_edge_cases()
    
    end_time = time.time()
    total_test_time = end_time - start_time
    
    # Generate summary report
    print("\n" + "📊" * 20)
    print("FINAL SUMMARY REPORT")
    print("📊" * 20)
    
    corrector = BrailleAutoCorrect()
    stats = corrector.get_stats()
    
    report = {
        "Overall Accuracy": f"{overall_accuracy*100:.1f}%",
        "Average Processing Time": f"{avg_performance:.2f}ms",
        "Learning Mechanism": "✅ Working" if learning_works else "❌ Needs Fix",
        "Dictionary Size": stats["dictionary_size"],
        "Total Test Duration": f"{total_test_time:.2f}s",
        "Category Breakdown": accuracy_results
    }
    
    for key, value in report.items():
        if key != "Category Breakdown":
            print(f"🔹 {key}: {value}")
    
    print(f"\n📋 Accuracy by Category:")
    for category, accuracy in accuracy_results.items():
        print(f"   • {category}: {accuracy:.1f}%")
    
    # Save report to file
    with open("test_report.json", "w") as f:
        json.dump(report, f, indent=2)
    
    print(f"\n💾 Detailed report saved to: test_report.json")
    
    # Provide recommendations
    print(f"\n💡 RECOMMENDATIONS:")
    if overall_accuracy < 0.8:
        print("   • Consider expanding the dictionary")
        print("   • Fine-tune the distance threshold")
    if avg_performance > 10:
        print("   • Consider optimizing for larger dictionaries")
        print("   • Implement caching for frequent queries")
    if not learning_works:
        print("   • Fix the learning mechanism implementation")
    
    print("\n🎉 Testing completed successfully!")

if __name__ == "__main__":
    print("🧪 BRAILLE AUTO-CORRECT SYSTEM - COMPREHENSIVE TESTING")
    print("This will test accuracy, performance, learning, and edge cases\n")
    
    choice = input("Run full test suite? (y/n): ").strip().lower()
    if choice == 'y':
        generate_report()
    else:
        print("Available individual tests:")
        print("1. Accuracy tests")
        print("2. Performance tests") 
        print("3. Learning tests")
        print("4. Edge case tests")
        
        test_choice = input("Choose test (1-4): ").strip()
        if test_choice == "1":
            run_accuracy_tests()
        elif test_choice == "2":
            run_performance_tests()
        elif test_choice == "3":
            test_learning_mechanism()
        elif test_choice == "4":
            test_edge_cases()
        else:
            print("Invalid choice. Running full suite...")
            generate_report()