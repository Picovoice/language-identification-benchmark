import argparse
import json
import os
from typing import *

import matplotlib.pyplot as plt

from benchmark import RESULTS_FOLDER
from dataset import Datasets
from engine import Engines
from metric import Metrics

Color = Tuple[float, float, float]


def rgb_from_hex(x: str) -> Color:
    x = x.strip("# ")
    assert len(x) == 6
    return int(x[:2], 16) / 255, int(x[2:4], 16) / 255, int(x[4:], 16) / 255


BLACK = rgb_from_hex("#000000")
GREY1 = rgb_from_hex("#3F3F3F")
GREY2 = rgb_from_hex("#5F5F5F")
GREY3 = rgb_from_hex("#7F7F7F")
GREY4 = rgb_from_hex("#9F9F9F")
GREY5 = rgb_from_hex("#BFBFBF")
WHITE = rgb_from_hex("#FFFFFF")
BLUE = rgb_from_hex("#377DFF")

ENGINE_COLORS = {
    Engines.PICOVOICE_BAT: BLUE,
    Engines.SPEECHBRAIN: GREY1,
}

ENGINE_PRINT_NAMES = {
    Engines.PICOVOICE_BAT: "Picovoice\nBat",
    Engines.SPEECHBRAIN: "SpeechBrain",
}


def _plot_metric(
        results: dict,
        dataset: Datasets,
        metric: Metrics,
        show: bool) -> None:
    fig, ax = plt.subplots(figsize=(6, 4))
    for engine in Engines:
        engine_value = results[dataset][engine][metric.value] * 100
        engine_value = round(engine_value, 2)
        ax.bar(
            ENGINE_PRINT_NAMES[engine],
            engine_value,
            width=0.5,
            color=ENGINE_COLORS[engine],
            edgecolor="none",
            label=ENGINE_PRINT_NAMES[engine]
        )
        ax.text(
            ENGINE_PRINT_NAMES[engine],
            engine_value,
            f"{engine_value:.2f}%",
            ha="center",
            va="bottom",
            fontsize=12,
            color=ENGINE_COLORS[engine],
        )

    more_info = ""
    if metric is Metrics.ACCURACY:
        more_info = " (higher is better)"

    ax.set_ylabel(f"{metric.value} {more_info}", fontsize=12)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_visible(False)
    ax.set_yticks([])

    plot_path = os.path.join(
        RESULTS_FOLDER,
        "plots",
        dataset.value,
        metric.value.lower().replace(" ", "_") + ".png")
    plt.savefig(plot_path, bbox_inches="tight")
    print(f"Saved plot to {plot_path}")

    if show:
        plt.show()

    plt.close()


def _plot_average_metric(
        results: dict,
        metric: Metrics,
        show: bool) -> None:
    fig, ax = plt.subplots(figsize=(6, 4))
    for engine in Engines:
        engine_value = 0.0
        for dataset in Datasets:
            engine_value += results[dataset][engine][metric.value] * 100
        engine_value = round(engine_value / len(Datasets), 2)

        ax.bar(
            ENGINE_PRINT_NAMES[engine],
            engine_value,
            width=0.5,
            color=ENGINE_COLORS[engine],
            edgecolor="none",
            label=ENGINE_PRINT_NAMES[engine]
        )
        ax.text(
            ENGINE_PRINT_NAMES[engine],
            engine_value,
            f"{engine_value:.2f}%",
            ha="center",
            va="bottom",
            fontsize=12,
            color=ENGINE_COLORS[engine],
        )

    more_info = ""
    if metric is Metrics.ACCURACY:
        more_info = " (higher is better)"

    ax.set_ylabel(f"{metric.value} {more_info}", fontsize=12)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_visible(False)
    ax.set_yticks([])

    plot_path = os.path.join(
        RESULTS_FOLDER,
        "plots",
        metric.value.lower().replace(" ", "_") + ".png")
    plt.savefig(plot_path, bbox_inches="tight")
    print(f"Saved plot to {plot_path}")

    if show:
        plt.show()

    plt.close()


def _plot_cpu(
        results: dict,
        show: bool) -> None:
    fig, ax = plt.subplots(figsize=(6, 4))
    for engine in Engines:
        process_time = 0.0
        audio_time = 0.0
        for dataset in Datasets:
            process_time += results[dataset][engine]["process_time"]
            audio_time += results[dataset][engine]["audio_time"]

        core_hour = (process_time / audio_time * 100)
        ax.barh(
            ENGINE_PRINT_NAMES[engine],
            core_hour,
            height=0.5,
            color=ENGINE_COLORS[engine],
            edgecolor="none",
            label=ENGINE_PRINT_NAMES[engine],
        )
        ax.text(
            core_hour + 0.75,
            ENGINE_PRINT_NAMES[engine],
            f"{core_hour:.1f}\nCore-hour" if core_hour >= 1 else f"{core_hour:.2f}\nCore-hour",
            ha="center",
            va="center",
            fontsize=12,
            color=ENGINE_COLORS[engine],
        )

    ax.spines["top"].set_visible(False)
    ax.spines["bottom"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.set_xticks([])
    plt.title("Core-hour required to process 100 hours of audio (lower is better)", fontsize=12)
    plot_path = os.path.join(
        RESULTS_FOLDER,
        "plots",
        "cpu.png")
    plt.savefig(plot_path, bbox_inches="tight")
    print(f"Saved plot to {plot_path}")

    if show:
        plt.show()

    plt.close()


def _plot_mem(
        results: dict,
        show: bool) -> None:
    fig, ax = plt.subplots(figsize=(6, 4))
    for engine in Engines:
        size_bytes = 0.0
        for dataset in Datasets:
            size_bytes += results[dataset][engine]["size_bytes"]
        size_bytes /= len(Datasets)

        size_bytes /= 1024 * 1024

        ax.barh(
            ENGINE_PRINT_NAMES[engine],
            size_bytes,
            height=0.5,
            color=ENGINE_COLORS[engine],
            edgecolor="none",
            label=ENGINE_PRINT_NAMES[engine],
        )
        ax.text(
            size_bytes + 10,
            ENGINE_PRINT_NAMES[engine],
            f"{size_bytes:.2f}MB",
            ha="center",
            va="center",
            fontsize=12,
            color=ENGINE_COLORS[engine],
        )

    ax.spines["top"].set_visible(False)
    ax.spines["bottom"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.set_xticks([])
    plt.title("MB required to initialize the model", fontsize=12)
    plot_path = os.path.join(
        RESULTS_FOLDER,
        "plots",
        "mem.png")
    plt.savefig(plot_path, bbox_inches="tight")
    print(f"Saved plot to {plot_path}")

    if show:
        plt.show()

    plt.close()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--show", action="store_true")
    args = parser.parse_args()

    results = {}
    for dataset in Datasets:
        results[dataset] = {}
        for engine in Engines:
            result_path = os.path.join(
                RESULTS_FOLDER,
                "data",
                dataset.value,
                engine.value + ".json")
            with open(result_path, "r", encoding="utf-8") as fd:
                results[dataset][engine] = json.load(fd)

    for dataset in Datasets:
        for metric in Metrics:
            _plot_metric(results, dataset, metric, args.show)
        _plot_average_metric(results, metric, args.show)
    _plot_cpu(results, args.show)
    _plot_mem(results, args.show)


if __name__ == "__main__":
    main()

__all__ = [
    "Color",
    "plot_results",
    "rgb_from_hex",
]