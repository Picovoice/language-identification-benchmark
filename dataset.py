import os.path
from enum import Enum
from random import Random
from typing import Optional

import numpy as np
import soundfile
from numpy.typing import NDArray

from pvbat import BatLanguages


class Datasets(Enum):
    VOX_LINGUA_107 = "VoxLingua107"


class Dataset(object):
    def __init__(self, length_sample: Optional[int], seed: Optional[int]) -> None:
        self._length_sample = length_sample

        self._r = Random(seed)

    def get(self, language: BatLanguages, index: int) -> NDArray[np.single]:
        raise NotImplementedError()

    def size(self, language: BatLanguages) -> int:
        raise NotImplementedError()

    @property
    def sample_rate(self) -> int:
        return 16000

    def __str__(self) -> str:
        raise NotImplementedError()

    @classmethod
    def create(cls, dataset: Datasets, length_sample: int, seed: Optional[int] = 666) -> 'Dataset':
        children = {
            Datasets.VOX_LINGUA_107: VoxLingua107Dataset,
        }

        if dataset not in children:
            raise ValueError(f"Cannot create {cls.__name__} of type {dataset.value}")

        return children[dataset](length_sample=length_sample, seed=seed)


class VoxLingua107Dataset(Dataset):
    def __init__(self, length_sample: Optional[int], seed: Optional[int], min_num_samples: int = 2) -> None:
        super().__init__(length_sample=length_sample, seed=seed)

        paths = dict()
        for language in BatLanguages:
            paths[language] = list()
            if language is BatLanguages.UNKNOWN:
                folder = os.path.join(os.path.dirname(__file__), "audio", "voxlingua107")
                for x in sorted(os.listdir(folder)):
                    if x not in [str(xx) for xx in BatLanguages]:
                        language_folder = os.path.join(os.path.dirname(__file__), "audio", "voxlingua107", x)
                        for xx in sorted(os.listdir(language_folder)):
                            paths[language].append(os.path.join(language_folder, xx))
            else:
                language_folder = os.path.join(os.path.dirname(__file__), "audio", "voxlingua107", str(language))
                if os.path.exists(language_folder):
                    for x in sorted(os.listdir(language_folder)):
                        paths[language].append(os.path.join(language_folder, x))
                    if len(paths[language]) < min_num_samples:
                        paths.pop(language)
                else:
                    paths.pop(language)
        num_samples = min(len(v) for v in paths.values())
        for k in list(paths.keys()):
            paths[k] = self._r.sample(paths[k], num_samples)

        self._audios = dict()
        for k in paths.keys():
            self._audios[k] = list()
            for p in paths[k]:
                pcm = soundfile.read(p, dtype='int16')[0]
                if self._length_sample is not None:
                    offset = self._r.randint(0, len(pcm) - self._length_sample)
                    self._audios[k].append(pcm[offset:offset + self._length_sample])
                else:
                    self._audios[k].append(pcm)

    def get(self, language: BatLanguages, index: int) -> NDArray[np.single]:
        return self._audios[language][index]

    def size(self, language: BatLanguages) -> int:
        return len(self._audios[language]) if language in self._audios else 0

    def __str__(self) -> str:
        return f"{self.__class__.__bases__[0].__name__}[{Datasets.VOX_LINGUA_107.value}]"


__all__ = [
    "Dataset",
    "Datasets",
]
