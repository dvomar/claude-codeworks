# Estimate: DMS3 Invoice Integration

**Date:** 2026-01-15
**Category:** New integration

## Task Description

Implement integration with DMS3 dealer management system for loading and managing invoices. Includes:
- REST API client for DMS3 communication
- Transformation of DMS3 invoices to internal format
- SignalR hub for frontend communication
- Configuration and DI registration

## Analysis

### Affected Files
- `Infrastructure/ExternalIs/DMS3/` - new directory
- `CashMachine5/Program.cs` - module registration
- `CashMachine5/Settings/DMS3Settings.json` - configuration
- `Common.Abstractions/Invoice/` - possible interface extension

### Scope of Changes
- **New files:** 8
- **Modified files:** 2
- **Estimated lines of code:** ~800

## Time Estimate

| Phase | Hours | Description |
|-------|-------|-------------|
| Analysis | 2 | Study DMS3 API documentation, explore existing integrations |
| Design | 1 | Design service layer, data mapping (following existing patterns) |
| Implementation | 7 | API client, service, hub, configuration |
| Testing | 2.5 | Manual testing with DMS3 test environment |
| Refinement | 1 | Code review, adjustments based on feedback |
| **Buffer** | 2.5 | Incomplete API documentation (+20%) |
| **TOTAL** | **16** | |

## Cost Estimate

| Item | Value |
|------|-------|
| Total time | 16 hours |
| Hourly rate | 650 CZK |
| **Total cost** | **10 400 CZK** |

## Key Files

1. `Infrastructure/ExternalIs/DMS3/DMS3Configuration.cs` - configuration
2. `Infrastructure/ExternalIs/DMS3/DMS3ApiClient.cs` - HTTP client
3. `Infrastructure/ExternalIs/DMS3/DMS3InvoiceService.cs` - main service
4. `Infrastructure/ExternalIs/DMS3/Models/` - DTO models
5. `SignalRApi/Hubs/InvoiceHub.cs` - hub extension

## Risks and Notes

- **Risk:** DMS3 API documentation may be outdated
- **Risk:** Test environment may not contain realistic data
- **Note:** Coordination with DMS3 team needed for access credentials
- **Note:** Consider caching to reduce API load

---
*Estimate created with Claude Code task-estimate skill*
