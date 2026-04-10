import time
import os
from enum import Enum
from typing import (
    Any,
    Dict,
    Sequence,
    Tuple
)

import psutil
import numpy as np
import torch
from speechbrain.inference.classifiers import EncoderClassifier

import pvbat
from pvbat import BatLanguages


class Engines(Enum):
    PICOVOICE_BAT = "bat"
    SPEECHBRAIN = "speechbrain"


class Engine(object):
    def process(self, pcm: Sequence[int]) -> Tuple[Dict[BatLanguages, float], float]:
        raise NotImplementedError()

    @property
    def size_bytes(self) -> int:
        raise NotImplementedError

    def __str__(self) -> str:
        raise NotImplementedError()

    @classmethod
    def create(cls, engine: Engines, **kwargs: Any) -> 'Engine':
        children = {
            Engines.PICOVOICE_BAT: BatEngine,
            Engines.SPEECHBRAIN: SpeechBrainEngine,
        }

        if engine not in children:
            raise ValueError(f"Cannot create {cls.__name__} of type {engine.value}")

        return children[engine](**kwargs)


class BatEngine(Engine):
    def __init__(self, access_key: str, device: str) -> None:
        pre_bytes = psutil.Process(os.getpid()).memory_info().rss

        self._classifier = pvbat.create(access_key=access_key, device=device, voice_threshold=.02)

        post_bytes = psutil.Process(os.getpid()).memory_info().rss
        self._size_bytes = post_bytes - pre_bytes

    def process(self, pcm: Sequence[int]) -> Tuple[Dict[BatLanguages, float], float]:
        start_time = time.perf_counter()

        i = 0
        result = None
        for i in range(len(pcm) // self._classifier.frame_length):
            partial = self._classifier.process(pcm[i * self._classifier.frame_length:(i + 1) * self._classifier.frame_length])
            if result is None:
                result = partial
                if result is not None:
                    i = 1
            elif partial is not None:
                for k, v in partial.items():
                    result[k] += v
                i += 1

        if result is not None:
            for k in result.keys():
                result[k] /= i

        end_time = time.perf_counter()
        return result, end_time - start_time

    @property
    def size_bytes(self) -> int:
        return self._size_bytes

    def __str__(self) -> str:
        return f"{self.__class__.__bases__[0].__name__}[{Engines.PICOVOICE_BAT.value}]"


class SpeechBrainEngine(Engine):
    def __init__(self) -> None:
        pre_bytes = psutil.Process(os.getpid()).memory_info().rss

        self._classifier = EncoderClassifier.from_hparams(
            source="speechbrain/lang-id-voxlingua107-ecapa",
            run_opts={"device": "cpu"})
        self._classifier.hparams.label_encoder.expect_len(107)

        post_bytes = psutil.Process(os.getpid()).memory_info().rss
        self._size_bytes = post_bytes - pre_bytes

    def process(self, pcm: Sequence[int]) -> Dict[BatLanguages, float]:
        start_time = time.perf_counter()

        audio = np.array(pcm, dtype=np.single) / 32768.0
        probs = self._classifier.classify_batch(torch.from_numpy(audio).unsqueeze(0))[0][0]

        indices = torch.arange(probs.numel(), device=probs.device)
        labels = self._classifier.hparams.label_encoder.decode_torch(indices)
        labels = [x.split(":")[0].strip() for x in labels]

        result: Dict[BatLanguages, float] = {
            BatLanguages.DE: 0.0,
            BatLanguages.EN: 0.0,
            BatLanguages.ES: 0.0,
            BatLanguages.FR: 0.0,
            BatLanguages.IT: 0.0,
            BatLanguages.JA: 0.0,
            BatLanguages.KO: 0.0,
            BatLanguages.PT: 0.0,
            BatLanguages.UNKNOWN: 0.0,
        }

        for label, prob in zip(labels, probs.tolist()):
            try:
                lang = BatLanguages.from_str(str(label))
            except KeyError:
                lang = BatLanguages.UNKNOWN
            result[lang] += float(prob)

        end_time = time.perf_counter()
        return result, end_time - start_time

    @property
    def size_bytes(self) -> int:
        return self._size_bytes

    def __str__(self) -> str:
        return f"{self.__class__.__bases__[0].__name__}[{Engines.SPEECHBRAIN.value}]"


__all__ = [
    "Engine",
    "Engines",
]
