# 📦 PMS Core – Description

PMS Core is the central processing service of the PMS ecosystem, responsible for advanced production logic and KPI computation alongside ThingsBoard. It ingests raw machine telemetry, links it to job cards and assets, performs calculations such as OEE, efficiency, and quality, and writes the results back to ThingsBoard for visualization and monitoring.

Running as an independent FastAPI service on the same infrastructure as ThingsBoard, PMS Core centralizes all business logic for production monitoring: job status evaluation, baselining, good/bad quantity handling, and real-time KPI updates. This keeps dashboards simple while allowing the compute layer to evolve and support increasingly complex rules and workflows.

## Key capabilities:

- Ingests and normalizes telemetry from devices and gateways

- Resolves related assets and active job cards from ThingsBoard

- Computes OEE and other KPIs using live telemetry plus stored baselines

- Supports both sensor-based and manually entered bad quantity counts

- Updates job card attributes and pushes computed KPIs back into ThingsBoard

- Encapsulates PMS business rules in a single, testable, extensible microservice

## Data Schema

**Status**: Fixed / Immutable

The ingestion API expects data in the following format. This schema is critical for the `flatten_dict` logic in `routers/ingest.py`.

### Structure

- **Root Object**: Dictionary
- **Key**: The Machine Name (e.g., `MACHINE-1`). There should be exactly one key.
- **Value**: A **List** of dictionaries.
- **List Items**: Each dictionary in the list contains exactly **one** key-value pair (e.g., a metric or timestamp).

### Example Payload

```json
{
  "MACHINE-1": [
    {"OCCURRENCE-7": "4"},
    {"OCCURRENCE-8": "7"},
    {"OCCURRENCE-9": "16"},
    {"OCCURRENCE-10": "7"},
    {"DURATION-1": "1734"},
    {"DURATION-2": "199473"},
    {"DURATION-3": "10295"},
    {"DURATION-4": "12430"},
    {"DURATION-5": "20345"},
    {"DURATION-6": "61"},
    {"DURATION-7": "65"},
    {"DURATION-8": "6841"},
    {"DURATION-9": "26333"},
    {"DURATION-10": "1221"},
    {"PRODUCTION-COUNT": "17875"},
    {"active_status": "11"},
    {"OCCURRENCE-1": "24"},
    {"OCCURRENCE-2": "4"},
    {"OCCURRENCE-3": "15"},
    {"OCCURRENCE-4": "16"},
    {"OCCURRENCE-5": "20"},
    {"OCCURRENCE-6": "2"},
    {"OCCURRENCE-7": "4"},
    {"OCCURRENCE-8": "7"},
    {"OCCURRENCE-9": "16"},
    {"OCCURRENCE-10": "7"},
    {"DURATION-1": "1734"},
    {"DURATION-2": "199473"},
    {"DURATION-3": "10295"},
    {"DURATION-4": "12430"},
    {"DURATION-5": "20345"},
    {"DURATION-6": "61"},
    {"DURATION-7": "65"},
    {"DURATION-8": "6841"},
    {"DURATION-9": "26333"},
    {"DURATION-10": "1221"},
    {"PRODUCTION-COUNT": "17875"},
    {"active_status": "11"},
    {"timestamp": 1763829434}
  ]
}
```
