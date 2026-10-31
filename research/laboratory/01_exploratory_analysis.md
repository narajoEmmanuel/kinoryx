# Stage 01, Exploratory Signal Analysis

**Status:** In progress. This stage is actively supported by the local Laboratory workspace.

## Objective

Inspect the **unprocessed** Cometa EMG measurements, channel names and time windows before assigning any meaning to signal excursions. The source `research/source_data/EMG2_Squats-200714130240.mvne` remains unchanged.

## Saved work

- [Original recording inventory](../source_data/README.md), four EMG channels, 2,000 Hz, 16,527 samples per channel.
- [Experiment 01: First EMG Burst, 1.0 to 2.0 s](../experiments/01_first_burst_raw.md), sample-domain statistics and interpretation limits.
- [Investigation journal](../STUDY_LOG.md), screenshots reviewed and quality questions raised.

## Local workspace

Visit `http://127.0.0.1:8050/lab/exploration`.

- Drag a source channel to **Panel A** or **Panel B**; remove and transfer channels without modifying the recording.
- Select **Side by side**, **Stacked** or **Overlay** to change how the two groups of raw traces are arranged.
- Each channel keeps a distinct color across layouts, and the window can be adjusted to inspect individual episodes.
- The initial panels show right and left rectus femoris, respectively, at the first burst (1.0 to 2.0 seconds).
- Overlay uses original values in unknown units. No normalization, filters, physiological activation estimate or inferred gait event is applied.

## Questions still open

1. Are waveform peaks part of broad signal bursts or isolated samples?
2. What repeatable descriptive patterns appear in later windows?
3. How much visual difference is caused by separate y-axis autoscaling?
4. What metadata would support calibrated amplitude comparisons?

**Stage completion requires documented observations and scientific limitations, not a particular number of charts.**
