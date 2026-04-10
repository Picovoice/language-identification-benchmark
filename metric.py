from enum import Enum
from typing import Sequence

import numpy as np


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


__all__ = [
    "Metric",
    "Metrics",
]