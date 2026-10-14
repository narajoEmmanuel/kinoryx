# Scientific validation plan

Current peak candidates are not foot contact events. The project has no clinically verified gait-phase detector and no accuracy estimate.

## Future validation design

1. Define anatomical and signal-based event definitions for both limbs (initial contact, final contact/toe-off), separately from peak candidates.
2. Secure permission and consent for de-identified recordings. Identify sampling frequency, sensor placement, population, walking conditions and software versions.
3. Build independently annotated reference events from synchronized pressure sensors, force plates, footswitches or appropriately reviewed video.
4. Match predicted/reference events under a documented, prespecified temporal tolerance.
5. Report event timing error (bias, MAE, dispersion), sensitivity, precision, false positives and misses by limb, patient and condition.
6. Audit turning, slow walking, pauses, hemiparetic gait, shuffling and irregular cycles as distinct subgroups.
7. Keep patient-level partitions across train/validation/test to avoid leakage.
8. Compare parameter settings and any future learned models with transparent baselines, confidence intervals and failure examples.
9. Explicitly report cases where an event cannot be determined.

Do not infer ground reaction forces, joint moments, medical diagnoses or full gait subphases from unsupported sensors. Synthetic test success is a software integration check, never clinical validation.
