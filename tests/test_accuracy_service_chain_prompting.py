"""
Tests for ChainPromptingAccuracyService - TDD approach for chain prompting architecture

These tests verify that:
1. Each task (quotes, reels, warnings, chapters) uses separate API calls
2. Each call has a focused, single-task prompt
3. Chapter generation uses two-step chain: titles first, then timestamps
4. Output format matches HighAccuracyContentService for drop-in compatibility
"""

import pytest
import json
from unittest.mock import Mock, patch, call
from services.accuracy_service_chain_prompting import ChainPromptingAccuracyService


class TestChainPromptingArchitecture:
    """Test that chain prompting uses separate API calls for each task"""

    @pytest.fixture
    def service(self):
        """Create service instance with mock API key"""
        return ChainPromptingAccuracyService(api_key="test_api_key")

    @pytest.fixture
    def sample_transcript(self):
        """Sample transcript for testing"""
        return """00:00:15 speaker_0: Welcome to the show! Today we're discussing AI.
00:01:30 speaker_1: Thanks for having me. AI is transforming everything.
00:03:45 speaker_0: Let's talk about the future of automation.
00:05:20 speaker_1: Automation will change how we work fundamentally.
00:08:00 speaker_0: What about ethics in AI development?
00:10:15 speaker_1: Ethics must be our top priority."""

    @pytest.fixture
    def episode_info(self):
        """Sample episode info"""
        return {
            "show": "Tech Talk",
            "host": "John Doe",
            "guest": "Jane Smith",
            "episode_number": "42"
        }

    @patch('services.accuracy_service_chain_prompting.genai.Client')
    def test_each_task_uses_separate_api_call(self, mock_client_class, service, sample_transcript, episode_info):
        """
        CRITICAL TEST: Verify that quotes, reels, warnings, chapters each make separate API calls.
        This is the core of chain prompting architecture.
        """
        # Setup mock client
        mock_client = Mock()
        mock_client_class.return_value = mock_client

        # Mock responses for each separate call
        mock_responses = [
            Mock(text='{"quotable_moments": [{"quote": "AI is transforming everything", "timestamp": "01:30", "context": "intro", "speaker": "speaker_1"}]}'),
            Mock(text='{"reel_suggestions": [{"title": "AI Future", "start_time": "03:45", "end_time": "05:20", "description": "test", "hook": "test", "closing": "test", "editing_instructions": "test", "confidence_level": "high"}]}'),
            Mock(text='{"content_warnings": ["No warnings"]}'),
            Mock(text='{"chapter_titles": ["Introduction", "AI Ethics"]}'),
            Mock(text='{"timestamp": "00:15"}'),  # First chapter timestamp
            Mock(text='{"timestamp": "08:00"}'),  # Second chapter timestamp
        ]

        mock_client.models.generate_content.side_effect = mock_responses

        # Execute
        service.client = mock_client
        result = service.generate_accuracy_critical_content(sample_transcript, episode_info, "en")

        # Verify: Should have made multiple separate API calls
        # Minimum: quotes (1) + reels (1) + warnings (1) + chapter_titles (1) + timestamps (2) = 6 calls
        assert mock_client.models.generate_content.call_count >= 4, \
            f"Expected at least 4 separate API calls (quotes, reels, warnings, chapters), got {mock_client.models.generate_content.call_count}"

        # Verify result has all required sections
        assert "quotable_moments" in result
        assert "reel_suggestions" in result
        assert "content_warnings" in result
        assert "chapter_timestamps" in result

    @patch('services.accuracy_service_chain_prompting.genai.Client')
    def test_quotable_moments_focused_prompt(self, mock_client_class, service, sample_transcript):
        """
        Verify quotable moments gets a focused prompt asking ONLY for quotes.
        No mixing of tasks in single prompt.
        """
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        mock_client.models.generate_content.return_value = Mock(
            text='{"quotable_moments": [{"quote": "test", "timestamp": "01:30", "context": "test", "speaker": "speaker_1"}]}'
        )

        service.client = mock_client
        service._generate_quotable_moments(sample_transcript, "en")

        # Get the prompt that was sent
        call_args = mock_client.models.generate_content.call_args
        prompt = call_args.kwargs['contents']

        # Verify prompt focuses ONLY on quotable moments
        assert "quotable" in prompt.lower() or "quote" in prompt.lower(), \
            "Prompt should focus on quotable moments"

        # Verify prompt does NOT ask for reels, warnings, or chapters
        assert "reel" not in prompt.lower() or "reel suggestions" not in prompt.lower(), \
            "Quotable moments prompt should NOT ask for reels"
        assert "chapter" not in prompt.lower() or "chapter_timestamps" not in prompt.lower(), \
            "Quotable moments prompt should NOT ask for chapters"

    @patch('services.accuracy_service_chain_prompting.genai.Client')
    def test_reel_suggestions_focused_prompt(self, mock_client_class, service, sample_transcript):
        """
        Verify reel suggestions gets a focused prompt asking ONLY for reels.
        """
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        mock_client.models.generate_content.return_value = Mock(
            text='{"reel_suggestions": [{"title": "test", "start_time": "03:45", "end_time": "05:20", "description": "test", "hook": "test", "closing": "test", "editing_instructions": "test", "confidence_level": "high"}]}'
        )

        service.client = mock_client
        service._generate_reel_suggestions(sample_transcript, "en")

        # Get the prompt
        call_args = mock_client.models.generate_content.call_args
        prompt = call_args.kwargs['contents']

        # Verify focused on reels only
        assert "reel" in prompt.lower(), "Prompt should focus on reels"
        assert "short" in prompt.lower() or "video" in prompt.lower(), \
            "Prompt should mention short-form content"

    @patch('services.accuracy_service_chain_prompting.genai.Client')
    def test_chapter_generation_is_two_step_chain(self, mock_client_class, service, sample_transcript):
        """
        CRITICAL TEST: Verify chapters use TWO-STEP CHAIN:
        Step 1: Get chapter titles (no timestamps)
        Step 2: For each title, find its specific timestamp

        This tests the core innovation of chain prompting.
        """
        mock_client = Mock()
        mock_client_class.return_value = mock_client

        # Mock two separate calls: titles first, then timestamps
        mock_responses = [
            Mock(text='{"chapter_titles": ["Introduction to AI", "Future of Automation", "Ethics Discussion"]}'),
            Mock(text='{"timestamp": "00:15"}'),  # Timestamp for title 1
            Mock(text='{"timestamp": "03:45"}'),  # Timestamp for title 2
            Mock(text='{"timestamp": "08:00"}'),  # Timestamp for title 3
        ]
        mock_client.models.generate_content.side_effect = mock_responses

        service.client = mock_client
        result = service._generate_chapter_timestamps(sample_transcript, "en")

        # Verify multiple calls were made
        assert mock_client.models.generate_content.call_count >= 2, \
            "Chapter generation should make at least 2 calls (titles + timestamps)"

        # Verify result has timestamps attached to titles
        assert isinstance(result, list), "Should return list of chapter strings"
        assert len(result) > 0, "Should have at least one chapter"

        # Each chapter should have timestamp format: "HH:MM:SS Title"
        for chapter in result:
            assert ":" in chapter, f"Chapter should have timestamp: {chapter}"

    @patch('services.accuracy_service_chain_prompting.genai.Client')
    def test_chapter_step1_returns_titles_without_timestamps(self, mock_client_class, service, sample_transcript):
        """
        First chapter call should return ONLY topic titles, no timestamps.
        Timestamps come in step 2.
        """
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        mock_client.models.generate_content.return_value = Mock(
            text='{"chapter_titles": ["Introduction", "Main Discussion", "Conclusion"]}'
        )

        service.client = mock_client
        titles = service._get_chapter_titles(sample_transcript, "en")

        # Verify returns list of title strings
        assert isinstance(titles, list), "Should return list of titles"
        assert len(titles) > 0, "Should have at least one title"

        # Verify titles do NOT contain timestamps yet
        for title in titles:
            assert ":" not in title or title.count(":") == 0, \
                f"Title should not have timestamp yet: {title}"

    @patch('services.accuracy_service_chain_prompting.genai.Client')
    def test_chapter_step2_finds_timestamp_for_specific_title(self, mock_client_class, service, sample_transcript):
        """
        Second chapter call should search for a specific title's timestamp.
        Gets one timestamp per call.
        """
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        mock_client.models.generate_content.return_value = Mock(
            text='{"timestamp": "03:45"}'
        )

        service.client = mock_client
        timestamp = service._find_chapter_timestamp(sample_transcript, "Introduction to AI", "en")

        # Verify returns timestamp string
        assert isinstance(timestamp, str), "Should return timestamp string"
        assert ":" in timestamp, "Should be valid timestamp format (MM:SS or HH:MM:SS)"

        # Verify the prompt asked for specific title
        call_args = mock_client.models.generate_content.call_args
        prompt = call_args.kwargs['contents']
        assert "Introduction to AI" in prompt, \
            "Prompt should mention the specific chapter title to find"


