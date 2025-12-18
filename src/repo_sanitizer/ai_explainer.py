import requests
import json

SYSTEM_PROMPT = (
    "You are a senior software engineer. "
    "Explain Git branches conservatively. "
    "Never recommend deletion unless the branch is merged "
    "and inactive. "
    "Format your response using Markdown bullet points. "
    "Highlight key details like dates or status in **bold**."
)

def explain_branch(branch_info: dict) -> str:
    """
    Generate a human-readable explanation for a stale branch using Ollama.
    """

    user_prompt = f"""
Branch name: {branch_info['branch']}
Last commit message: {branch_info['last_commit_message']}
Last commit date: {branch_info['last_commit_date']}
Commit count: {branch_info['commit_count']}
Merged: {branch_info['merged']}
Upstream status: {branch_info['upstream_status']}

Explain why this branch is considered stale.
"""

    try:
        response = requests.post(
            "http://localhost:11434/api/chat",
            json={
                "model": "llama3.2",
                "messages": [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt},
                ],
                "stream": False
            },
            timeout=30
        )
        response.raise_for_status()
        return response.json()["message"]["content"].strip()
    except Exception as e:
        return f"Error calling Ollama: {e}"


def generate_commit_message(diff: str) -> str:
    """
    Generate a conventional commit message based on the provided diff.
    """
    system_prompt = (
        "You are a helpful assistant that writes semantic git commit messages. "
        "Use the Conventional Commits format (e.g. feat: ..., fix: ..., docs: ...). "
        "Keep the subject line under 72 characters. "
        "Do not include any explanation, just the commit message."
    )
    
    user_prompt = f"Generate a commit message for the following changes:\n\n{diff[:4000]}"

    try:
        response = requests.post(
            "http://localhost:11434/api/chat",
            json={
                "model": "llama3.2",
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                "stream": False
            },
            timeout=30
        )
        response.raise_for_status()
        return response.json()["message"]["content"].strip().strip('"')
    except Exception as e:
        return f"chore: automated commit (AI failed: {e})"
