# Tester A MCP Usage Inventory

## Available MCPs/Tools
- Playwright MCP: used for UI automation, screenshots, downloads
- Filesystem tools: used for artifact writing
- Bash tool: used for Docker/Compose control, DB queries, curl, pytest attempt

## Unavailable MCPs (fallbacks used)
- Postgres MCP: not available
  - Fallback: docker compose exec db psql (captured outputs in artifacts/db/A/results)
- Docker/Compose MCP: not available
  - Fallback: docker compose CLI (captured in artifacts/health/A)
- Logs MCP: not available
  - Fallback: docker compose logs (captured in artifacts/health/A/logs)

## Notes
- Playwright console/network MCPs returned no entries; event stream errors recorded in artifacts/ui/A/console_logs/page_errors_match_run_1.txt
- Playwright pytest CLI could not run: pytest missing (artifacts/ui/A/playwright_cli_results.txt)
