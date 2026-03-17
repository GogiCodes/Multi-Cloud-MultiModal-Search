import pytest
from unittest.mock import AsyncMock, patch
from app.google_embedding import GoogleEmbeddingService

@pytest.mark.asyncio
async def test_google_embedding_service():
    """Test Google embedding service with mocked responses."""
    service = GoogleEmbeddingService()

    # Mock the Google AI response
    mock_embedding = [0.1, 0.2, 0.3, 0.4, 0.5] * 100  # 500 dimensions

    with patch('google.generativeai.embed_content') as mock_embed:
        mock_embed.return_value = {'embedding': mock_embedding}

        result = await service.generate_text_embedding("test text")

        assert result == mock_embedding
        mock_embed.assert_called_once()

@pytest.mark.asyncio
async def test_embedding_fallback():
    """Test CLIP fallback when Google API fails."""
    service = GoogleEmbeddingService()

    with patch('google.generativeai.embed_content', side_effect=Exception("API Error")), \
         patch.object(service, '_clip_text_embedding') as mock_clip:

        mock_clip.return_value = [0.1, 0.2, 0.3]

        result = await service.generate_text_embedding("test text")

        assert result == [0.1, 0.2, 0.3]
        mock_clip.assert_called_once_with("test text")