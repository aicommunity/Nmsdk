"""Plot recorded training and inference signals used in the NeuroModeler guide."""

import argparse
import json
from pathlib import Path

import matplotlib.pyplot as plt


def read_records(path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]


def plot_training(source, output):
    figure, (amplitude, structure) = plt.subplots(2, 1, figsize=(9.5, 5.9), sharex=True)
    for kind, label, color in (("trainer", "NT", "#126388"), ("learner", "NL", "#A24B16")):
        data = read_records(source / f"training-{kind}-22/iterations.jsonl")
        times = [row["model_time"] for row in data]
        if kind == "learner":
            amplitude.plot(times, [max(row["soma_maxima"]) * 1000 for row in data],
                           "o--", color=color, markersize=4, linewidth=1, label=label)
        structure.step(times, [sum(row["dendrites"]) for row in data],
                       where="post", color=color, linewidth=1.5, label=f"{label} · сегменты")
        structure.step(times, [sum(row["synapses"]) for row in data],
                       where="post", color=color, linestyle="--", linewidth=1.5,
                       label=f"{label} · синапсы")
    amplitude.set_ylabel("Максимум потенциала\nучастка сомы, мВ")
    amplitude.set_ylim(bottom=0)
    structure.set_ylabel("Сегменты и синапсы, шт.")
    structure.set_xlabel("Модельное время, с")
    amplitude.legend()
    structure.legend(ncol=2)
    for axes in (amplitude, structure):
        axes.grid(alpha=0.26)
    figure.tight_layout()
    figure.savefig(output / "training-trace.png", dpi=165)
    plt.close(figure)


def plot_inference(source, output):
    records = read_records(source / "inference-NL22/waveforms.jsonl")
    samples = [row for row in records if row["input_id"] == 22]
    figure, (inputs, soma, output_spikes) = plt.subplots(
        3, 1, figsize=(9.5, 5.1), sharex=True, gridspec_kw={"height_ratios": [2, 2, 1]}
    )
    times = [row["time"] * 1000 for row in samples]
    for channel in range(5):
        events = [time for time, row in zip(times, samples, strict=True)
                  if row["sources"][channel] > 0]
        inputs.vlines(events, channel + 0.75, channel + 1.25, color="#126388", linewidth=1.5)
    inputs.set_yticks(range(1, 6))
    inputs.set_ylim(0.5, 5.5)
    inputs.set_ylabel("Канал входа")
    soma.plot(times, [row["sum_soma"] * 1000 for row in samples], color="#126388")
    soma.set_ylabel("Сумма потенциалов\nсомы, мВ")
    spikes = [time for time, row in zip(times, samples, strict=True) if row["LTZone"] > 0.001]
    output_spikes.vlines(spikes, 0, 1, color="#A24B16", linewidth=1.7)
    output_spikes.set_yticks([0, 1])
    output_spikes.set_ylabel("Спайк LTZone")
    output_spikes.set_xlabel("Время от начала предъявления, мс")
    output_spikes.set_xlim(0, times[-1])
    if spikes:
        output_spikes.annotate(f"{spikes[0]:.1f} мс", (spikes[0], 0.75),
                               xytext=(7, 0), textcoords="offset points")
    for axes in (inputs, soma, output_spikes):
        axes.grid(axis="x", alpha=0.26)
    figure.tight_layout()
    figure.savefig(output / "inference-trace.png", dpi=165)
    plt.close(figure)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path, help="Directory of Release verification results")
    parser.add_argument("output", type=Path, help="Directory for the two guide figures")
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    plot_training(args.source, args.output)
    plot_inference(args.source, args.output)


if __name__ == "__main__":
    main()
