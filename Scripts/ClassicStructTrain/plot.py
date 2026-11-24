"""Render scientific control figures from saved measurements, without simulation."""
import argparse
import json
from pathlib import Path
import sys

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / ".deps/classic-plot-python"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from report_paths import report_path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from evaluate import metrics


def records(path):
    if not path.exists():
        return []
    result = []
    for line in path.read_text(encoding="utf-8").splitlines():
        try:
            result.append(json.loads(line))
        except json.JSONDecodeError:
            # An interrupted historical probe has an incomplete final line.
            pass
    return result


def main(run):
    output = run / "figures"
    output.mkdir(exist_ok=True)
    evidence = json.loads((REPO / "Reports/StructTrainClassic/_work/archive-evidence.json").read_text(encoding="utf-8"))
    actual = [r for p in sorted(run.glob("recognition*/results.jsonl")) for r in records(p)
              if r.get("frozen_archive_structure") and r.get("status") == "completed"]
    if actual:
        first = {r["reference"]["variant_index"]: r for r in actual if r["repeat"] == 1}
        indices = sorted(first)
        classes = [x["class"] for x in evidence["dataset"]]
        archive, observed, labels = [], [], []
        for index in indices:
            r = first[index]
            ref = evidence["recognition"][index]
            archive.append(100*metrics(ref["answers"], classes, (r["id"]-1)//50+1)["balanced_accuracy"])
            observed.append(100*r["balanced_accuracy"])
            labels.append(("NL" if r["kind"] == "learner" else "NT") + str(r["id"]) +
                          (str(ref["variant"])[str(ref["variant"]).find("("):] if "(" in str(ref["variant"]) else ""))
        fig, ax = plt.subplots(figsize=(13, 5.3), layout="constrained")
        ax.bar([i-.19 for i in range(len(indices))], archive, .38, label="Archive", color="#46688c")
        ax.bar([i+.19 for i in range(len(indices))], observed, .38, label="Reconstructed frozen structure", color="#d98c36")
        ax.set(ylim=(0, 105), ylabel="Balanced accuracy (%)", xticks=range(len(indices)), xticklabels=labels,
               title="Recognition on 150 inputs — frozen structures, not repeated training")
        ax.tick_params(axis="x", labelrotation=65)
        ax.spines[["right", "top"]].set_visible(False)
        ax.legend(loc="lower right")
        ax.grid(axis="y", alpha=.2)
        fig.savefig(output / "frozen-recognition.png", dpi=170)
        fig.savefig(output / "frozen-recognition.pdf")
        plt.close(fig)
    trace = records(REPO / "Reports/StructTrainClassic/_work/smoke-20261123-a1/smoke-r1/iterations.jsonl")
    trace = [r for r in trace if r.get("case") == "learner-22"]
    if trace:
        fig, axes = plt.subplots(2, 1, figsize=(8.5, 6), sharex=True, layout="constrained")
        x = [r["iteration"] for r in trace]
        for i in range(4):
            axes[0].plot(x, [r["synapses"][i] for r in trace], label=f"Input {i+1}", alpha=.8)
            axes[1].plot(x, [r["soma_maxima"][i] for r in trace], alpha=.8)
        axes[0].set(ylabel="Reported synapse count", title="Failed native control — learning did not complete")
        axes[1].set(xlabel="Native iteration", ylabel="Soma maximum (V)")
        axes[0].legend(ncol=4)
        for ax in axes:
            ax.grid(alpha=.2)
            ax.spines[["right", "top"]].set_visible(False)
        fig.savefig(output / "failed-native-control.png", dpi=170)
        fig.savefig(output / "failed-native-control.pdf")
        plt.close(fig)
    print(output)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run", type=Path)
    main(report_path(parser.parse_args().run.resolve()))
