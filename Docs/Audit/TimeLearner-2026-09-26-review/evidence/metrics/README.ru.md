# Host metrics during SoftCold (reboot forensics)

Сэмплер `sample_host_metrics.py` пишет JSONL с `fsync` каждые N секунд в `host_metrics.jsonl`.
После hard reset хвост файла обычно сохраняется (данные уже на диске).

Поля: UTC ts, loadavg, mem, /proc/stat cpu counters, hwmon (coretemp/acpitz/asus), thermal_zone, PIDs NeuroModeler/posttune_verify.

## Без установки (уже работает)

Читает `/sys/class/hwmon` и `/sys/class/thermal` напрямую. На этой машине: `coretemp` (Package/Core0–3), `acpitz`, `asus`.

```bash
python3 Docs/Audit/TimeLearner-2026-09-26-review/evidence/metrics/sample_host_metrics.py \
  --interval 5 \
  --out Docs/Audit/TimeLearner-2026-09-26-review/evidence/metrics/host_metrics.jsonl
```

## Опционально: lm-sensors (человекочитаемый вывод)

Пакет сейчас **не установлен**. Для `sensors` CLI:

```bash
sudo apt update
sudo apt install -y lm-sensors
sudo sensors-detect --auto   # отвечает Yes по умолчанию на типичные вопросы
sensors
```

Сэмплер от этого не зависит; `lm-sensors` удобен для ручной проверки.

## После reboot

```bash
tail -20 Docs/Audit/TimeLearner-2026-09-26-review/evidence/metrics/host_metrics.jsonl
journalctl --list-boots | tail -5
```

Смотреть: скачок Package temp перед обрывом, рост load, MemAvailable→0, исчезновение NM PID без monitor_stop.
