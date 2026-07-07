import os
import sys
import traceback
from dotenv import load_dotenv
from github import Github
from src.gen_readme import generate_fetch, generate_readme, gen_image

def main():
    try:
        load_dotenv()
        token = os.getenv("GH_TOKEN")
        if not token:
            raise ValueError("GH_TOKEN environment variable not set")
            
        g = Github(token)
        generate_readme(g)
        print("✨ README updated successfully! Wahooo!")
        return 0
        
    except Exception as e:

        print(f"❌ {e}", file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
        return 1

if __name__ == "__main__":
    sys.exit(main())