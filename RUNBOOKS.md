# Runbooks для MEGA CODER alerts

## PodCrashLooping

Проверить:

```bash
sudo k3s kubectl describe pod -n mega-coder <pod>
sudo k3s kubectl logs -n mega-coder <pod> --previous
```

Что искать: ошибка старта контейнера, неправильный image tag, нехватка secret/config, падение приложения.

## PodRestartTooOften

Проверить restart count:

```bash
sudo k3s kubectl get pods -n mega-coder
sudo k3s kubectl describe pod -n mega-coder <pod>
```

Что делать: посмотреть `Last State`, readiness/liveness probes, последние логи.

## DeploymentReplicasMismatch

Проверить rollout:

```bash
sudo k3s kubectl rollout status deployment/<deployment> -n mega-coder
sudo k3s kubectl describe deployment -n mega-coder <deployment>
```

Что делать: проверить образ, pull secret, ресурсы, события scheduling.

## PodNotReady

Проверить readiness:

```bash
sudo k3s kubectl describe pod -n mega-coder <pod>
sudo k3s kubectl logs -n mega-coder <pod> --tail=80
```

Что делать: проверить endpoint `/health`/`/ready`, зависимости Redis/API/worker.

## HighCPUUsage

Проверить top и логи:

```bash
sudo k3s kubectl top pods -n mega-coder
sudo k3s kubectl logs -n mega-coder <pod> --tail=120
```

Что делать: проверить нагрузку, зависшие циклы, поднять limits или уменьшить частоту задач.

## HighMemoryUsage

Проверить потребление памяти:

```bash
sudo k3s kubectl top pods -n mega-coder
sudo k3s kubectl describe pod -n mega-coder <pod>
```

Что делать: искать memory leak, большие ответы, рост очередей/кэша.

## TargetDown

Проверить Service/Endpoints:

```bash
sudo k3s kubectl get svc,endpoints -n mega-coder
sudo k3s kubectl get pods -n mega-coder -o wide
```

Что делать: проверить labels/selector, readiness, Prometheus target discovery.

## TooMany5xx

Проверить ingress/proxy logs:

```bash
sudo k3s kubectl logs -n mega-coder deploy/mega-mega-coder-web --tail=120
sudo k3s kubectl logs -n mega-coder deploy/mega-mega-coder-api --tail=120
```

Что делать: искать backend errors, timeout, неправильный upstream.

## LokiErrorSpike

Проверить Loki/Grafana Explore:

```logql
{namespace="mega-coder"} |= "ERROR"
```

Что делать: сгруппировать ошибки по сервисам `api`, `web`, `worker`, затем открыть соответствующие pod logs.

## GitLabPipelineFailed

Проверить GitLab pipeline:

1. Открыть pipeline URL из Telegram.
2. Открыть failed job logs.
3. Проверить stage: `pre_build`, `build`, `deploy`.
4. Если это deploy, проверить `helm list -A` и `kubectl get pods -A`.
