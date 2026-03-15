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
| `architecture` | Tech stack detection, convention extraction, backend/frontend pattern analysis | productivity |
| `implementation` | Requirements clarification, spec writing, task planning, guided implementation | productivity |
| `database` | Schema, query, and migration review for performance, security, and correctness | security |
| `dev-workflow` | Git branching, task loading, commit preparation, live testing, estimation | devops |
| `frontend-design` | Distinctive, production-grade UI components with high design quality | utilities |

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
