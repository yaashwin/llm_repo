import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import download_youtube_alternative

async def test():
    # Test with a short video
    test_url = "https://youtu.be/ocQi3dKo6BU?si=U58qUgl39iKNWsiw"  # "Me at the zoo" - first YouTube video
    
    try:
        print("Testing YouTube download...")
        result = await download_youtube_alternative(test_url)
        print(f"Success! Downloaded to: {result}")
        
        # Check file size
        size = os.path.getsize(result) / (1024 * 1024)  # Convert to MB
        print(f"File size: {size:.2f} MB")
        
        # Clean up
        if os.path.exists(result):
            os.remove(result)
            print("Test file cleaned up")
            
    except Exception as e:
        print(f"Test failed: {e}")

if __name__ == "__main__":
    asyncio.run(test())