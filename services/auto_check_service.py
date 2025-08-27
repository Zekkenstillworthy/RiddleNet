"""
Auto-Check Interface for Non-Simulation Items
Extends auto-checking capabilities beyond simulations to assignments, quizzes, and essays
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Tuple
from config.defaults import get_default
import re
import json


class AutoCheckInterface(ABC):
    """Base interface for auto-checking different types of content"""
    
    @abstractmethod
    def check_content(self, content: Any, criteria: Dict[str, Any]) -> Dict[str, Any]:
        """
        Check content against criteria and return results
        
        Args:
            content: The content to check
            criteria: The checking criteria
            
        Returns:
            Dict containing check results with keys:
            - score: float (0-100)
            - feedback: str
            - details: Dict[str, Any]
            - passed: bool
        """
        pass
    
    @abstractmethod
    def get_supported_criteria(self) -> List[str]:
        """Return list of supported criteria types"""
        pass


class AssignmentAutoChecker(AutoCheckInterface):
    """Auto-checker for text-based assignments"""
    
    def check_content(self, content: str, criteria: Dict[str, Any]) -> Dict[str, Any]:
        """Check assignment text content"""
        if not content or not isinstance(content, str):
            return self._empty_result("No content provided")
        
        results = {
            'score': 0.0,
            'feedback': [],
            'details': {},
            'passed': False
        }
        
        total_weight = sum(criteria.get(key, {}).get('weight', 1.0) for key in criteria)
        weighted_score = 0.0
        
        # Word count check
        if 'word_count' in criteria:
            word_check = self._check_word_count(content, criteria['word_count'])
            weight = criteria['word_count'].get('weight', 1.0)
            weighted_score += word_check['score'] * weight
            results['feedback'].append(word_check['feedback'])
            results['details']['word_count'] = word_check
        
        # Keyword presence check
        if 'keywords' in criteria:
            keyword_check = self._check_keywords(content, criteria['keywords'])
            weight = criteria['keywords'].get('weight', 1.0)
            weighted_score += keyword_check['score'] * weight
            results['feedback'].append(keyword_check['feedback'])
            results['details']['keywords'] = keyword_check
        
        # Structure check (headings, paragraphs)
        if 'structure' in criteria:
            structure_check = self._check_structure(content, criteria['structure'])
            weight = criteria['structure'].get('weight', 1.0)
            weighted_score += structure_check['score'] * weight
            results['feedback'].append(structure_check['feedback'])
            results['details']['structure'] = structure_check
        
        # Citation check
        if 'citations' in criteria:
            citation_check = self._check_citations(content, criteria['citations'])
            weight = criteria['citations'].get('weight', 1.0)
            weighted_score += citation_check['score'] * weight
            results['feedback'].append(citation_check['feedback'])
            results['details']['citations'] = citation_check
        
        # Grammar and spelling check (basic)
        if 'grammar' in criteria:
            grammar_check = self._check_grammar(content, criteria['grammar'])
            weight = criteria['grammar'].get('weight', 1.0)
            weighted_score += grammar_check['score'] * weight
            results['feedback'].append(grammar_check['feedback'])
            results['details']['grammar'] = grammar_check
        
        # Calculate final score
        if total_weight > 0:
            results['score'] = min(100.0, weighted_score / total_weight)
        
        min_passing = get_default('grading.min_passing_percentage', 60)
        results['passed'] = results['score'] >= min_passing
        
        # Combine feedback
        results['feedback'] = ' '.join(filter(None, results['feedback']))
        
        return results
    
    def get_supported_criteria(self) -> List[str]:
        return ['word_count', 'keywords', 'structure', 'citations', 'grammar']
    
    def _check_word_count(self, content: str, criteria: Dict[str, Any]) -> Dict[str, Any]:
        """Check if content meets word count requirements"""
        words = len(content.split())
        min_words = criteria.get('min', 0)
        max_words = criteria.get('max', float('inf'))
        target_words = criteria.get('target')
        
        if target_words:
            # Check against target with tolerance
            tolerance = criteria.get('tolerance', 0.1)  # 10% tolerance
            min_target = target_words * (1 - tolerance)
            max_target = target_words * (1 + tolerance)
            
            if min_target <= words <= max_target:
                score = 100.0
                feedback = f"Word count ({words}) meets target ({target_words})."
            else:
                diff = abs(words - target_words)
                penalty = min(50, (diff / target_words) * 100)
                score = max(0, 100 - penalty)
                feedback = f"Word count ({words}) differs from target ({target_words})."
        else:
            # Check against min/max range
            if min_words <= words <= max_words:
                score = 100.0
                feedback = f"Word count ({words}) is within acceptable range."
            elif words < min_words:
                penalty = ((min_words - words) / min_words) * 50
                score = max(0, 100 - penalty)
                feedback = f"Word count ({words}) is below minimum ({min_words})."
            else:
                penalty = ((words - max_words) / max_words) * 25
                score = max(0, 100 - penalty)
                feedback = f"Word count ({words}) exceeds maximum ({max_words})."
        
        return {
            'score': score,
            'feedback': feedback,
            'word_count': words,
            'requirements': criteria
        }
    
    def _check_keywords(self, content: str, criteria: Dict[str, Any]) -> Dict[str, Any]:
        """Check for presence of required keywords"""
        required_keywords = criteria.get('required', [])
        optional_keywords = criteria.get('optional', [])
        
        content_lower = content.lower()
        found_required = []
        found_optional = []
        
        for keyword in required_keywords:
            if keyword.lower() in content_lower:
                found_required.append(keyword)
        
        for keyword in optional_keywords:
            if keyword.lower() in content_lower:
                found_optional.append(keyword)
        
        # Score based on required keywords found
        required_score = (len(found_required) / len(required_keywords) * 100) if required_keywords else 100
        
        # Bonus for optional keywords
        optional_bonus = min(20, len(found_optional) * 5) if optional_keywords else 0
        
        total_score = min(100, required_score + optional_bonus)
        
        feedback_parts = []
        if found_required:
            feedback_parts.append(f"Found required keywords: {', '.join(found_required)}")
        if len(found_required) < len(required_keywords):
            missing = set(required_keywords) - set(found_required)
            feedback_parts.append(f"Missing keywords: {', '.join(missing)}")
        if found_optional:
            feedback_parts.append(f"Bonus keywords found: {', '.join(found_optional)}")
        
        return {
            'score': total_score,
            'feedback': '. '.join(feedback_parts),
            'found_required': found_required,
            'found_optional': found_optional,
            'missing_required': list(set(required_keywords) - set(found_required))
        }
    
    def _check_structure(self, content: str, criteria: Dict[str, Any]) -> Dict[str, Any]:
        """Check document structure (paragraphs, headings, etc.)"""
        paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
        headings = re.findall(r'^#+\s+(.+)$', content, re.MULTILINE)
        
        min_paragraphs = criteria.get('min_paragraphs', 0)
        required_headings = criteria.get('required_headings', [])
        
        score = 100.0
        feedback_parts = []
        
        # Check paragraph count
        if len(paragraphs) < min_paragraphs:
            penalty = ((min_paragraphs - len(paragraphs)) / min_paragraphs) * 30
            score -= penalty
            feedback_parts.append(f"Has {len(paragraphs)} paragraphs, needs {min_paragraphs}")
        else:
            feedback_parts.append(f"Has {len(paragraphs)} paragraphs")
        
        # Check for required headings
        if required_headings:
            content_lower = content.lower()
            found_headings = []
            for heading in required_headings:
                if heading.lower() in content_lower:
                    found_headings.append(heading)
            
            if len(found_headings) < len(required_headings):
                penalty = ((len(required_headings) - len(found_headings)) / len(required_headings)) * 30
                score -= penalty
                missing = set(required_headings) - set(found_headings)
                feedback_parts.append(f"Missing headings: {', '.join(missing)}")
        
        return {
            'score': max(0, score),
            'feedback': '. '.join(feedback_parts),
            'paragraph_count': len(paragraphs),
            'headings_found': headings
        }
    
    def _check_citations(self, content: str, criteria: Dict[str, Any]) -> Dict[str, Any]:
        """Check for citations and references"""
        min_citations = criteria.get('min_citations', 0)
        citation_format = criteria.get('format', 'any')  # 'apa', 'mla', 'chicago', 'any'
        
        # Basic citation patterns
        patterns = {
            'any': [
                r'\([^)]*\d{4}[^)]*\)',  # (Author, 2023)
                r'\[[^\]]*\d{4}[^\]]*\]',  # [Author, 2023]
                r'(?:Retrieved|Available)\s+from\s+https?://',  # URL citations
            ],
            'apa': [r'\([^)]*\d{4}[^)]*\)'],
            'mla': [r'\([^)]*[A-Z][a-z]+[^)]*\)'],
            'chicago': [r'\d+\.?\s+[A-Z][a-z]+']
        }
        
        citation_patterns = patterns.get(citation_format, patterns['any'])
        citations_found = []
        
        for pattern in citation_patterns:
            citations_found.extend(re.findall(pattern, content))
        
        citation_count = len(citations_found)
        
        if citation_count >= min_citations:
            score = 100.0
            feedback = f"Found {citation_count} citations (minimum {min_citations})"
        else:
            penalty = ((min_citations - citation_count) / min_citations) * 50
            score = max(0, 100 - penalty)
            feedback = f"Found {citation_count} citations, needs {min_citations}"
        
        return {
            'score': score,
            'feedback': feedback,
            'citations_found': citation_count,
            'citations_list': citations_found[:5]  # First 5 citations
        }
    
    def _check_grammar(self, content: str, criteria: Dict[str, Any]) -> Dict[str, Any]:
        """Basic grammar and spelling check"""
        # Simple grammar checks
        issues = []
        
        # Check for common issues
        if re.search(r'\.\s*[a-z]', content):  # Sentence should start with capital
            issues.append("Some sentences may not start with capital letters")
        
        if re.search(r'[a-zA-Z]\s{2,}[a-zA-Z]', content):  # Multiple spaces
            issues.append("Multiple consecutive spaces found")
        
        if re.search(r'[.!?]{2,}', content):  # Multiple punctuation
            issues.append("Multiple consecutive punctuation marks found")
        
        # Count sentences without proper punctuation
        sentences = re.split(r'[.!?]+', content)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        # Basic score calculation
        penalty = min(30, len(issues) * 10)
        score = max(0, 100 - penalty)
        
        feedback = f"Basic grammar check: {len(issues)} potential issues found" if issues else "Basic grammar check passed"
        
        return {
            'score': score,
            'feedback': feedback,
            'issues': issues,
            'sentence_count': len(sentences)
        }
    
    def _empty_result(self, message: str) -> Dict[str, Any]:
        """Return empty result with error message"""
        return {
            'score': 0.0,
            'feedback': message,
            'details': {},
            'passed': False
        }


class QuizAutoChecker(AutoCheckInterface):
    """Auto-checker for quiz responses"""
    
    def check_content(self, content: Dict[str, Any], criteria: Dict[str, Any]) -> Dict[str, Any]:
        """Check quiz responses against answer keys"""
        if not content or not isinstance(content, dict):
            return self._empty_result("No quiz responses provided")
        
        responses = content.get('responses', {})
        answer_key = criteria.get('answer_key', {})
        partial_credit = get_default('grading.partial_credit_enabled', True)
        
        if not answer_key:
            return self._empty_result("No answer key provided")
        
        total_questions = len(answer_key)
        if total_questions == 0:
            return self._empty_result("No questions to check")
        
        correct_count = 0
        partial_points = 0.0
        question_results = {}
        
        for question_id, correct_answer in answer_key.items():
            user_answer = responses.get(question_id)
            question_result = self._check_single_answer(user_answer, correct_answer, partial_credit)
            question_results[question_id] = question_result
            
            if question_result['correct']:
                correct_count += 1
            elif partial_credit:
                partial_points += question_result['partial_score']
        
        # Calculate final score
        total_score = correct_count + partial_points
        percentage = (total_score / total_questions) * 100
        
        min_passing = get_default('grading.min_passing_percentage', 60)
        passed = percentage >= min_passing
        
        feedback = f"Answered {correct_count}/{total_questions} questions correctly"
        if partial_credit and partial_points > 0:
            feedback += f" with {partial_points:.1f} partial credit points"
        
        return {
            'score': percentage,
            'feedback': feedback,
            'details': {
                'correct_count': correct_count,
                'total_questions': total_questions,
                'partial_points': partial_points,
                'question_results': question_results
            },
            'passed': passed
        }
    
    def get_supported_criteria(self) -> List[str]:
        return ['answer_key', 'partial_credit_rules', 'question_weights']
    
    def _check_single_answer(self, user_answer: Any, correct_answer: Any, partial_credit: bool) -> Dict[str, Any]:
        """Check a single quiz answer"""
        if user_answer is None:
            return {'correct': False, 'partial_score': 0.0, 'feedback': 'No answer provided'}
        
        # Handle different question types
        if isinstance(correct_answer, dict):
            question_type = correct_answer.get('type', 'multiple_choice')
            correct_value = correct_answer.get('answer')
            
            if question_type == 'multiple_choice':
                correct = str(user_answer).strip().lower() == str(correct_value).strip().lower()
                return {
                    'correct': correct,
                    'partial_score': 0.0,
                    'feedback': 'Correct' if correct else f'Incorrect. Correct answer: {correct_value}'
                }
            
            elif question_type == 'multiple_select':
                user_set = set(user_answer) if isinstance(user_answer, list) else {user_answer}
                correct_set = set(correct_value) if isinstance(correct_value, list) else {correct_value}
                
                if user_set == correct_set:
                    return {'correct': True, 'partial_score': 0.0, 'feedback': 'Correct'}
                elif partial_credit:
                    intersection = user_set & correct_set
                    partial_score = len(intersection) / len(correct_set) if correct_set else 0
                    return {
                        'correct': False,
                        'partial_score': partial_score,
                        'feedback': f'Partially correct ({len(intersection)}/{len(correct_set)} correct)'
                    }
                else:
                    return {'correct': False, 'partial_score': 0.0, 'feedback': 'Incorrect'}
            
            elif question_type == 'text':
                # Text comparison with partial matching
                user_text = str(user_answer).strip().lower()
                correct_text = str(correct_value).strip().lower()
                
                if user_text == correct_text:
                    return {'correct': True, 'partial_score': 0.0, 'feedback': 'Correct'}
                elif partial_credit:
                    # Simple similarity check (could be enhanced)
                    similarity = self._text_similarity(user_text, correct_text)
                    if similarity > 0.8:
                        return {'correct': False, 'partial_score': 0.8, 'feedback': 'Very close, mostly correct'}
                    elif similarity > 0.5:
                        return {'correct': False, 'partial_score': 0.5, 'feedback': 'Partially correct'}
                    else:
                        return {'correct': False, 'partial_score': 0.0, 'feedback': 'Incorrect'}
                else:
                    return {'correct': False, 'partial_score': 0.0, 'feedback': 'Incorrect'}
        
        else:
            # Simple value comparison
            correct = str(user_answer).strip() == str(correct_answer).strip()
            return {
                'correct': correct,
                'partial_score': 0.0,
                'feedback': 'Correct' if correct else f'Incorrect. Correct answer: {correct_answer}'
            }
    
    def _text_similarity(self, text1: str, text2: str) -> float:
        """Calculate simple text similarity"""
        words1 = set(text1.split())
        words2 = set(text2.split())
        
        if not words1 and not words2:
            return 1.0
        if not words1 or not words2:
            return 0.0
        
        intersection = words1 & words2
        union = words1 | words2
        
        return len(intersection) / len(union) if union else 0.0
    
    def _empty_result(self, message: str) -> Dict[str, Any]:
        """Return empty result with error message"""
        return {
            'score': 0.0,
            'feedback': message,
            'details': {},
            'passed': False
        }


class AutoCheckManager:
    """Manager for coordinating different auto-checkers"""
    
    def __init__(self):
        self.checkers = {
            'assignment': AssignmentAutoChecker(),
            'quiz': QuizAutoChecker(),
            # Add more checkers as needed
        }
    
    def check_content(self, content_type: str, content: Any, criteria: Dict[str, Any]) -> Dict[str, Any]:
        """Route content to appropriate checker"""
        checker = self.checkers.get(content_type)
        if not checker:
            return {
                'score': 0.0,
                'feedback': f'No auto-checker available for content type: {content_type}',
                'details': {},
                'passed': False
            }
        
        return checker.check_content(content, criteria)
    
    def get_supported_types(self) -> List[str]:
        """Get list of supported content types"""
        return list(self.checkers.keys())
    
    def get_criteria_for_type(self, content_type: str) -> List[str]:
        """Get supported criteria for a content type"""
        checker = self.checkers.get(content_type)
        return checker.get_supported_criteria() if checker else []


# Global auto-check manager instance
auto_check_manager = AutoCheckManager()
