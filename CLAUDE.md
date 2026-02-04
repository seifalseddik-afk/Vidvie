# CLAUDE.md - AI Assistant Guidelines for Vidvie

This file provides guidance for AI assistants working with the Vidvie repository.

## Project Overview

**Repository:** Vidvie
**Status:** New project - initial setup phase
**Owner:** seifalseddik-afk

Vidvie is a newly initialized repository. This documentation will be updated as the project develops.

## Repository Structure

```
Vidvie/
├── CLAUDE.md          # AI assistant guidelines (this file)
└── .git/              # Git version control
```

*Note: Additional directories and files will be documented here as the project grows.*

## Development Workflows

### Getting Started

1. Clone the repository
2. Check the current branch: `git branch`
3. Create feature branches following the naming convention below

### Branch Naming Convention

- Feature branches: `feature/<description>`
- Bug fixes: `fix/<description>`
- Documentation: `docs/<description>`
- Claude AI branches: `claude/<description>-<session-id>`

### Commit Guidelines

- Use clear, descriptive commit messages
- Start with a verb in imperative mood (Add, Fix, Update, Remove, Refactor)
- Keep the first line under 72 characters
- Reference issues when applicable

Example:
```
Add user authentication module

- Implement JWT token generation
- Add password hashing with bcrypt
- Create login/logout endpoints

Closes #123
```

### Pull Request Process

1. Create a feature branch from the main branch
2. Make your changes with clear commits
3. Push the branch and create a PR
4. Ensure all checks pass
5. Request review and address feedback
6. Merge after approval

## Code Conventions

### General Principles

- Write clean, readable code with meaningful names
- Follow the DRY (Don't Repeat Yourself) principle
- Keep functions focused and small
- Add comments only for complex logic, not obvious code
- Handle errors appropriately

### File Organization

- Group related files in logical directories
- Use consistent naming conventions
- Keep configuration files in the root or a dedicated config directory

## AI Assistant Guidelines

### When Working on This Repository

1. **Read before modifying** - Always read existing files before making changes
2. **Understand context** - Explore the codebase structure before implementing features
3. **Minimal changes** - Make only the changes necessary for the task
4. **No over-engineering** - Avoid adding unnecessary complexity or features
5. **Test your changes** - Run tests if available before committing

### Prohibited Actions

- Do not push to main/master without explicit permission
- Do not force push unless specifically requested
- Do not commit sensitive data (API keys, passwords, credentials)
- Do not skip pre-commit hooks without explicit permission

### Best Practices

- Use the TodoWrite tool to track multi-step tasks
- Commit frequently with clear messages
- Document significant architectural decisions
- Ask for clarification when requirements are unclear

## Testing

*Testing frameworks and commands will be documented here as they are set up.*

## Build & Deployment

*Build and deployment instructions will be documented here as the project develops.*

## Dependencies

*Project dependencies will be listed here as they are added.*

## Environment Setup

*Environment variables and configuration requirements will be documented here.*

## Useful Commands

```bash
# Git operations
git status                    # Check current state
git log --oneline -10         # View recent commits
git diff                      # View unstaged changes

# Branch management
git checkout -b <branch>      # Create and switch to new branch
git push -u origin <branch>   # Push and track new branch
```

## Additional Resources

*Links to relevant documentation, wikis, or external resources will be added here.*

---

*This CLAUDE.md file was created to provide guidance for AI assistants. It should be updated as the project evolves to reflect the current state of the codebase, conventions, and workflows.*
