# Reporting Guide

The reporting subsystem converts raw execution data into consumable artefacts for engineers, managers,
and external stakeholders.

## Report Types

| Format | Command | Use Case |
|--------|---------|---------|
| HTML | `python scripts/generate_report.py --format html --output data/reports/html/report.html` | Executive summaries with charts |
| Markdown | `python scripts/generate_report.py --format markdown` | Lightweight sharing over chat or wikis |
| JSON | `python scripts/generate_report.py --format json` | Machine-readable ingestion by downstream tools |
| CSV | `python scripts/generate_report.py --format csv` | Spreadsheet analysis |
| Crash bundle | `python scripts/generate_report.py --format crash --crash-id <id>` | Deep crash investigations |
| Coverage | `python scripts/generate_report.py --format coverage` | Coverage trend monitoring |

## Templates

Templates reside in `src/reporting/templates/`:

- `summary_template.html` – Overview of campaign scope, key metrics, and status.
- `crash_template.html` – Detailed crash table with exploitability, stack traces, reproduction steps.
- `coverage_template.html` – Coverage metrics, heatmaps, and diff to previous campaign.

Customise templates to match branding or add metadata by editing these files and re-running report
generation.

## Data Sources

Reports pull from:

- SQLite database (`src/storage/database.py`) for execution metadata.
- Crash storage for artefact links.
- Coverage tracker output for per-target coverage.
- Monitoring subsystem for host statistics during the campaign.

## Scheduling Reports

Use the reporting scheduler:

```bash
python scripts/generate_report.py --schedule daily --format html --output data/reports/html/daily.html
```

or configure cron/systemd timers that invoke the script with desired arguments.

## Distribution

- Upload generated reports to shared storage (S3, SMB, SharePoint) using custom scripts.
- Integrate with notifiers by configuring `notification_config.yaml` to push report URLs to Slack/email.
- Export JSON/CSV into BI tools for trend analysis.

## Verification

Validate report generation after template or schema changes:

```bash
pytest tests/unit/test_reporting.py
pytest tests/integration/test_full_campaign.py -k report
```

## Troubleshooting

- Missing data – check `logs/reporting.log` (or general `logs/execution.log`) for query errors.
- Template errors – ensure Jinja2 variables exist; run the unit tests to catch regressions.
- Permission issues – confirm the target directory under `data/reports/` is writable.

For a holistic view of metrics and KPIs, pair reports with the dashboards described in
[`MONITORING.md`](MONITORING.md) and the notebooks under `notebooks/05_metrics_dashboard.ipynb`.
