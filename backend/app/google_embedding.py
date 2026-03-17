import asyncio
import logging
from typing import List, Optional
import google.generativeai as genai
from app.config import settings
import numpy as np
import clip
import torch
from PIL import Image
import io

logger = logging.getLogger(__name__)

class GoogleEmbeddingService:
    def __init__(self):
        if not settings.google_ai_key:
            logger.warning("Google AI key not configured - using CLIP fallback")
            self.model = None
            self.embedding_model = None
        else:
            try:
                genai.configure(api_key=settings.google_ai_key)
                self.model = genai.GenerativeModel('gemini-pro-vision')
                self.embedding_model = genai.GenerativeModel('embedding-001')
            except Exception as e:
                logger.error(f"Failed to initialize Google AI: {str(e)}")
                self.model = None
                self.embedding_model = None

        # CLIP fallback
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.clip_model, self.clip_preprocess = None, None

    async def _load_clip(self):
        if self.clip_model is None:
            self.clip_model, self.clip_preprocess = clip.load("ViT-B/32", device=self.device)

    async def generate_text_embedding(self, text: str) -> Optional[List[float]]:
        """
        Generate embedding for text using Google Gemini.
        """
        if not self.embedding_model:
            logger.warning("Google AI not available - using CLIP fallback")
            return await self._clip_text_embedding(text)

        try:
            result = genai.embed_content(
                model="models/embedding-001",
                content=text,
                task_type="retrieval_document"
            )
            return result['embedding']
        except Exception as e:
            logger.warning(f"Google embedding failed for text: {str(e)}")
            return await self._clip_text_embedding(text)

    async def generate_image_embedding(self, image_bytes: bytes) -> Optional[List[float]]:
        """
        Generate embedding for image using Google Gemini or CLIP fallback.
        """
        if not self.model:
            logger.warning("Google AI not available - using CLIP fallback")
            return await self._clip_image_embedding(image_bytes)

        try:
            image = Image.open(io.BytesIO(image_bytes))
            # Use Gemini for image embedding
            response = self.model.generate_content([
                "Generate a detailed description of this product for embedding purposes.",
                image
            ])
            description = response.text
            return await self.generate_text_embedding(description)
        except Exception as e:
            logger.warning(f"Google image embedding failed: {str(e)}")
            return await self._clip_image_embedding(image_bytes)

    async def _clip_text_embedding(self, text: str) -> Optional[List[float]]:
        """Fallback CLIP text embedding."""
        try:
            await self._load_clip()
            text_tokens = clip.tokenize([text]).to(self.device)
            with torch.no_grad():
                text_features = self.clip_model.encode_text(text_tokens)
                return text_features.cpu().numpy().flatten().tolist()
        except Exception as e:
            logger.error(f"CLIP text embedding failed: {str(e)}")
            return None

    async def _clip_image_embedding(self, image_bytes: bytes) -> Optional[List[float]]:
        """Fallback CLIP image embedding."""
        try:
            await self._load_clip()
            image = Image.open(io.BytesIO(image_bytes))
            image_input = self.clip_preprocess(image).unsqueeze(0).to(self.device)
            with torch.no_grad():
                image_features = self.clip_model.encode_image(image_input)
                return image_features.cpu().numpy().flatten().tolist()
        except Exception as e:
            logger.error(f"CLIP image embedding failed: {str(e)}")
            return None

google_embedding = GoogleEmbeddingService()