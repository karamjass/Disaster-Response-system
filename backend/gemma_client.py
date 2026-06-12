from groq import AsyncGroq
import base64

class GemmaClient:
    def __init__(self, api_key: str):
        self.client = AsyncGroq(api_key=api_key)
        self.model = "gemma2-9b-it"

    async def generate(self, prompt, model=None, images=None):
        try:
            messages = []

            if images:
                # image support ke liye llava use karo
                image_content = []
                for img in images:
                    image_content.append({
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{img}"
                        }
                    })
                image_content.append({"type": "text", "text": prompt})
                messages.append({"role": "user", "content": image_content})
                use_model = "llava-v1.5-7b-4096-preview"  # groq pe image wala
            else:
                messages.append({"role": "user", "content": prompt})
                use_model = model or self.model

            response = await self.client.chat.completions.create(
                model=use_model,
                messages=messages,
                max_tokens=2048
            )
            return response.choices[0].message.content

        except Exception as e:
            return f"Groq Error: {str(e)}"