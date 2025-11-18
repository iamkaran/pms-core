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
