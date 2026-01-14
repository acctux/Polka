#!/usr/bin/env python3
from pygit2 import Repository, discover_repository, GitError
from rich.console import Console
from rich.syntax import Syntax
from rich.prompt import Prompt

console = Console()

def git_fuzzy():
    # Find Git repository
    try:
        repo_path = discover_repository(".")
        if not repo_path:
            console.print("[red]Not inside a Git repository.[/red]")
            return 1
        repo = Repository(repo_path)
    except GitError:
        console.print("[red]Not inside a Git repository.[/red]")
        return 1

    search_term = Prompt.ask("Search").strip()
    if not search_term:
        return 0

    # Collect all commits from all branches
    commit_set = set()
    matching_commits = []

    for ref_name in repo.references:
        if not ref_name.startswith("refs/heads/"):
            continue
        branch = repo.references[ref_name]
        stack = [repo[branch.target]]
        while stack:
            commit = stack.pop()
            if commit.id in commit_set:
                continue
            commit_set.add(commit.id)

            # Use None for old_tree if no parent (first commit)
            old_tree = commit.parents[0].tree if commit.parents else None
            new_tree = commit.tree

            try:
                diff = repo.diff(old_tree, new_tree)
                diff_text = diff.patch if diff else ""
            except Exception as e:
                console.print(f"[red]Error diffing commit {commit.id}: {e}[/red]")
                diff_text = ""

            if search_term.lower() in diff_text.lower() or search_term.lower() in commit.message.lower():
                message_line = commit.message.splitlines()[0].strip()
                matching_commits.append((str(commit.id)[:7], message_line, diff_text))
            
            stack.extend(commit.parents)

    if not matching_commits:
        console.print(f"[yellow]No commits found containing '{search_term}'.[/yellow]")
        return 0

    # Display matching commits for selection
    console.print("\nMatching commits:\n")
    for idx, (c_hash, msg, _) in enumerate(matching_commits, 1):
        console.print(f"[cyan]{idx}[/cyan]. [green]{c_hash}[/green] {msg}")

    while True:
        choice = Prompt.ask("\nSelect a commit by number (or 'q' to quit)")
        if choice.lower() == 'q':
            return 0
        if not choice.isdigit():
            console.print("[red]Invalid input. Enter a number.[/red]")
            continue
        idx = int(choice) - 1
        if 0 <= idx < len(matching_commits):
            _, _, diff_text = matching_commits[idx]
            syntax = Syntax(diff_text if diff_text else "[yellow]No changes in this commit.[/yellow]",
                            "diff", theme="ansi_dark", line_numbers=False)
            console.print(syntax)
            break
        else:
            console.print("[red]Number out of range.[/red]")

if __name__ == "__main__":
    git_fuzzy()
