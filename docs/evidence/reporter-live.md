# MEGA CODER: отчет по Kubernetes

- Сформирован: `2026-04-13 20:25:38 UTC`
- Namespace: `mega-coder`
- Pod'ов: `9`
- Перезапусков контейнеров всего: `0`
- Deployment без нужного числа реплик: `нет`

## Pods
| Pod | Фаза | Готовность | Перезапуски |
|---|---|---:|---:|
| `mega-mega-coder-alert-bot-57648659f9-7xgkm` | Running | 1/1 | 0 |
| `mega-mega-coder-api-78866b6f4d-pnfj2` | Running | 1/1 | 0 |
| `mega-mega-coder-api-78866b6f4d-slrrb` | Running | 1/1 | 0 |
| `mega-mega-coder-redis-56647786b9-tg6cn` | Running | 1/1 | 0 |
| `mega-mega-coder-web-7f7b649ddc-7nn85` | Running | 1/1 | 0 |
| `mega-mega-coder-web-7f7b649ddc-tcvjl` | Running | 1/1 | 0 |
| `mega-mega-coder-worker-7db4f67ddf-69b5c` | Running | 1/1 | 0 |
| `mega-mega-coder-worker-7db4f67ddf-cxm8v` | Running | 1/1 | 0 |
| `reporter-final-evidence-20260413232534-8fw6w` | Running | 1/1 | 0 |

## Deployments
| Deployment | Желаемые реплики | Доступные реплики | Недоступно |
|---|---:|---:|---:|
| `mega-mega-coder-alert-bot` | 1 | 1 | 0 |
| `mega-mega-coder-api` | 2 | 2 | 0 |
| `mega-mega-coder-redis` | 1 | 1 | 0 |
| `mega-mega-coder-web` | 2 | 2 | 0 |
| `mega-mega-coder-worker` | 2 | 2 | 0 |

## Последние Kubernetes Warning/Error events
_Это диагностические события Kubernetes; они могут быть историческими и не всегда означают текущую аварию._
- `UnexpectedJob` Saw a job that the controller did not create or forgot: reporter-final-evidence-20260413232534
- `UnexpectedJob` Saw a job that the controller did not create or forgot: reporter-manual-demo-20260413231839
- `UnexpectedJob` Saw a job that the controller did not create or forgot: reporter-manual-demo-20260413231234
- `FailedScheduling` 0/1 nodes are available: 1 node(s) didn't have free ports for the requested pod ports. no new claims to deallocate, preemption: 0/1 nodes are available: 1 No preemption victims found for incoming pod.
- `UnexpectedJob` Saw a job that the controller did not create or forgot: reporter-manual-demo-20260413224815
- `BackoffLimitExceeded` Job has reached the specified backoff limit
- `BackOff` Back-off restarting failed container reporter in pod reporter-manual-demo-20260413224815-6ps8r_mega-coder(970b80df-6eb1-4d88-9a0e-cd9f06ec027a)

## Краткая сводка метрик
- CPU по pod'ам: `mega-mega-coder-redis-56647786b9-tg6cn: 0.0053029124699194305, mega-mega-coder-api-78866b6f4d-slrrb: 0.0076985302379526475, mega-mega-coder-web-7f7b649ddc-7nn85: 0.00008012316561844695, mega-mega-coder-worker-7db4f67ddf-cxm8v: 0.0022742651761183683, mega-mega-coder-worker-7db4f67ddf-69b5c: 0.002240408318284781`
- Память по pod'ам: `mega-mega-coder-redis-56647786b9-tg6cn: 4112384, mega-mega-coder-api-78866b6f4d-slrrb: 58200064, mega-mega-coder-web-7f7b649ddc-7nn85: 7487488, mega-mega-coder-worker-7db4f67ddf-cxm8v: 41447424, mega-mega-coder-worker-7db4f67ddf-69b5c: 40275968`
- Доступные реплики: `mega-mega-coder-redis: 1, mega-mega-coder-worker: 2, mega-mega-coder-web: 2, mega-mega-coder-api: 2, mega-mega-coder-alert-bot: 1`

## Пример ERROR-логов из Loki
no recent ERROR logs

## Сводка по приложению
- `api`, `web`, `worker` должны иметь по 2 реплики.
- `redis` должен иметь 1 реплику.
- Alerting построен через Prometheus rules + Alertmanager webhook + Telegram bridge.
