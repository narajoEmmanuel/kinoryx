# Stage 03, Signal Processing Experiments

**Status:** Not started. Experimental tools may exist in code but they are not an approved processing pipeline.

## Purpose

Compare each proposed processing operation to the original EMG and document its assumptions, parameter choices and effects.

## Proposed experiments

- Digital band-pass filtering with explicit cutoffs, order and zero-phase implementation limits.
- Rectification and envelope/RMS approaches with clearly defined window lengths.
- Comparisons of boundary effects, parameter sensitivity and retained versus attenuated waveform structure.

## Evidence required before interpretation

Record the exact code revision, sample rate, interval, parameters and expected effect. Display the original alongside each transform. Never equate transformed amplitude with force, normalized activation, validated onset time or diagnosis without further supporting methods.

**Next action:** review Signal Quality Assessment and choose justified candidate methods.
