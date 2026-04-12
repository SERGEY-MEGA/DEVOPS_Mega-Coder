from __future__ import annotations

import json
from datetime import datetime
from html import escape
from pathlib import Path


ROOT = Path(__file__).resolve().parent
EVIDENCE = ROOT / "evidence"
HTML_DIR = ROOT / "html"
HTML_DIR.mkdir(parents=True, exist_ok=True)


STYLE = """
<style>
  :root {
    --bg: #0b1020;
    --panel: #121a2d;
    --panel-2: #0f172a;
    --text: #e5eefb;
    --muted: #9fb1d0;
    --accent: #63b3ff;
    --ok: #32d296;
    --warn: #ffb454;
    --border: #26324d;
  }
  * { box-sizing: border-box; }
  body {
    margin: 0;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    background: linear-gradient(180deg, #09111f 0%, #101b31 100%);
    color: var(--text);
  }
  main {
    width: 1280px;
    margin: 0 auto;
    padding: 36px 42px 48px;
  }
  h1, h2, h3 { margin: 0 0 16px; }
  p { margin: 0 0 14px; color: var(--muted); line-height: 1.5; }
  .hero {
    padding: 24px 28px;
    border: 1px solid var(--border);
    border-radius: 18px;
    background: rgba(18, 26, 45, 0.92);
    margin-bottom: 22px;
  }
  .grid {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 16px;
    margin-bottom: 20px;
  }
  .cards-4 {
    display: grid;
    grid-template-columns: repeat(4, minmax(0, 1fr));
    gap: 14px;
    margin-bottom: 20px;
  }
  .card, .panel {
    border: 1px solid var(--border);
    border-radius: 16px;
    background: rgba(18, 26, 45, 0.94);
    padding: 18px 20px;
  }
  .metric-label {
    color: var(--muted);
    font-size: 14px;
    margin-bottom: 8px;
  }
  .metric-value {
    font-size: 34px;
    font-weight: 700;
    color: var(--accent);
  }
  .pill {
    display: inline-block;
    padding: 4px 10px;
    border-radius: 999px;
    background: rgba(50, 210, 150, 0.14);
    color: var(--ok);
    border: 1px solid rgba(50, 210, 150, 0.28);
    font-size: 13px;
    margin-right: 8px;
  }
  .small { font-size: 13px; color: var(--muted); }
  pre {
    margin: 0;
    padding: 16px 18px;
    background: var(--panel-2);
    border: 1px solid var(--border);
    border-radius: 14px;
    overflow: hidden;
    white-space: pre-wrap;
    word-break: break-word;
    font-size: 15px;
    line-height: 1.45;
  }
  table {
    width: 100%;
    border-collapse: collapse;
    font-size: 15px;
  }
  th, td {
    text-align: left;
    padding: 10px 12px;
    border-bottom: 1px solid var(--border);
  }
  th { color: var(--muted); font-weight: 600; }
  tr:last-child td { border-bottom: none; }
  code {
    font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
    font-size: 14px;
  }
</style>
"""


def read_text(name: str) -> str:
    return (EVIDENCE / name).read_text(encoding="utf-8").strip()


def read_json(name: str) -> dict:
    return json.loads(read_text(name))


def prom_scalar(name: str) -> float:
    data = read_json(name)
    return float(data["data"]["result"][0]["value"][1])


def render_page(title: str, body: str, filename: str) -> None:
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    html = f"""<!DOCTYPE html>
<html lang="ru">
<head>
  <meta charset="utf-8">
  <title>{escape(title)}</title>
  {STYLE}
</head>
<body>
  <main>
    <section class="hero">
      <h1>{escape(title)}</h1>
      <p>Живые данные стенда MEGA CODER, зафиксированные {escape(ts)}.</p>
    </section>
    {body}
  </main>
</body>
</html>
"""
    (HTML_DIR / filename).write_text(html, encoding="utf-8")


def build_backend_page() -> None:
    api_info = read_text("api-info.json")
    frontend_head = read_text("frontend-head.txt")
    body = f"""
    <section class="grid">
      <div class="panel">
        <h2>Backend API</h2>
        <p>Ответ endpoint <code>/api/info</code> с живого сервиса.</p>
        <pre>{escape(api_info)}</pre>
      </div>
      <div class="panel">
        <h2>HTTP-проверка frontend</h2>
        <p>Проверка NodePort frontend-сервиса.</p>
        <pre>{escape(frontend_head)}</pre>
      </div>
    </section>
    """
    render_page("MEGA CODER: Frontend + Backend", body, "backend-proof.html")


def build_k8s_page() -> None:
    raw = read_text("k8s-live.txt")
    parts = [part.strip() for part in raw.split("====")]
    nodes = parts[0] if len(parts) > 0 else raw
    pods = parts[1] if len(parts) > 1 else ""
    workloads = parts[2] if len(parts) > 2 else ""
    releases = parts[3] if len(parts) > 3 else ""
    monitoring_pods = parts[4] if len(parts) > 4 else ""

    body = f"""
    <section class="panel" style="margin-bottom: 18px;">
      <h2>Статус кластера</h2>
      <p><span class="pill">k3s Ready</span><span class="pill">namespace mega-coder</span><span class="pill">monitoring stack active</span></p>
      <pre>{escape(nodes)}</pre>
    </section>
    <section class="grid">
      <div class="panel">
        <h2>Pods</h2>
        <p>Подтверждение, что приложение и monitoring работают одновременно.</p>
        <pre>{escape(pods)}</pre>
      </div>
      <div class="panel">
        <h2>Deployments / Services / ConfigMap / Secret</h2>
        <p>Срез объектов из namespace <code>mega-coder</code>.</p>
        <pre>{escape(workloads)}</pre>
      </div>
    </section>
    <section class="panel">
      <h2>Helm releases</h2>
      <p>Приложение, Loki и kube-prometheus-stack установлены через Helm.</p>
      <pre>{escape(releases)}</pre>
    </section>
    <section class="panel" style="margin-top: 18px;">
      <h2>Monitoring pods</h2>
      <p>Подтверждение, что Prometheus, Grafana, Loki, Promtail, Node Exporter и kube-state-metrics работают в namespace <code>monitoring</code>.</p>
      <pre>{escape(monitoring_pods)}</pre>
    </section>
    """
    render_page("Kubernetes: live cluster evidence", body, "k8s-proof.html")


