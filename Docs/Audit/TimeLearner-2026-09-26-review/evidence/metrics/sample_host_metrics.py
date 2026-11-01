#!/usr/bin/env python3
"""Sample host metrics every INTERVAL sec; fsync each line so hard reset keeps last samples."""
from __future__ import annotations
import json, os, time, argparse
from pathlib import Path
from datetime import datetime, timezone

def read_hwmon() -> dict:
    out = {}
    base = Path('/sys/class/hwmon')
    if not base.exists():
        return out
    for hw in sorted(base.glob('hwmon*')):
        try:
            name = (hw / 'name').read_text().strip()
        except OSError:
            continue
        temps = {}
        for t in sorted(hw.glob('temp*_input')):
            lab = t.with_name(t.name.replace('_input', '_label'))
            try:
                label = lab.read_text().strip() if lab.exists() else t.name
                temps[label] = round(int(t.read_text()) / 1000.0, 1)
            except OSError:
                continue
        if temps:
            out[name] = temps
    return out

def meminfo() -> dict:
    want = {'MemTotal', 'MemAvailable', 'MemFree', 'SwapTotal', 'SwapFree', 'Cached', 'Buffers'}
    d = {}
    for line in Path('/proc/meminfo').read_text().splitlines():
        k, v = line.split(':', 1)
        if k in want:
            d[k] = int(v.strip().split()[0])  # KiB
    return d

def loadavg() -> list:
    return [float(x) for x in Path('/proc/loadavg').read_text().split()[:3]]

def cpu_stat() -> dict:
    # first line of /proc/stat
    parts = Path('/proc/stat').read_text().splitlines()[0].split()
    # user nice system idle iowait irq softirq steal
    keys = ['user', 'nice', 'system', 'idle', 'iowait', 'irq', 'softirq', 'steal']
    vals = [int(x) for x in parts[1:1+len(keys)]]
    return dict(zip(keys, vals))

def thermal_zone() -> dict:
    out = {}
    for z in sorted(Path('/sys/class/thermal').glob('thermal_zone*')):
        try:
            typ = (z / 'type').read_text().strip()
            temp = int((z / 'temp').read_text()) / 1000.0
            out[f'{z.name}:{typ}'] = round(temp, 1)
        except OSError:
            continue
    return out

def nm_pids() -> list:
    pids = []
    for p in Path('/proc').iterdir():
        if not p.name.isdigit():
            continue
        try:
            cmd = (p / 'cmdline').read_bytes().replace(b'\x00', b' ').decode('utf-8', 'replace')
        except OSError:
            continue
        if 'NeuroModeler' in cmd or 'posttune_verify' in cmd:
            pids.append({'pid': int(p.name), 'cmd': cmd[:160]})
    return pids

def sample() -> dict:
    return {
        'ts': datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
        'mono': round(time.monotonic(), 1),
        'loadavg': loadavg(),
        'mem_kib': meminfo(),
        'cpu': cpu_stat(),
        'hwmon': read_hwmon(),
        'thermal': thermal_zone(),
        'nm': nm_pids(),
    }

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--interval', type=float, default=5.0)
    ap.add_argument('--out', type=Path, required=True)
    args = ap.parse_args()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    # marker for reboot correlation
    with open(args.out, 'a', encoding='utf-8') as f:
        f.write(json.dumps({'event': 'monitor_start', 'ts': datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'), 'pid': os.getpid()}) + '\n')
        f.flush(); os.fsync(f.fileno())
    while True:
        row = sample()
        line = json.dumps(row, ensure_ascii=False) + '\n'
        with open(args.out, 'a', encoding='utf-8') as f:
            f.write(line)
            f.flush()
            os.fsync(f.fileno())
        # also touch a tiny last.json for quick look
        last = args.out.with_name('last_sample.json')
        with open(last, 'w', encoding='utf-8') as f:
            f.write(json.dumps(row, indent=2, ensure_ascii=False) + '\n')
            f.flush(); os.fsync(f.fileno())
        time.sleep(args.interval)

if __name__ == '__main__':
    main()
