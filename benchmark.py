import argparse
import os
import json

from typing import (
    Any,
    Dict
)

import torch

from pvbat import BatLanguages
from dataset import *
from engine import *
from metric import *

RESULTS_FOLDER = os.path.join(os.path.dirname(__file__), "results")


def _engine_params_parser(args: argparse.Namespace) -> Dict[str, Any]:
    kwargs_engine = dict()
    engine = Engines(args.engine)
    if engine is Engines.PICOVOICE_BAT:
        if args.picovoice_access_key is None:
            raise ValueError(f"Engine {args.engine} requires --picovoice-access-key")
        kwargs_engine.update(access_key=args.picovoice_access_key)
        kwargs_engine.update(device=args.picovoice_device)
    return kwargs_engine


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--dataset",
        choices=[x.value for x in Datasets],
        default=Datasets.VOX_LINGUA_107.value)
    parser.add_argument('--length-sec', type=float, default=None)
    parser.add_argument('--engine', choices=[x.value for x in Engines], required=True)
    parser.add_argument("--metric", choices=[x.value for x in Metrics], default=Metrics.ACCURACY.value)
    parser.add_argument("--picovoice-access-key")
    parser.add_argument("--picovoice-device", default="cpu:1")
    args = parser.parse_args()

    torch.set_num_threads(1)

    dataset = Datasets(args.dataset)
    engine = Engines(args.engine)
    metric = Metrics(args.metric)

    length_sample = int(Dataset.sample_rate * args.length_sec) if args.length_sec is not None else None

    engine_kwargs = _engine_params_parser(args)

    dataset = Dataset.create(dataset=dataset, length_sample=length_sample)
    print(dataset)

    engine = Engine.create(engine=engine, **engine_kwargs)
    print(engine)

    metric = Metric.create(metric)

    num_correct = 0
    num_wrong = 0
    total_process_time = 0.0
    total_audio_time = 0.0
    for language in BatLanguages:
        for i in range(dataset.size(language)):
            probs, process_time = engine.process(dataset.get(language, i))
            audio_time = len(dataset.get(language, i)) / dataset.sample_rate
            prediction = max(probs, key=probs.get)
            if prediction == language:
                num_correct += 1
            else:
                num_wrong += 1
            total_process_time += process_time
            total_audio_time += audio_time

    with measure_peak_memory() as peak_memory_result:
        for language in BatLanguages:
            for i in range(dataset.size(language)):
                _, _ = engine.process(dataset.get(language, i))

    accuracy = metric.compute(num_correct, num_wrong)
    rtf = total_process_time / total_audio_time

    print(f"{metric}: {accuracy:.2f}")
    print(f"🚀 RTF {rtf:.03f}")

    results_path = os.path.join(RESULTS_FOLDER, "data", args.dataset, f"{args.engine}.json")
    results = {
        args.metric: accuracy,
        "init_size_bytes": engine.size_bytes,
        "proc_size_bytes": peak_memory_result['peak_mem'],
        "process_time": total_process_time,
        "audio_time": total_audio_time,
    }
    with open(results_path, "w") as f:
        json.dump(results, f, indent=2)


if __name__ == "__main__":
    main()
