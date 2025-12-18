# Git-Janitor 🧹

**Git-Janitor** (aka `repo-sanitizer`) is a powerful CLI tool to keep your git repositories clean and organized. It helps you identify and delete stale branches, and now features AI-powered capabilities to explain branch context and automate commit messages.

## 🚀 Features

- **Stale Branch Detection**: Automatically finds branches that are merged or deleted from remote.
- **Interactive UI**: Beautiful terminal interface to select branches for deletion.
- **AI Branch Explainer**: Uses local AI (Ollama) to explain *why* a branch is stale before you delete it.
- **AI Auto-Commit & Push**: Generates semantic commit messages based on your changes and pushes them upstream.
- **Safety First**: Checks upstream status and merge history to prevent accidental data loss.

## 📦 Installation

1.  Clone the repository:
    ```bash
    git clone https://github.com/Aniketgawande1/Git-Janitor.git
    cd Git-Janitor
    ```

2.  Install the package:
    ```bash
    pip install .
    ```

3.  **Prerequisite for AI Features**:
    You need [Ollama](https://ollama.com/) installed and running locally with the `llama3.2` model.
    ```bash
    ollama run llama3.2
    ```

## 🛠️ Usage

The main command is `clean-repo`.

### 1. Clean Stale Branches

Scan your repository for stale branches and interactively choose which ones to delete.

```bash
clean-repo clean
```

### 2. AI-Powered Cleaning 🧠

Get a detailed explanation of *why* a branch is considered stale (e.g., last commit date, merge status) using AI.

```bash
clean-repo clean --explain
```

*Example Output:*
> **feature-login**: This branch implemented OAuth login and was merged into main. No activity in 6 months. Deletion appears safe.

### 3. AI Auto-Commit & Push 🤖

Stage all changes, generate a Conventional Commit message using AI, and push to the remote.

```bash
clean-repo push
```

*The tool will show you the generated message and ask for confirmation before pushing.*

To skip confirmation:
```bash
clean-repo push --auto
```

### 4. Undo Deletion

Accidentally deleted a branch? Restore it immediately (if it hasn't been garbage collected).

```bash
clean-repo undo <branch_name>
```

## ⚙️ Configuration

The tool uses a local Ollama instance by default (`http://localhost:11434`). Ensure Ollama is running for AI features to work.

## 📄 License

MIT