class TestOutputCompatibility:
    """Test that output format matches HighAccuracyContentService for drop-in compatibility"""

    @pytest.fixture
    def service(self):
        return ChainPromptingAccuracyService(api_key="test_api_key")

    @pytest.fixture
    def sample_transcript(self):
        return """00:00:15 speaker_0: Welcome!
00:01:30 speaker_1: Thanks for having me."""

    @patch('services.accuracy_service_chain_prompting.genai.Client')
    def test_output_format_matches_original_service(self, mock_client_class, service, sample_transcript):
        """
        Output JSON must match HighAccuracyContentService for A/B testing compatibility.

        Expected structure:
        {
            "quotable_moments": [...],
            "reel_suggestions": [...],
            "content_warnings": [...],
            "chapter_timestamps": [...]
        }
        """
        mock_client = Mock()
        mock_client_class.return_value = mock_client

        # Mock all responses
        mock_responses = [
            Mock(text='{"quotable_moments": [{"quote": "test", "timestamp": "01:30", "context": "intro", "speaker": "speaker_1"}]}'),
            Mock(text='{"reel_suggestions": [{"title": "test", "start_time": "00:15", "end_time": "01:30", "description": "test", "hook": "test", "closing": "test", "editing_instructions": "test", "confidence_level": "high"}]}'),
            Mock(text='{"content_warnings": ["test warning"]}'),
            Mock(text='{"chapter_titles": ["Introduction"]}'),
            Mock(text='{"timestamp": "00:15"}'),
        ]
        mock_client.models.generate_content.side_effect = mock_responses

        service.client = mock_client
        result = service.generate_accuracy_critical_content(sample_transcript, language="en")

        # Verify all required keys exist
        assert "quotable_moments" in result, "Missing quotable_moments"
        assert "reel_suggestions" in result, "Missing reel_suggestions"
        assert "content_warnings" in result, "Missing content_warnings"
        assert "chapter_timestamps" in result, "Missing chapter_timestamps"

        # Verify types
        assert isinstance(result["quotable_moments"], list), "quotable_moments should be list"
        assert isinstance(result["reel_suggestions"], list), "reel_suggestions should be list"
        assert isinstance(result["content_warnings"], list), "content_warnings should be list"
        assert isinstance(result["chapter_timestamps"], list), "chapter_timestamps should be list"

        # Verify quotable moments structure
        if len(result["quotable_moments"]) > 0:
            quote = result["quotable_moments"][0]
            assert "quote" in quote, "Quote must have 'quote' field"
            assert "timestamp" in quote, "Quote must have 'timestamp' field"
            assert "context" in quote, "Quote must have 'context' field"
            assert "speaker" in quote, "Quote must have 'speaker' field"

        # Verify reel suggestions structure
        if len(result["reel_suggestions"]) > 0:
            reel = result["reel_suggestions"][0]
            assert "title" in reel, "Reel must have 'title'"
            assert "start_time" in reel, "Reel must have 'start_time'"
            assert "end_time" in reel, "Reel must have 'end_time'"
            assert "confidence_level" in reel, "Reel must have 'confidence_level'"

        # Verify chapter timestamps format
        if len(result["chapter_timestamps"]) > 0:
            chapter = result["chapter_timestamps"][0]
            assert isinstance(chapter, str), "Chapter should be string"
            assert ":" in chapter, "Chapter should contain timestamp"


