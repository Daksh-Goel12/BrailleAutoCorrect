from typing import List, Tuple, Dict
import heapq
import json
import os
import time
from collections import defaultdict

class BrailleAutoCorrect:
    def __init__(self, dictionary_file="sample_dictionary.txt", memory_file="memory.json"):
        self.braille_map = {
            'a': '100000', 'b': '110000', 'c': '100100', 'd': '100110', 'e': '100010',
            'f': '110100', 'g': '110110', 'h': '110010', 'i': '010100', 'j': '010110',
            'k': '101000', 'l': '111000', 'm': '101100', 'n': '101110', 'o': '101010',
            'p': '111100', 'q': '111110', 'r': '111010', 's': '011100', 't': '011110',
            'u': '101001', 'v': '111001', 'w': '010111', 'x': '101101', 'y': '101111', 'z': '101011'
        }
        
        self.dictionary = self.load_dictionary(dictionary_file)
        self.memory_file = memory_file
        self.user_corrections = self.load_memory()
        
        # Optimization: Pre-compute braille patterns and group by length
        self.braille_words = {}
        self.words_by_length = defaultdict(list)
        self._preprocess_dictionary()
    
    def load_dictionary(self, filename: str) -> List[str]:
        """Load dictionary from file"""
        try:
            with open(filename, "r") as f:
                return [line.strip().lower() for line in f.readlines() if line.strip()]
        except FileNotFoundError:
            print(f"Warning: {filename} not found. Using default words.")
            return ["cat", "cap", "bat", "rat", "car", "dog", "can", "help", "hello"]
    
    def load_memory(self) -> Dict[str, str]:
        """Load user correction history"""
        if os.path.exists(self.memory_file):
            try:
                with open(self.memory_file, "r") as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def _preprocess_dictionary(self):
        """Pre-compute braille patterns for efficiency"""
        for word in self.dictionary:
            braille_pattern = self.word_to_braille(word)
            self.braille_words[word] = braille_pattern
            self.words_by_length[len(braille_pattern)].append(word)
    
    def word_to_braille(self, word: str) -> str:
        """Convert word to braille pattern"""
        return ''.join(self.braille_map.get(c.lower(), '000000') for c in word)
    
    def levenshtein_optimized(self, s1: str, s2: str, max_distance: int = None) -> int:
        """Optimized Levenshtein distance with early termination"""
        if abs(len(s1) - len(s2)) > (max_distance or float('inf')):
            return max_distance + 1 if max_distance else abs(len(s1) - len(s2))
        
        n, m = len(s1), len(s2)
        if n > m:
            s1, s2, n, m = s2, s1, m, n
        
        current_row = list(range(n + 1))
        for i in range(1, m + 1):
            previous_row, current_row = current_row, [i] + [0] * n
            for j in range(1, n + 1):
                add, delete, change = previous_row[j] + 1, current_row[j - 1] + 1, previous_row[j - 1]
                if s1[j - 1] != s2[i - 1]:
                    change += 1
                current_row[j] = min(add, delete, change)
            
            # Early termination if all values exceed threshold
            if max_distance and min(current_row) > max_distance:
                return max_distance + 1
        
        return current_row[n]
    

    def suggest_words(self, input_word: str, max_suggestions: int = 5, max_distance: int = None) -> List[Tuple[str, int, float]]:
        """
        Suggest words with confidence scores
        Returns: List of (word, distance, confidence_score)
        """
        input_word = input_word.lower()

        # Check learned corrections first
        if input_word in self.user_corrections:
            learned_word = self.user_corrections[input_word]
            if learned_word in self.dictionary:
                return [(learned_word, 0, 1.0)]
        
        input_braille = self.word_to_braille(input_word)
        input_len = len(input_braille)

        # Set adaptive max_distance based on input length
        if max_distance is None:
            if len(input_word) <= 3:
                max_distance = 6
            elif len(input_word) <= 5:
                max_distance = 5
            else:
                max_distance = 4

        suggestions = []
        search_lengths = [input_len]
        for i in range(1, max_distance + 1):
            if input_len - i > 0:
                search_lengths.append(input_len - i)
            search_lengths.append(input_len + i)

        for length in search_lengths:
            if length in self.words_by_length:
                for word in self.words_by_length[length]:
                    word_braille = self.braille_words[word]
                    distance = self.levenshtein_optimized(input_braille, word_braille, max_distance)

                    if distance <= max_distance:
                        # Improved confidence: based on combined length, not just max()
                        confidence = 1.0 - (distance / (len(input_braille) + len(word_braille)))

                        # Bonus if it's a learned correction
                        if word in self.user_corrections.values():
                            confidence += 0.1
                        
                        suggestions.append((word, distance, round(confidence, 3)))

        # Sort: lowest distance, then highest confidence
        suggestions.sort(key=lambda x: (x[1], -x[2]))

        # Fallback: if no results, return top closest even if over distance
        if not suggestions:
            fallback = [(word, self.levenshtein_optimized(input_braille, braille), 0.0)
                        for word, braille in self.braille_words.items()]
            fallback.sort(key=lambda x: x[1])
            return fallback[:1]

        return suggestions[:max_suggestions]


    def remember_choice(self, typed: str, corrected: str):
        """Store user correction for learning"""
        self.user_corrections[typed.lower()] = corrected.lower()
        try:
            with open(self.memory_file, "w") as f:
                json.dump(self.user_corrections, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save correction memory: {e}")
    
    def get_stats(self) -> Dict:
        """Get system statistics"""
        return {
            "dictionary_size": len(self.dictionary),
            "learned_corrections": len(self.user_corrections),
            "braille_patterns_cached": len(self.braille_words)
        }

def run_tests():
    """Test cases to demonstrate system effectiveness"""
    print("=" * 50)
    print("BRAILLE AUTO-CORRECT SYSTEM - TEST CASES")
    print("=" * 50)
    
    corrector = BrailleAutoCorrect()
    
    test_cases = [
        ("cak", "cap"),  # Basic typo
        ("dg", "dog"),   # Missing letter
        ("cann", "can"), # Extra letter
        ("baat", "bat"), # Multiple errors
        ("helllo", "hello"), # Common typo
        ("hoppe", "hope"), # Similar word
    ]
    
    total_correct = 0
    
    for i, (input_word, expected) in enumerate(test_cases, 1):
        start_time = time.time()
        suggestions = corrector.suggest_words(input_word, max_suggestions=3)
        end_time = time.time()
        
        print(f"\nTest {i}: Input '{input_word}' -> Expected: '{expected}'")
        print(f"Processing time: {(end_time - start_time)*1000:.2f}ms")
        
        if suggestions:
            top_suggestion = suggestions[0][0]
            print(f"Top suggestion: '{top_suggestion}' (distance: {suggestions[0][1]}, confidence: {suggestions[0][2]:.2f})")
            
            if top_suggestion == expected:
                total_correct += 1
                print("✅ CORRECT")
            else:
                print("❌ INCORRECT")
            
            if len(suggestions) > 1:
                print("Other suggestions:", [f"{s[0]} ({s[1]})" for s in suggestions[1:]])
        else:
            print("❌ No suggestions found")
    
    print(f"\n" + "=" * 30)
    print(f"ACCURACY: {total_correct}/{len(test_cases)} ({total_correct/len(test_cases)*100:.1f}%)")
    print(f"SYSTEM STATS: {corrector.get_stats()}")
    print("=" * 30)

def main():
    """Main CLI interface"""
    print("Enhanced Braille Auto-Correct System")
    print("Type 'test' to run test cases, 'quit' to exit")
    
    corrector = BrailleAutoCorrect()
    
    while True:
        user_input = input("\nEnter Braille word (QWERTY-style): ").strip()
        
        if user_input.lower() == 'quit':
            break
        elif user_input.lower() == 'test':
            run_tests()
            continue
        elif not user_input:
            continue
        
        start_time = time.time()
        suggestions = corrector.suggest_words(user_input, max_suggestions=3)
        end_time = time.time()
        
        if suggestions:
            print(f"\nSuggestions (processed in {(end_time-start_time)*1000:.1f}ms):")
            for i, (word, distance, confidence) in enumerate(suggestions, 1):
                print(f"{i}. {word} (confidence: {confidence:.2f})")
            
            # Ask if user wants to confirm correction for learning
            if suggestions:
                choice = input(f"\nIs '{suggestions[0][0]}' correct? (y/n): ").strip().lower()
                if choice == 'y':
                    corrector.remember_choice(user_input, suggestions[0][0])
                    print("✅ Correction saved for future learning!")
        else:
            print("No suggestions found. Try a different input.")

# Backward compatibility functions for existing code
def load_dictionary(filename="sample_dictionary.txt") -> List[str]:
    """Backward compatibility function"""
    corrector = BrailleAutoCorrect(filename)
    return corrector.dictionary

def suggest_word(input_word: str, dictionary: List[str], memory_file="memory.json") -> str:
    """Backward compatibility function"""
    corrector = BrailleAutoCorrect(memory_file=memory_file)
    corrector.dictionary = dictionary
    corrector._preprocess_dictionary()
    
    suggestions = corrector.suggest_words(input_word, max_suggestions=1)
    if suggestions:
        best_word = suggestions[0][0]
        corrector.remember_choice(input_word, best_word)
        return best_word
    return input_word

if __name__ == "__main__":
    main()