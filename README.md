# Language Identification Benchmark

Made in Vancouver, Canada by [Picovoice](https://picovoice.ai)

This repository serves as a minimalist and extensible framework designed for benchmarking various language indentification engines in the context of streaming audio.

## Table of Contents

- [Methodology](#methodology)
- [Metrics](#metrics)
- [Engines](#engines)
- [Usage](#usage)
- [Results](#results)

## Methodology

For this benchmark, audio from various languages is fed into the engine and and the highest scored language is compared to the truth. For un-supported languages, if the engine returns "unknown" it is counted as a success.

## Metrics

### Accuracy Percentage

The Accuracy metric is determined by taking the simple percentage of correct inferences over the total inferences:

$$
ACCURACY = \frac{CORRECT}{INCORRECT + CORRECT}
$$

### Model Size

The size of the model on init is used to evaluate the memory consumption of the language identification engine, indicating the minimum amount of ram required to use the engine.

## Engines

- [Picovoice Bat](https://picovoice.ai/)
- [SpeechBrain](https://github.com/speechbrain/speechbrain)

## Usage

This benchmark has been developed and tested on `Ubuntu 24.04` using `Python 3.12`.

1. Install the requirements:

  ```console
  pip3 install -r requirements.txt
  ```

2. Run the command. Specify the desired engine using the `--engine` flag. For instructions on each engine and the required flags, consult the section below.

```console
python3 -m benchmark \
   --engine ${ENGINE} \
   ...
```

Additionally,

#### Picovoice Bat Instructions

Replace `${PICOVOICE_ACCESS_KEY}` with AccessKey obtained from [Picovoice Console](https://console.picovoice.ai/).

```console
python3 -m benchmark \
   --engine bat \
   --picovoice-access-key ${PICOVOICE_ACCESS_KEY}
```

#### SpeechBrain Instructions

```console
python3 -m benchmark \
   --engine speechbrain
```

## Results

Measurement is carried on an `Ubuntu 24.04.3 LTS` machine with Intel CPU (`Intel(R) Core(TM) i7-1185G7 @ 3.00GHz`),
16 GB of RAM, and NVMe storage.

### Accuracy

|     Engine      |   Accuracy   |
|:---------------:|:------------:|
|  Picovoice Bat  |    92.86%    |
|   SpeechBrain   |    85.03%    |

![](./results/plots/accuracy.png)

### Model Size

|     Engine      | Model Size |
|:---------------:|:----------:|
|  Picovoice Bat  |    5.1MB   |
|   SpeechBrain   |  115.20MB  |

![](./results/plots/mem.png)

### CPU

|     Engine      |  Core-Hour |
|:---------------:|:----------:|
|  Picovoice Bat  |    0.62    |
|   SpeechBrain   |    5.20    |

![](./results/plots/cpu.png)