class TestLanguageSupport:
    """Test multi-language support (Hebrew, English)"""

    @pytest.fixture
    def service(self):
        return ChainPromptingAccuracyService(api_key="test_api_key")

    @pytest.fixture
    def hebrew_transcript(self):
        return """00:00:15 speaker_0: שלום וברוכים הבאים לתוכנית
00:01:30 speaker_1: תודה שהזמנתם אותי"""

    @pytest.fixture
    def english_transcript(self):
        return """00:00:15 speaker_0: Welcome to the show
00:01:30 speaker_1: Thanks for having me"""

    @patch('services.accuracy_service_chain_prompting.genai.Client')
    def test_handles_hebrew_language(self, mock_client_class, service, hebrew_transcript):
        """Works with language='he' for Hebrew content"""
        mock_client = Mock()
        mock_client_class.return_value = mock_client

        # Mock responses
        mock_responses = [
            Mock(text='{"quotable_moments": [{"quote": "תודה שהזמנתם אותי", "timestamp": "01:30", "context": "פתיחה", "speaker": "speaker_1"}]}'),
            Mock(text='{"reel_suggestions": []}'),
            Mock(text='{"content_warnings": []}'),
            Mock(text='{"chapter_titles": ["פתיחה"]}'),
            Mock(text='{"timestamp": "00:15"}'),
        ]
        mock_client.models.generate_content.side_effect = mock_responses

        service.client = mock_client
        result = service.generate_accuracy_critical_content(hebrew_transcript, language="he")

        # Verify language instruction was included in prompts
        # Check first call (quotable moments)
        call_args = mock_client.models.generate_content.call_args_list[0]
        prompt = call_args.kwargs['contents']

        assert "hebrew" in prompt.lower() or "עברית" in prompt, \
            "Prompt should include Hebrew language instruction"

        # Verify result structure is valid
        assert "quotable_moments" in result

    @patch('services.accuracy_service_chain_prompting.genai.Client')
    def test_handles_english_language(self, mock_client_class, service, english_transcript):
        """Works with language='en' for English content"""
        mock_client = Mock()
        mock_client_class.return_value = mock_client

        mock_responses = [
            Mock(text='{"quotable_moments": [{"quote": "Thanks for having me", "timestamp": "01:30", "context": "intro", "speaker": "speaker_1"}]}'),
            Mock(text='{"reel_suggestions": []}'),
            Mock(text='{"content_warnings": []}'),
            Mock(text='{"chapter_titles": ["Introduction"]}'),
            Mock(text='{"timestamp": "00:15"}'),
        ]
        mock_client.models.generate_content.side_effect = mock_responses

        service.client = mock_client
        result = service.generate_accuracy_critical_content(english_transcript, language="en")

        # Verify English language instruction
        call_args = mock_client.models.generate_content.call_args_list[0]
        prompt = call_args.kwargs['contents']

        assert "english" in prompt.lower(), \
            "Prompt should include English language instruction"

        # Verify result structure
        assert "quotable_moments" in result


