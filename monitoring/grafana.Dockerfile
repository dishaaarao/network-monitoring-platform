FROM grafana/grafana:11.2.0
USER root
COPY grafana-datasource.yml /etc/grafana/provisioning/datasources/datasource.yml
COPY grafana-dashboard-provider.yml /etc/grafana/provisioning/dashboards/provider.yml
COPY grafana-dashboard.json /etc/grafana/provisioning/dashboards/network-monitoring.json
RUN chown -R 472:0 /etc/grafana/provisioning
USER 472
