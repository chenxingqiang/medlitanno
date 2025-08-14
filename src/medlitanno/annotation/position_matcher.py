#!/usr/bin/env python3
"""
Position matching module for automatic text position calculation
"""

import re
import difflib
from typing import List, Tuple, Optional, Dict, Any
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class MatchResult:
    """Result of text matching"""
    text: str
    start_pos: int
    end_pos: int
    confidence: float  # 0.0 to 1.0
    matched_text: str  # Actual text found in the document
    

class TextPositionMatcher:
    """Automatically match text positions using various strategies"""
    
    def __init__(self, min_confidence: float = 0.8):
        """
        Initialize position matcher
        
        Args:
            min_confidence: Minimum confidence score for accepting a match
        """
        self.min_confidence = min_confidence
    
    def find_text_position(self, 
                          target_text: str, 
                          full_text: str, 
                          context_window: int = 50) -> Optional[MatchResult]:
        """
        Find the position of target text in full text using multiple strategies
        
        Args:
            target_text: Text to find
            full_text: Full document text
            context_window: Context window for fuzzy matching
            
        Returns:
            MatchResult or None if no good match found
        """
        # Strategy 1: Exact match
        exact_match = self._exact_match(target_text, full_text)
        if exact_match and exact_match.confidence >= self.min_confidence:
            return exact_match
        
        # Strategy 2: Case-insensitive match
        case_match = self._case_insensitive_match(target_text, full_text)
        if case_match and case_match.confidence >= self.min_confidence:
            return case_match
        
        # Strategy 3: Normalized match (remove extra spaces, punctuation)
        normalized_match = self._normalized_match(target_text, full_text)
        if normalized_match and normalized_match.confidence >= self.min_confidence:
            return normalized_match
        
        # Strategy 4: Fuzzy match using difflib
        fuzzy_match = self._fuzzy_match(target_text, full_text, context_window)
        if fuzzy_match and fuzzy_match.confidence >= self.min_confidence:
            return fuzzy_match
        
        # Strategy 5: Partial match (find best substring)
        partial_match = self._partial_match(target_text, full_text)
        if partial_match and partial_match.confidence >= self.min_confidence:
            return partial_match
        
        # If no good match found, return the best one we have
        best_match = max([m for m in [exact_match, case_match, normalized_match, fuzzy_match, partial_match] if m], 
                        key=lambda x: x.confidence, default=None)
        
        if best_match:
            logger.warning(f"Low confidence match for '{target_text[:50]}...': {best_match.confidence:.2f}")
        else:
            logger.warning(f"No match found for '{target_text[:50]}...'")
        
        return best_match
    
    def _exact_match(self, target_text: str, full_text: str) -> Optional[MatchResult]:
        """Find exact match"""
        start_pos = full_text.find(target_text)
        if start_pos != -1:
            end_pos = start_pos + len(target_text)
            return MatchResult(
                text=target_text,
                start_pos=start_pos,
                end_pos=end_pos,
                confidence=1.0,
                matched_text=target_text
            )
        return None
    
    def _case_insensitive_match(self, target_text: str, full_text: str) -> Optional[MatchResult]:
        """Find case-insensitive match"""
        target_lower = target_text.lower()
        full_lower = full_text.lower()
        
        start_pos = full_lower.find(target_lower)
        if start_pos != -1:
            end_pos = start_pos + len(target_text)
            matched_text = full_text[start_pos:end_pos]
            return MatchResult(
                text=target_text,
                start_pos=start_pos,
                end_pos=end_pos,
                confidence=0.95,
                matched_text=matched_text
            )
        return None
    
    def _normalized_match(self, target_text: str, full_text: str) -> Optional[MatchResult]:
        """Find match after normalizing whitespace and punctuation"""
        def normalize(text):
            # Remove extra whitespace and normalize punctuation
            text = re.sub(r'\s+', ' ', text.strip())
            text = re.sub(r'[^\w\s]', '', text)
            return text.lower()
        
        target_norm = normalize(target_text)
        full_norm = normalize(full_text)
        
        start_pos = full_norm.find(target_norm)
        if start_pos != -1:
            # Find the actual position in original text
            # This is approximate since normalization changes character positions
            words_before = len(full_norm[:start_pos].split())
            original_words = full_text.split()
            
            if words_before < len(original_words):
                # Find approximate position
                approx_start = len(' '.join(original_words[:words_before]))
                if approx_start > 0:
                    approx_start += 1  # Add space
                
                # Search around approximate position
                search_window = 100
                search_start = max(0, approx_start - search_window)
                search_end = min(len(full_text), approx_start + len(target_text) + search_window)
                search_text = full_text[search_start:search_end]
                
                # Try to find similar text in the window
                best_match = difflib.get_close_matches(target_text, [search_text], n=1, cutoff=0.6)
                if best_match:
                    actual_start = full_text.find(best_match[0], search_start)
                    if actual_start != -1:
                        actual_end = actual_start + len(best_match[0])
                        return MatchResult(
                            text=target_text,
                            start_pos=actual_start,
                            end_pos=actual_end,
                            confidence=0.85,
                            matched_text=best_match[0]
                        )
        return None
    
    def _fuzzy_match(self, target_text: str, full_text: str, context_window: int) -> Optional[MatchResult]:
        """Find fuzzy match using sliding window"""
        target_len = len(target_text)
        best_match = None
        best_ratio = 0
        
        # Use sliding window approach
        for i in range(0, len(full_text) - target_len + 1, max(1, target_len // 4)):
            window_text = full_text[i:i + target_len]
            ratio = difflib.SequenceMatcher(None, target_text, window_text).ratio()
            
            if ratio > best_ratio:
                best_ratio = ratio
                best_match = MatchResult(
                    text=target_text,
                    start_pos=i,
                    end_pos=i + target_len,
                    confidence=ratio * 0.9,  # Slightly lower confidence for fuzzy match
                    matched_text=window_text
                )
        
        return best_match if best_ratio > 0.7 else None
    
    def _partial_match(self, target_text: str, full_text: str) -> Optional[MatchResult]:
        """Find best partial match"""
        words = target_text.split()
        if len(words) < 2:
            return None
        
        best_match = None
        best_score = 0
        
        # Try different combinations of words
        for start_word in range(len(words)):
            for end_word in range(start_word + 1, len(words) + 1):
                partial_text = ' '.join(words[start_word:end_word])
                
                # Try to find this partial text
                start_pos = full_text.lower().find(partial_text.lower())
                if start_pos != -1:
                    end_pos = start_pos + len(partial_text)
                    # Score based on how much of the original text we matched
                    score = len(partial_text) / len(target_text)
                    
                    if score > best_score:
                        best_score = score
                        best_match = MatchResult(
                            text=target_text,
                            start_pos=start_pos,
                            end_pos=end_pos,
                            confidence=score * 0.8,  # Lower confidence for partial match
                            matched_text=full_text[start_pos:end_pos]
                        )
        
        return best_match
    
    def batch_match_positions(self, 
                             texts: List[str], 
                             full_text: str) -> List[Optional[MatchResult]]:
        """
        Match positions for multiple texts
        
        Args:
            texts: List of texts to match
            full_text: Full document text
            
        Returns:
            List of MatchResult or None for each input text
        """
        results = []
        for text in texts:
            result = self.find_text_position(text, full_text)
            results.append(result)
        return results
    
    def get_statistics(self, match_results: List[Optional[MatchResult]]) -> Dict[str, Any]:
        """Get matching statistics"""
        total = len(match_results)
        matched = sum(1 for r in match_results if r is not None)
        
        if matched > 0:
            avg_confidence = sum(r.confidence for r in match_results if r is not None) / matched
            min_confidence = min(r.confidence for r in match_results if r is not None)
            max_confidence = max(r.confidence for r in match_results if r is not None)
        else:
            avg_confidence = min_confidence = max_confidence = 0.0
        
        return {
            'total_texts': total,
            'matched_texts': matched,
            'match_rate': matched / total if total > 0 else 0.0,
            'average_confidence': avg_confidence,
            'min_confidence': min_confidence,
            'max_confidence': max_confidence
        }


def create_position_matcher(min_confidence: float = 0.8) -> TextPositionMatcher:
    """Create a configured position matcher"""
    return TextPositionMatcher(min_confidence=min_confidence)
