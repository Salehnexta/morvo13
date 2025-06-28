# Monitoring & Observability

The Morvo backend exposes Prometheus metrics for both the FastAPI application and the Celery worker.  A reference Grafana dashboard JSON export will live in this folder once finalized.

## Prometheus targets
| Component | Endpoint |
|-----------|----------|
| FastAPI   | `http://<service>/metrics` |
| Celery    | Pushes task duration & count via `prometheus_client` |

Configure Prometheus to scrape both Kubernetes `Deployment` pods by matching the `prometheus.io/*` annotations included in the Helm chart.

## Grafana dashboard
1. Import `grafana-dashboard.json` (to be added).
2. Set the Prometheus data source.

Metrics visualized:
* HTTP request rate / latency (FastAPI)
* Task duration histogram (Celery)
* Task failure rate
* CPU / memory (K8s Node & Pod)

> TODO: Add alerting rules for high latency and failed tasks. 