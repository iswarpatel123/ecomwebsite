#!/usr/bin/env python3
import sys
from google import genai
from google.genai import types
from pathlib import Path
from dotenv import load_dotenv

sys.path.append(str(Path(__file__).resolve().parents[1]))

"""Load .env from the project root."""
root_dir = Path(__file__).resolve().parents[1]
env_path = root_dir / ".env"
if env_path.exists():
    load_dotenv(dotenv_path=env_path)

def ask_gemini_with_search(query: str):
    # 1. Initialize the client. It automatically grabs GEMINI_API_KEY from your environment.
    client = genai.Client()

    if not query.strip():
        print("Query cannot be empty.")
        return

    print("\nSearching Google and generating answer...")
    print(f"Query: {query}")

    try:
        # 2. Call the API using the standard flash model and enable Google Search grounding
        response = client.models.generate_content(
            model="gemma-4-26b-a4b-it",
            contents=query,
            config=types.GenerateContentConfig(
                tools=[types.Tool(google_search=types.GoogleSearch())],
            ),
        )

        # 3. Print the query back out and show the AI's final answered text
        print("\n" + "="*60)
        print(f"QUERY: {query}")
        print("="*60)
        print(f"AI ANSWER:\n{response.text}")
        print("="*40)

    except Exception as e:
        print(f"\nAn error occurred: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # Accept query as a command-line argument; if none provided, prompt the user.
    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])
    else:
        query = input("Enter search query for Gemini: ")

    ask_gemini_with_search(query)
