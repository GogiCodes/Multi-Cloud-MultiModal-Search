import asyncio
import logging
from typing import Optional
from app.config import settings
from app.models import VisionResult
import base64
import io
from PIL import Image

logger = logging.getLogger(__name__)

class AzureVisionService:
    def __init__(self):
        if not settings.azure_openai_key or not settings.azure_openai_endpoint:
            logger.warning("Azure OpenAI credentials not configured - vision service will be disabled")
            self.client = None
        else:
            try:
                from openai import AsyncAzureOpenAI
                self.client = AsyncAzureOpenAI(
                    api_key=settings.azure_openai_key,
                    api_version="2024-02-01",
                    azure_endpoint=settings.azure_openai_endpoint
                )
            except Exception as e:
                logger.error(f"Failed to initialize Azure OpenAI client: {str(e)}")
                self.client = None

    async def analyze_image(self, image_bytes: bytes) -> Optional[VisionResult]:
        """
        Analyze image using Azure GPT-4o Vision to extract product details.
        """
        if not self.client:
            logger.warning("Azure Vision service not available - returning mock result")
            return VisionResult(
                brands=["unknown"],
                colors=["unknown"],
                objects=["product"],
                text_extracted="",
                confidence=0.5
            )

        try:
            # Convert image to base64
            image = Image.open(io.BytesIO(image_bytes))
            # Resize if too large
            max_size = (1024, 1024)
            image.thumbnail(max_size, Image.Resampling.LANCZOS)

            # Convert to base64
            buffer = io.BytesIO()
            image.save(buffer, format='JPEG')
            image_b64 = base64.b64encode(buffer.getvalue()).decode()

            prompt = """
            Analyze this product image and provide detailed information in JSON format:
            {
                "brands": ["list of detected brand names"],
                "colors": ["list of main colors"],
                "objects": ["list of objects/products detected"],
                "text_extracted": "any text visible in the image",
                "confidence": 0.95
            }
            Be specific about brands, colors, and objects. If no brand is detectable, use ["unknown"].
            """

            response = await self.client.chat.completions.create(
                model=settings.azure_openai_deployment,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {"url": f"data:image/jpeg;base64,{image_b64}"}
                            }
                        ]
                    }
                ],
                max_tokens=500,
                temperature=0.1
            )

            result_text = response.choices[0].message.content
            logger.info(f"Azure Vision result: {result_text}")

            # Parse JSON response
            import json
            try:
                result_data = json.loads(result_text)
                return VisionResult(**result_data)
            except json.JSONDecodeError:
                logger.error("Failed to parse Azure Vision JSON response")
                return None

        except Exception as e:
            logger.error(f"Azure Vision analysis failed: {str(e)}")
            return None

azure_vision = AzureVisionService()