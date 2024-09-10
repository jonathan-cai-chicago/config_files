# Setup
- Run `pre-commit install` to install pre-commit hooks.
- Activate the appropriate mamba envrionment, or use the `env.yml` to install a new env.
- Run `pip install .` to install `prelude` into your environment.

# Standard practices
- Never use `print`. Create a logger object by calling `create_console_logger` from `log_utils.py` instead.
- Use pre-commit hooks to enforce good coding styles.
- Use `PascalCase` for class names, `mypackage` for package names, and `snake_case` for anything else.
- Always provide type hints and doc strings in for automatic documentations. Use LLM for assistance if needed.

# Conventions
- Use `polars` instead of `pandas` if possible.
- Use `plotly.express` for visualizations if possible.

# Doc
- To refresh documentations after changes, run `pdoc --force --html --output-dir docs src/prelude` at project root.

# Overview of Git Workflow
- `git pull` to get most up-to-date `main` branch.
- Create a feature branch, write codes and commit to the branch as you go.
- `git pull` again when ready to rebase.
- Rebase and squash with `git rebase --interactive main`; Resolve any merge conflicts.
- `git push` and open pull request. Note that since this workflow re-writes history, might need to do `git push --force origin feature_branch` if the remote `feature_branch` contains some past commits.

## Interactive rebase
- An interactive rebase operation allows you to squash your commits, combining many commits into fewer, or even one singular commit.
- First, refresh the main branch, go back to feature branch, and do `git rebase --interactive main`
- This will open an editor presenting all the commits.
- Keep `pick` for the first message, and change all subsequent messages to `s` or `squash`
- Now, save the exit. Rebase will continue, and craft the commit message for the new, squashed commit.
- Merge conflicts are possible and must be manually resolved:
    - Run `git status` to identify which files have conflicts.
    - Resolve them, run `git add` to stage these files.
    - Run `git rebase --continue` (don’t do `git commit`) to continue the rebase process.
