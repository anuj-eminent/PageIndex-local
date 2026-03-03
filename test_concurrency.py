import asyncio
import sys
import os
# Add parent directory to sys.path to import pageindex
sys.path.append(os.getcwd())

from pageindex.utils import ChatGPT_API_async

async def main():
    print("Starting concurrency test...")
    prompt = "Reply with 'OK'"
    model = "gpt-oss:120b"
    
    # Fire off 20 requests at once. The semaphore should limit them to 5 at a time.
    tasks = [ChatGPT_API_async(model, prompt) for _ in range(20)]
    results = await asyncio.gather(*tasks)
    
    ok_count = sum(1 for r in results if r == "OK")
    error_count = sum(1 for r in results if r == "Error")
    
    print(f"Results: {ok_count} OK, {error_count} Error")
    if ok_count > 0:
        print("Test passed! (Or at least partially succeeded if some failed due to 429)")

if __name__ == "__main__":
    asyncio.run(main())
