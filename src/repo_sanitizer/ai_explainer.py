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
        # Try using a faster model if available, otherwise fallback or let user configure
        # For now, we stick to llama3.2 but limit context to speed it up
        response = requests.post(
            "http://localhost:11434/api/chat",
            json={
                "model": "llama3.2",
                "messages": [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt},
                ],
                "stream": False,
                "options": {
                    "num_ctx": 2048,  # Limit context window for speed
                    "temperature": 0.2, # Lower temp for faster deterministic output
                    "num_predict": 150 # Limit output tokens
                }
            },
            timeout=120
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
                "stream": False,
                "options": {
                    "num_ctx": 2048,
                    "temperature": 0.2,
                    "num_predict": 50 # Commit messages are short
                }
            },
            timeout=120
        )
        response.raise_for_status()
        return response.json()["message"]["content"].strip().strip('"')
    except Exception as e:
        return f"chore: automated commit (AI failed: {e})"


def generate_code_review(diff: str) -> str:
    """
    Generate a code review for the provided diff.
    """
    system_prompt = (
        "You are a senior code reviewer. "
        "Review the following code changes. "
        "Identify potential bugs, security issues, and improvements. "
        "Be constructive and concise. "
        "Format your response using Markdown."
    )
    
    user_prompt = f"Review the following changes:\n\n{diff[:4000]}"

    try:
        response = requests.post(
            "http://localhost:11434/api/chat",
            json={
                "model": "llama3.2",
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                "stream": False,
                "options": {
                    "num_ctx": 2048,
                    "temperature": 0.2,
                    "num_predict": 300
                }
            },
            timeout=120
        )
        response.raise_for_status()
        return response.json()["message"]["content"].strip()
    except Exception as e:
        return f"Error generating review: {e}"


def summarize_history(commits: list) -> str:
    """
    Summarize the recent commit history.
    """
    system_prompt = (
        "You are a project manager. "
        "Summarize the recent development activity based on the commit history. "
        "Highlight key achievements and changes. "
        "Format your response using Markdown."
    )
    
    history_text = "\n".join([f"- {c['hash']} ({c['author']}): {c['message']}" for c in commits])
    user_prompt = f"Summarize the following commit history:\n\n{history_text}"

    try:
        response = requests.post(
            "http://localhost:11434/api/chat",
            json={
                "model": "llama3.2",
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                "stream": False,
                "options": {
                    "num_ctx": 2048,
                    "temperature": 0.2,
                    "num_predict": 200
                }
            },
            timeout=120
        )
        response.raise_for_status()
        return response.json()["message"]["content"].strip()
    except Exception as e:
        return f"Error summarizing history: {e}"
