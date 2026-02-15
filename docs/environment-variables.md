# Environment Variables

This project supports two naming patterns for each secret:

1. Standard name (recommended for local `.env`)
2. Prefixed name (`AC_...`) for namespaced environments

## Supported Variables

- `OPENAI_API_KEY` or `AC_OPENAI_API_KEY`
- `GEMINI_API_KEY` or `AC_GEMINI_API_KEY`
- `PERPLEXITY_SESSION_TOKEN` or `AC_PERPLEXITY_SESSION_TOKEN`
- `PERPLEXITY_CSRF_TOKEN` or `AC_PERPLEXITY_CSRF_TOKEN`

## Notes

- These values are used for subscription-web/session based access in this project.
- Do not commit real values to Git.