def build_monitoring_page() -> None:
    up_targets = int(prom_scalar("prometheus-up.json"))
    cpu_used = prom_scalar("prometheus-cpu.json")
    mem_free_pct = prom_scalar("prometheus-memory.json")
    disk_free_gb = prom_scalar("prometheus-disk.json") / (1024 ** 3)
    rx_bps = prom_scalar("prometheus-network.json")
    pod_count = int(prom_scalar("prometheus-pod-count.json"))
    deployments = read_json("prometheus-deployments.json")["data"]["result"]

    rows = []
    for item in deployments:
      name = item["metric"].get("deployment", "unknown")
      replicas = item["value"][1]
      rows.append(f"<tr><td><code>{escape(name)}</code></td><td>{escape(replicas)}</td></tr>")

    body = f"""
    <section class="cards-4">
      <div class="card"><div class="metric-label">Prometheus targets up</div><div class="metric-value">{up_targets}</div></div>
      <div class="card"><div class="metric-label">CPU used</div><div class="metric-value">{cpu_used:.2f}%</div></div>
      <div class="card"><div class="metric-label">Memory available</div><div class="metric-value">{mem_free_pct:.2f}%</div></div>
      <div class="card"><div class="metric-label">Disk available on /</div><div class="metric-value">{disk_free_gb:.1f} GB</div></div>
    </section>
    <section class="grid">
      <div class="panel">
        <h2>Node Exporter / system metrics</h2>
        <p>Эти метрики дальше визуализируются в Grafana system dashboard.</p>
        <table>
          <tr><th>Metric</th><th>Value</th></tr>
          <tr><td><code>sum(up)</code></td><td>{up_targets}</td></tr>
          <tr><td><code>CPU used</code></td><td>{cpu_used:.2f}%</td></tr>
          <tr><td><code>Memory available</code></td><td>{mem_free_pct:.2f}%</td></tr>
          <tr><td><code>Disk available</code></td><td>{disk_free_gb:.1f} GB</td></tr>
          <tr><td><code>Network receive rate</code></td><td>{rx_bps / 1024:.2f} KB/s</td></tr>
        </table>
      </div>
      <div class="panel">
        <h2>kube-state-metrics / Kubernetes objects</h2>
        <p>Подтверждение состояния workload'ов из namespace <code>mega-coder</code>.</p>
        <p class="small">Общее количество pod в namespace: <strong>{pod_count}</strong></p>
        <table>
          <tr><th>Deployment</th><th>Available replicas</th></tr>
          {''.join(rows)}
        </table>
      </div>
    </section>
    <section class="panel">
      <h2>Grafana dashboards used in demo</h2>
      <p><code>MEGA CODER / DevOps Overview</code> — основной dashboard для защиты: system metrics, Kubernetes replicas и Loki logs в одном месте.</p>
      <p><code>MEGA CODER / App Logs</code> — отдельный dashboard с логами приложения, если нужно показать Loki подробнее.</p>
      <p class="small">URL Grafana: <code>http://192.168.1.29:30030</code></p>
    </section>
    """
    render_page("Monitoring evidence: Prometheus + Grafana datasources", body, "monitoring-proof.html")


def build_loki_page() -> None:
    loki = read_json("loki-query.json")
    streams = loki["data"]["result"]
    entries = []
    for stream in streams:
        labels = stream["stream"]
        component = labels.get("component", labels.get("container", "unknown"))
        pod = labels.get("pod", "unknown")
        values = stream["values"][:3]
        for _, line in values:
            entries.append((component, pod, line))

    rows = []
    for component, pod, line in entries[:12]:
        rows.append(
            f"<tr><td><code>{escape(component)}</code></td><td><code>{escape(pod)}</code></td><td>{escape(line)}</td></tr>"
        )

    body = f"""
    <section class="panel" style="margin-bottom: 18px;">
      <h2>Loki / App logs</h2>
      <p>Логи подтягиваются из <code>promtail</code> в <code>Loki</code> по label <code>namespace=&quot;mega-coder&quot;</code>.</p>
      <p><span class="pill">api</span><span class="pill">web</span><span class="pill">worker</span></p>
    </section>
    <section class="panel">
      <table>
        <tr><th>Component</th><th>Pod</th><th>Log line</th></tr>
        {''.join(rows)}
      </table>
    </section>
    """
    render_page("Loki evidence: live logs from namespace mega-coder", body, "loki-proof.html")


def main() -> None:
    build_backend_page()
    build_k8s_page()
    build_monitoring_page()
    build_loki_page()


if __name__ == "__main__":
    main()
