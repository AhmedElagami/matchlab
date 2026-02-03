# Tester B MCP Usage Inventory

## Available MCPs/Tools
- Playwright MCP: used for UI automation, screenshots, console logs, network logs
- Filesystem tools: used for artifact writing
- Bash tool: used for Docker/Compose control, DB queries via psql, pytest execution

## Unavailable MCPs (fallbacks used)
- Postgres MCP: not available
  - Fallback: docker compose exec db psql (captured outputs in artifacts/db/B/results)
- Docker/Compose MCP: not available
  - Fallback: docker compose CLI (captured in artifacts/health/B)
- Logs MCP: not available
  - Fallback: docker compose logs (captured in artifacts/health/B/logs)

## Notes
- Playwright pytest CLI run failed with Django async DB error (artifacts/ui/B/playwright_cli_results.txt)
