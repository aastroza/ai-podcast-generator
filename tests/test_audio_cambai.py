import os
import sys
import tempfile
import pytest
from unittest.mock import patch, Mock, MagicMock

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


class TestConvertText2Audio:
    """Unit tests for convertText2Audio_cambai."""

    def test_returns_bytes(self):
        with patch("src.audio_cambai.CAMBAI_API_KEY", "test-key"), \
             patch("camb.client.CambAI") as mock_cls:
            mock_client = Mock()
            mock_client.text_to_speech.tts.return_value = iter([b"chunk1", b"chunk2"])
            mock_cls.return_value = mock_client

            # Reset the cached client
            import src.audio_cambai as mod
            with patch.object(mod, "_get_client", return_value=mock_client):
                result = mod.convertText2Audio_cambai("Hello", 147320)

            assert isinstance(result, bytes)
            assert result == b"chunk1chunk2"

    def test_uses_correct_params(self):
        mock_client = Mock()
        mock_client.text_to_speech.tts.return_value = iter([b"audio"])

        import src.audio_cambai as mod
        with patch.object(mod, "_get_client", return_value=mock_client), \
             patch.object(mod, "CAMBAI_LANGUAGE", "fr-fr"), \
             patch.object(mod, "CAMBAI_SPEECH_MODEL", "mars-pro"):
            mod.convertText2Audio_cambai("Bonjour", 99999)

        call_kwargs = mock_client.text_to_speech.tts.call_args.kwargs
        assert call_kwargs["text"] == "Bonjour"
        assert call_kwargs["voice_id"] == 99999
        assert call_kwargs["language"] == "fr-fr"
        assert call_kwargs["speech_model"] == "mars-pro"

    def test_voice_id_converted_to_int(self):
        mock_client = Mock()
        mock_client.text_to_speech.tts.return_value = iter([b"audio"])

        import src.audio_cambai as mod
        with patch.object(mod, "_get_client", return_value=mock_client):
            mod.convertText2Audio_cambai("test", "147320")  # string input

        call_kwargs = mock_client.text_to_speech.tts.call_args.kwargs
        assert call_kwargs["voice_id"] == 147320
        assert isinstance(call_kwargs["voice_id"], int)


class TestMergeAudioSegments:
    def test_merge_creates_output_file(self):
        # Create minimal valid MP3-like data using pydub
        from pydub import AudioSegment
        from pydub.generators import Sine
        import io

        # Generate two short silence segments
        seg1 = AudioSegment.silent(duration=100)
        seg2 = AudioSegment.silent(duration=100)

        buf1 = io.BytesIO()
        buf2 = io.BytesIO()
        seg1.export(buf1, format="mp3")
        seg2.export(buf2, format="mp3")

        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
            output_path = f.name

        try:
            from src.audio_cambai import merge_audio_segments
            merge_audio_segments([buf1.getvalue(), buf2.getvalue()], output_path)

            assert os.path.exists(output_path)
            assert os.path.getsize(output_path) > 0

            # Verify it's valid audio
            merged = AudioSegment.from_mp3(output_path)
            assert len(merged) >= 200  # at least 200ms
        finally:
            if os.path.exists(output_path):
                os.remove(output_path)

    def test_merge_skips_none_segments(self):
        from pydub import AudioSegment
        import io

        seg = AudioSegment.silent(duration=100)
        buf = io.BytesIO()
        seg.export(buf, format="mp3")

        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
            output_path = f.name

        try:
            from src.audio_cambai import merge_audio_segments
            merge_audio_segments([buf.getvalue(), None, buf.getvalue()], output_path)
            assert os.path.exists(output_path)
            assert os.path.getsize(output_path) > 0
        finally:
            if os.path.exists(output_path):
                os.remove(output_path)


class TestChatBotProvider:
    def test_speak_uses_cambai_when_configured(self):
        # Mock marvin.Bot before importing chat.py (marvin API changed)
        mock_bot_cls = Mock()
        with patch.dict("sys.modules", {"marvin": Mock(Bot=mock_bot_cls)}):
            # Force reimport
            if "src.chat" in sys.modules:
                del sys.modules["src.chat"]
            with patch("src.audio.convertText2Audio", return_value="ignored"), \
                 patch.dict(os.environ, {"TTS_PROVIDER": "cambai"}):
                import importlib
                import src.chat as chat_mod
                importlib.reload(chat_mod)

                with patch("src.audio_cambai.convertText2Audio_cambai", return_value=b"audio") as mock_cambai:
                    bot = chat_mod.ChatBot.__new__(chat_mod.ChatBot)
                    bot.voice = 147320
                    result = bot.speak("Hello")
                    mock_cambai.assert_called_once_with("Hello", 147320)
                    assert result == b"audio"

    def test_speak_uses_playht_when_configured(self):
        mock_bot_cls = Mock()
        mock_convert = Mock(return_value="txn-123")
        with patch.dict("sys.modules", {"marvin": Mock(Bot=mock_bot_cls)}):
            if "src.chat" in sys.modules:
                del sys.modules["src.chat"]
            with patch.dict(os.environ, {"TTS_PROVIDER": "playht"}):
                # Patch at the source module level before reload
                with patch("src.audio.convertText2Audio", mock_convert):
                    import importlib
                    import src.chat as chat_mod
                    importlib.reload(chat_mod)
                    # Also patch it on the reloaded module directly
                    chat_mod.convertText2Audio = mock_convert

                    bot = chat_mod.ChatBot.__new__(chat_mod.ChatBot)
                    bot.voice = "en-US-JennyNeural"
                    result = bot.speak("Hello")
                    mock_convert.assert_called_once_with("Hello", "en-US-JennyNeural")
                    assert result == "txn-123"


@pytest.mark.integration
class TestCambAIIntegration:
    @pytest.fixture(autouse=True)
    def skip_without_key(self):
        if not os.environ.get("CAMB_API_KEY"):
            pytest.skip("CAMB_API_KEY not set")

    def test_real_api_returns_audio_bytes(self):
        os.environ["CAMBAI_API_KEY"] = os.environ["CAMB_API_KEY"]
        from src.audio_cambai import convertText2Audio_cambai
        result = convertText2Audio_cambai("Integration test.", 147320)
        assert isinstance(result, bytes)
        assert len(result) > 0