class TestErrorHandling:
    """Test error handling and edge cases"""

    @pytest.fixture
    def service(self):
        return ChainPromptingAccuracyService(api_key="test_api_key")

    @patch('services.accuracy_service_chain_prompting.genai.Client')
    def test_handles_api_failure_gracefully(self, mock_client_class, service):
        """Should return error structure if API call fails"""
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        mock_client.models.generate_content.side_effect = Exception("API Error")

        service.client = mock_client
        result = service.generate_accuracy_critical_content("test transcript", language="en")

        # Should return error response with all required keys
        assert "error" in result or all(k in result for k in ["quotable_moments", "reel_suggestions", "content_warnings", "chapter_timestamps"])

        # If error key exists, verify structure
        if "error" in result:
            assert isinstance(result["error"], str)
            assert "quotable_moments" in result
            assert "reel_suggestions" in result
            assert "content_warnings" in result
            assert "chapter_timestamps" in result

    @patch('services.accuracy_service_chain_prompting.genai.Client')
    def test_handles_empty_transcript(self, mock_client_class, service):
        """Should handle empty transcript gracefully"""
        mock_client = Mock()
        mock_client_class.return_value = mock_client

        mock_responses = [
            Mock(text='{"quotable_moments": []}'),
            Mock(text='{"reel_suggestions": []}'),
            Mock(text='{"content_warnings": []}'),
            Mock(text='{"chapter_titles": []}'),
        ]
        mock_client.models.generate_content.side_effect = mock_responses

        service.client = mock_client
        result = service.generate_accuracy_critical_content("", language="en")

        # Should return valid structure even for empty input
        assert "quotable_moments" in result
        assert "reel_suggestions" in result
        assert "content_warnings" in result
        assert "chapter_timestamps" in result


class TestModelConfiguration:
    """Test that model settings match HighAccuracyContentService"""

    @pytest.fixture
    def service(self):
        return ChainPromptingAccuracyService(api_key="test_api_key")

    @patch('services.accuracy_service_chain_prompting.genai.Client')
    def test_uses_gemini_25_pro_model(self, mock_client_class, service):
        """Should use Gemini 2.5 Pro for all calls"""
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        mock_client.models.generate_content.return_value = Mock(
            text='{"quotable_moments": []}'
        )

        service.client = mock_client
        service._generate_quotable_moments("test", "en")

        call_args = mock_client.models.generate_content.call_args
        assert call_args.kwargs['model'] == "gemini-2.5-pro", \
            "Should use gemini-2.5-pro model"

    @patch('services.accuracy_service_chain_prompting.genai.Client')
    def test_uses_high_accuracy_settings(self, mock_client_class, service):
        """Should use temperature=0.05, top_p=0.5, top_k=10 for accuracy"""
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        mock_client.models.generate_content.return_value = Mock(
            text='{"quotable_moments": []}'
        )

        service.client = mock_client
        service._generate_quotable_moments("test", "en")

        call_args = mock_client.models.generate_content.call_args
        config = call_args.kwargs['config']

        assert config.temperature == 0.05, "Temperature should be 0.05"
        assert config.top_p == 0.5, "top_p should be 0.5"
        assert config.top_k == 10, "top_k should be 10"

    @patch('services.accuracy_service_chain_prompting.genai.Client')
    def test_requests_json_response_format(self, mock_client_class, service):
        """Should request JSON response format"""
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        mock_client.models.generate_content.return_value = Mock(
            text='{"quotable_moments": []}'
        )

        service.client = mock_client
        service._generate_quotable_moments("test", "en")

        call_args = mock_client.models.generate_content.call_args
        config = call_args.kwargs['config']

        assert config.response_mime_type == "application/json", \
            "Should request JSON response format"
