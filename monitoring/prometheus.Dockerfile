FROM prom/prometheus:v2.54.1
COPY prometheus.yml /etc/prometheus/prometheus.yml
COPY prometheus-alerts.yml /etc/prometheus/prometheus-alerts.yml
