# Git Worktrees: Complete Guide for Parallel Development

## What are Git Worktrees?

Git worktrees allow you to have multiple working directories for the same repository, each with a different branch checked out. Instead of switching branches in one directory (which requires stashing changes), you can work on multiple branches simultaneously in separate folders.

**Think of it like this**: Instead of having one desk where you constantly shuffle papers, you have multiple desks - each dedicated to a different project.

## Key Benefits

- **No context switching**: Work on multiple features/branches simultaneously
- **Resource efficient**: Shares Git objects between worktrees (no duplicate .git folders)
- **Perfect for AI coding**: Run multiple Claude Code instances on different branches
- **Safe parallel development**: No risk of conflicts between different work streams

## Basic Git Worktree Commands

### Creating Worktrees
```bash
# Create worktree for existing branch
git worktree add ../feature-branch feature-branch

# Create worktree with new branch
git worktree add ../new-feature -b new-feature

# Create from specific commit/branch
git worktree add ../hotfix main -b hotfix
```

### Managing Worktrees
```bash
# List all worktrees
git worktree list

# Remove a worktree
git worktree remove ../feature-branch

# Move a worktree
git worktree move ../old-path ../new-path

# Prune deleted worktrees
git worktree prune
```

## Using Git Worktrees with Claude Code

### Basic Workflow

1. **Create a worktree for your feature**:
   ```bash
   cd /home/tallb/projects/map-doc-automation
   git worktree add ../map-doc-feature-x -b feature-x
   ```

2. **Open Claude Code in the new worktree**:
   ```bash
   cd ../map-doc-feature-x
   claude
   ```

3. **Work on your feature in isolation** - Claude Code operates in this separate directory with its own branch

4. **When done, merge back**:
   ```bash
   cd /home/tallb/projects/map-doc-automation  # back to main repo
   git merge feature-x
   git worktree remove ../map-doc-feature-x
   ```

### Advanced: Custom Worktree Management

Create a bash function for easier worktree management (add to your `~/.bashrc`):

```bash
# Worktree manager function
w() {
    local repo_name="map-doc-automation"
    local worktree_base="$HOME/projects/worktrees"

    if [ $# -eq 0 ]; then
        echo "Usage: w <branch-name> [command]"
        echo "Example: w feature-x claude"
        return 1
    fi

    local branch_name="$1"
    local worktree_path="$worktree_base/${repo_name}-${branch_name}"

    # If no command provided, just cd to worktree
    if [ $# -eq 1 ]; then
        if [ -d "$worktree_path" ]; then
            cd "$worktree_path"
        else
            echo "Worktree doesn't exist. Create it first."
        fi
        return
    fi

    shift  # Remove first argument
    local command="$@"

    # Special commands
    case "$command" in
        "create")
            mkdir -p "$worktree_base"
            cd "$HOME/projects/map-doc-automation"
            git worktree add "$worktree_path" -b "$branch_name"
            echo "Created worktree: $worktree_path"
            ;;
        "claude")
            if [ -d "$worktree_path" ]; then
                cd "$worktree_path"
                claude
            else
                echo "Worktree doesn't exist. Run: w $branch_name create"
            fi
            ;;
        "remove")
            if [ -d "$worktree_path" ]; then
                git worktree remove "$worktree_path"
                echo "Removed worktree: $worktree_path"
            fi
            ;;
        *)
            # Run any command in the worktree context
            if [ -d "$worktree_path" ]; then
                (cd "$worktree_path" && eval "$command")
            else
                echo "Worktree doesn't exist. Run: w $branch_name create"
            fi
            ;;
    esac
}
```

### Usage Examples with the Function

```bash
# Create a new worktree and branch
w phase3-rag create

# Open Claude Code in that worktree
w phase3-rag claude

# Run git status in the worktree
w phase3-rag git status

# Run your Python script in the worktree
w phase3-rag python main.py

# Remove the worktree when done
w phase3-rag remove
```

## Practical Workflow for Your Podcast Project

Let's say you want to work on Phase 3 (RAG implementation) while keeping your current Phase 2 work intact:

### Step 1: Create Phase 3 Worktree
```bash
cd /home/tallb/projects/map-doc-automation
git worktree add ../map-doc-phase3 -b phase3-rag-implementation
```

### Step 2: Start Claude Code in Phase 3
```bash
cd ../map-doc-phase3
claude
```

Now you have:
- Original project at `/home/tallb/projects/map-doc-automation` (main branch)
- Phase 3 work at `/home/tallb/projects/map-doc-phase3` (phase3-rag-implementation branch)
- Both can run Claude Code simultaneously!

### Step 3: Parallel Development
You can now:
- Keep your original Claude Code session running for maintenance/bug fixes
- Use the new Claude Code session for Phase 3 development
- Test both versions independently
- Switch between them without losing context

### Step 4: Integration
When Phase 3 is ready:
```bash
cd /home/tallb/projects/map-doc-automation
git merge phase3-rag-implementation
git worktree remove ../map-doc-phase3
git branch -d phase3-rag-implementation  # Clean up branch if desired
```

## Best Practices

1. **Organize worktrees**: Use a consistent directory structure like `~/projects/worktrees/`
2. **Name branches clearly**: `feature-x`, `hotfix-y`, `experiment-z`
3. **Limit active worktrees**: Keep 2-3 active to avoid confusion
4. **Clean up regularly**: Remove worktrees when features are merged
5. **Use descriptive names**: Include your username or issue numbers in branch names

## Troubleshooting

**Problem**: "fatal: 'branch-name' is already checked out"
**Solution**: You can't check out the same branch in multiple worktrees

**Problem**: Disk space issues
**Solution**: Worktrees share Git objects, but working files are duplicated. Clean up unused worktrees.

**Problem**: Confused about which worktree you're in
**Solution**: Use `git worktree list` and check your current directory

## Modern 2025 Workflows with AI Development

### Parallel AI Coding
Git worktrees have become essential for modern AI-assisted development workflows:

- **Multiple AI agents**: Run different Claude Code instances on separate branches
- **Comparative development**: Generate multiple implementations of the same feature
- **Risk mitigation**: If one AI session gets confused, others continue working
- **Design exploration**: Explore different architectural approaches simultaneously

### Integration with Claude Code
The combination of git worktrees and Claude Code enables:
- **Isolated conversations**: Each Claude session maintains separate context
- **Branch-specific knowledge**: Claude learns about branch-specific changes
- **Parallel feature development**: Work on multiple features without conflicts
- **Experimental branches**: Try risky changes without affecting main development

This setup will greatly improve your development workflow, especially when working with Claude Code on complex features like your podcast automation system!