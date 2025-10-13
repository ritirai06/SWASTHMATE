import httpx
import asyncio

OCRSPACE_API_KEY = "YOUR_OCRSPACE_API_KEY"  # <-- replace with your actual key


async def extract_text_async(image_path, api_key=OCRSPACE_API_KEY):
    """Async OCR extraction using OCR.Space API"""
    with open(image_path, "rb") as image_file:
        files = {"filename": (image_path, image_file, "image/jpeg")}
        data = {"apikey": api_key, "language": "eng"}

        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.ocr.space/parse/image",
                files=files,
                data=data
            )

    result = response.json()

    if result.get("IsErroredOnProcessing"):
        print("OCR.Space Error:", result.get("ErrorMessage", "Unknown error"))
        return ""

    parsed_results = result.get("ParsedResults")
    if parsed_results and len(parsed_results) > 0:
        return parsed_results[0].get("ParsedText", "").strip()

    return ""


def extract_text(image_path, api_key=OCRSPACE_API_KEY):
    """Sync wrapper for Flask/Django apps (runs the async function)"""
    return asyncio.run(extract_text_async(image_path, api_key))
