import asyncio
import logging
from typing import List, Dict, Any
import json
import boto3
from botocore.exceptions import BotoCoreError, ClientError
from app.config import settings
from app.models import Product, VisionResult

logger = logging.getLogger(__name__)

class AWSClaudeService:
    def __init__(self):
        if not settings.aws_access_key_id or not settings.aws_secret_access_key:
            logger.warning("AWS credentials not configured - Claude service will be disabled")
            self.client = None
        else:
            try:
                self.client = boto3.client(
                    'bedrock-runtime',
                    aws_access_key_id=settings.aws_access_key_id,
                    aws_secret_access_key=settings.aws_secret_access_key,
                    region_name=settings.aws_region
                )
            except Exception as e:
                logger.error(f"Failed to initialize AWS client: {str(e)}")
                self.client = None

    async def generate_recommendations(
        self,
        vision_result: VisionResult,
        similar_products: List[Product],
        user_text: str = "",
        top_k: int = 5
    ) -> Dict[str, Any]:
        """
        Generate natural language recommendations using AWS Claude 3.5.
        """
        if not self.client:
            logger.warning("AWS Claude service not available - returning fallback recommendations")
            return self._fallback_recommendations(similar_products, vision_result)

        try:
            # Prepare context
            products_text = "\n".join([
                f"- {p.name} by {p.brand}: {p.description} (${p.price})"
                for p in similar_products[:top_k]
            ])

            prompt = f"""
            Based on the following image analysis and similar products, generate personalized product recommendations.

            Image Analysis:
            - Detected brands: {', '.join(vision_result.brands)}
            - Colors: {', '.join(vision_result.colors)}
            - Objects: {', '.join(vision_result.objects)}
            - Text extracted: {vision_result.text_extracted}

            User query: {user_text or "No text query provided"}

            Similar products found:
            {products_text}

            Please provide:
            1. A brief summary of what the user seems to be looking for
            2. Top 3 recommended products with explanations why they match
            3. Any additional suggestions or alternatives

            Format as JSON:
            {{
                "summary": "brief summary",
                "recommendations": [
                    {{
                        "product_id": "id",
                        "reason": "why it matches",
                        "confidence": 0.9
                    }}
                ],
                "suggestions": ["additional suggestions"]
            }}
            """

            response = self.client.invoke_model(
                modelId='anthropic.claude-3-5-sonnet-20240620-v1:0',
                body=json.dumps({
                    "anthropic_version": "bedrock-2023-05-31",
                    "max_tokens": 1000,
                    "messages": [
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ]
                })
            )

            response_body = json.loads(response['body'].read())
            result_text = response_body['content'][0]['text']

            import json
            result = json.loads(result_text)
            return result

        except (BotoCoreError, ClientError) as e:
            logger.error(f"AWS Claude API error: {str(e)}")
            return self._fallback_recommendations(similar_products, vision_result)
        except Exception as e:
            logger.error(f"Claude recommendation generation failed: {str(e)}")
            return self._fallback_recommendations(similar_products, vision_result)

    def _fallback_recommendations(self, similar_products: List[Product], vision_result: VisionResult) -> Dict[str, Any]:
        """Simple fallback recommendations."""
        return {
            "summary": f"Products matching {', '.join(vision_result.objects)}",
            "recommendations": [
                {
                    "product_id": p.id,
                    "reason": f"Similar to detected {vision_result.objects[0] if vision_result.objects else 'product'}",
                    "confidence": 0.7
                } for p in similar_products[:3]
            ],
            "suggestions": ["Consider checking product reviews", "Compare prices across retailers"]
        }

aws_claude = AWSClaudeService()