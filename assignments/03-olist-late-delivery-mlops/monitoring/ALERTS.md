# Monitoring and alert policy

The service exposes Prometheus metrics at `/metrics` and stores every successful prediction in PostgreSQL.

Initial alert policy:

- **Availability:** alert when the API health check fails for more than 2 consecutive checks.
- **Latency:** investigate when p95 prediction latency stays above 500 ms.
- **Errors:** investigate when the request error rate exceeds 5% over a 5-minute window.
- **Prediction drift:** investigate when the recent predicted-late share differs from the validation reference (0.09723) by more than 0.05 absolute.
- **Model loading:** page immediately if the configured MLflow model alias cannot be resolved at service startup.

These are operational starting thresholds, not claims that they are universally optimal. They are intentionally kept in configuration and documentation so they can be changed without changing inference logic.
