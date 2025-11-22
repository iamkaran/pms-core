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
    {"OCCURRENCE_7": "4"},
    {"OCCURRENCE_8": "7"},
    {"OCCURRENCE_9": "16"},
    {"OCCURRENCE_10": "7"},
    {"DURATION_1": "1734"},
    {"DURATION_2": "199473"},
    {"DURATION_3": "10295"},
    {"DURATION_4": "12430"},
    {"DURATION_5": "20345"},
    {"DURATION_6": "61"},
    {"DURATION_7": "65"},
    {"DURATION_8": "6841"},
    {"DURATION_9": "26333"},
    {"DURATION_10": "1221"},
    {"PRODUCTION_COUNT": "17875"},
    {"active_status": "11"},
    {"OCCURRENCE_1": "24"},
    {"OCCURRENCE_2": "4"},
    {"OCCURRENCE_3": "15"},
    {"OCCURRENCE_4": "16"},
    {"OCCURRENCE_5": "20"},
    {"OCCURRENCE_6": "2"},
    {"OCCURRENCE_7": "4"},
    {"OCCURRENCE_8": "7"},
    {"OCCURRENCE_9": "16"},
    {"OCCURRENCE_10": "7"},
    {"DURATION_1": "1734"},
    {"DURATION_2": "199473"},
    {"DURATION_3": "10295"},
    {"DURATION_4": "12430"},
    {"DURATION_5": "20345"},
    {"DURATION_6": "61"},
    {"DURATION_7": "65"},
    {"DURATION_8": "6841"},
    {"DURATION_9": "26333"},
    {"DURATION_10": "1221"},
    {"PRODUCTION_COUNT": "17875"},
    {"active_status": "11"},
    {"timestamp": 1763829434}
  ]
}
```
