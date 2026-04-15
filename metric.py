import threading

from contextlib import contextmanager
from enum import Enum
from typing import (
    Any,
    Generator,
    Sequence,
    Dict,
)

import numpy as np
import psutil


class Metrics(Enum):
    ACCURACY = "accuracy"


class Metric(object):
    def compute(self, num_positives: int, num_negatives: int) -> float:
        raise NotImplementedError()

    def __str__(self) -> str:
        raise NotImplementedError()

    @classmethod
    def create(cls, metric: Metrics) -> "Metric":
        children = {
            Metrics.ACCURACY: AccuracyMetric,
        }

        if metric not in children:
            raise ValueError(f"Cannot create `{cls.__name__}` of type `{metric.value}`")

        return children[metric]()


class AccuracyMetric(Metric):
    def compute(self, num_positives: int, num_negatives: int) -> float:
        return num_positives / (num_negatives + num_positives)

    def __str__(self) -> str:
        return f"🧪[{Metrics.ACCURACY.value}]"


def _memory_tree(proc_main):
    total = 0
    proc_list = [proc_main] + proc_main.children(recursive=True)
    for p in proc_list:
        try:
            total += p.memory_full_info().pss
        except psutil.NoSuchProcess:
            pass
    return total


@contextmanager
def measure_peak_memory(interval: float = 0.005)-> Generator[Dict[str, int], Any, None]:
    proc_main = psutil.Process()
    peak_mem = 0
    result = {
        "peak_mem": peak_mem,
    }
    stop_event = threading.Event()

    initial_mem = _memory_tree(proc_main)

    def _measure():
        nonlocal peak_mem
        while not stop_event.is_set():
            mem = _memory_tree(proc_main)
            peak_mem = max(peak_mem, mem)
            stop_event.wait(interval)

    t = threading.Thread(target=_measure)
    t.start()

    try:
        yield result
    finally:
        stop_event.set()
        t.join()

    result["peak_mem"] = (peak_mem - initial_mem)


__all__ = [
    "Metric",
    "Metrics",
    "measure_peak_memory",
]