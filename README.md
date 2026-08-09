# Claude Codeworks

Curated collection of Claude Code plugins for software development — code review, architecture analysis, implementation workflows, and dev tooling.

## Installation

### Add marketplace to Claude Code

```
/plugin marketplace add dvomar/claude-codeworks
```

### Browse available plugins

```
/plugin
```

Go to the **Discover** tab to browse available plugins.

### Install a specific plugin

```
/plugin install <plugin-name>@codeworks
```

## Available Plugins

| Plugin | Description | Category |
|--------|-------------|----------|
| `code-review` | 3-pass code reviews, optimization analysis, refactoring cleanup, GitLab MR integration | productivity |
| `architecture` | Tech stack detection, convention extraction, backend/frontend pattern analysis, two-phase project mapping into an Obsidian vault | productivity |
| `implementation` | Requirements clarification, spec writing, task planning, guided implementation | productivity |
| `auto-memory` | Session memory capture, knowledge doc upkeep, end-of-session wrap-up | productivity |
| `database` | Schema, query, and migration review for performance, security, and correctness | security |
| `security` | Language- and stack-agnostic security audits with prioritized findings | security |
| `dev-workflow` | Git branching and worktrees, commit preparation, task loading, estimation, integration proposals, HTML-to-PDF | devops |
| `frontend-design` | UI/UX designed from an existing codebase, optimization via competing proposals, distinctive production-grade components | utilities |

## Team Setup

Add to `.claude/settings.json` in your project:

```json
{
  "extraKnownMarketplaces": {
    "codeworks": {
      "source": {
        "source": "github",
        "repo": "dvomar/claude-codeworks"
      }
    }
  }
}
```

## Contributing

Want to add a plugin? Open a Pull Request with a new folder in `plugins/`.
Each plugin must contain `.claude-plugin/plugin.json` and `README.md`.

## License

MIT
