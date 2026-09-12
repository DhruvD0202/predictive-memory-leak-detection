# Dataset validation checkpoint

Date: 7 September 2026. Validation was run locally in the project workspace; no Colab runtime or training session was used.

## Scope and verdict

Antarex CPU-MEM_mono is suitable for an initial multivariate memory-forecasting and controlled-leak detection experiment. Westermo is suitable for a separate real-workload forecasting experiment. The evidence does not yet support prediction of memory exhaustion, crashes, or naturally occurring production leaks.

The approved dataset pair is retained. The pilot subset is an explicit implementation proposal, not a claim that all Antarex blocks have been validated.

## Acquisition and provenance

- Antarex: Zenodo record 2553224, version 1.0, DOI 10.5281/zenodo.2553224, CC BY 4.0. Publisher metadata is saved in `data/metadata/antarex_record_2553224.json`.
- Publisher ZIP size: 1,632,357,471 bytes. Published full-ZIP MD5: `285e502a5e2943a5e7e5b6dd2663b06a`.
- The full ZIP download stalled. Its partial contents included the complete 487,811,676-byte CPU-MEM_mono 7z archive and both CPU/memory workload schedules. These complete ZIP members were recovered and their sizes and ZIP CRCs verified against the remote central directory. Local SHA-256 values are recorded. **The full ZIP MD5 has not been verified.**
- The nested archive was successfully read and selected telemetry/label members extracted by libarchive. No downloaded workload program or launch script was executed.
- Westermo: pinned Git commit `47e0ccdc10c30e86327d6eb828ed48d164469fd4`, CC BY 4.0. All 19 CSV files plus README and license were downloaded. Each was verified against its published Git blob hash and size. Total CSV size: **379,186,945 bytes**.
- Download, subset and archive-member manifests are in `data/metadata/`.

Sources: [Antarex record](https://zenodo.org/records/2553224), [Antarex documentation](https://zenodo.org/records/2553224/files/Readme_Antarex_Dataset.pdf), [Westermo repository](https://github.com/westermo/test-system-performance-dataset).

## Antarex CPU-MEM_mono

The four required streams were audited over their full row ranges for the selected fields below. Other LDMS streams and the multi-core telemetry have not been numerically audited.

| Stream | Observations | Examples of verified fields |
|---|---:|---|
| meminfo | 1,031,998 | MemTotal, MemAvailable, MemFree, AnonPages, Committed_AS, SwapTotal, SwapFree |
| vmstat | 1,031,988 | pgfault, pgmajfault, pswpin, pswpout, pgpgin, pgpgout |
| procstat | 1,031,985 | user, sys, idle, iowait, context_switches, procs_running |
| procdiskstats | 1,032,014 | read/write operations, sectors and rates for the monitored sdc1 partition |

- Each stream spans approximately 12 days. Median observed spacing is about **1.005 seconds**, rather than exactly one second. The streams have different row counts and fractional timestamp offsets, so joining by row index would be wrong.
- No duplicate exact timestamps, empty cells, nonfinite values or negative values were found in the selected fields.
- Each stream includes some intervals just over two seconds. Model inputs must use timestamp-based alignment with a finite staleness tolerance; long gaps must never be bridged without explicit handling.
- Each stream has one final sample outside the supplied label extent. That sample must be excluded from labeled evaluation.
- Memory quantities in meminfo follow Linux KiB conventions. Convert explicitly to bytes or GiB. CPU and page-fault counters require differences over elapsed time; guest CPU time must not be counted twice.
- The supplied disk byte fields are not assumed to be trustworthy byte totals merely because of their names. If a later block provides varying disk counters, validate them against sector counts and documentation before selecting a throughput measure.

### Ground truth

- Label table: **1,036,807 one-second entries**.
- **228 leak episodes**, identified by matching `status_start` and `status_end` records for the leak program.
- **63,136 seconds** carry the `leak_0` label. This is the literal positive leak category in the supplied label file, not a zero/negative class.
- Start-inclusive, end-exclusive intervals reconstructed from the execution log agree with the leak labels at **every labeled second**: zero mismatches.
- Leak durations: minimum **207 s**, median **260 s**, maximum **693 s**.
- **118 low-intensity episodes** are distinguishable through the execution arguments. The remaining 110 use the other mode.
- No execution-log error field differs from the literal `None` value.
- The block also labels ddot, dial, memeater, cpufreq and pagefail. They must not be collapsed into the positive leak class. They can be used as challenging non-leak cases and reported separately.
- A proposed 70/15/15 chronological split by elapsed time contains **162/31/35 complete leak episodes** before any window purging. These are dataset counts, not model results. No leak episode crosses those proposed boundaries.

### Limits that affect the research claims

For audit purposes, memory pressure was defined as `1 - MemAvailable / MemTotal`.

- Observed range: **1.05% to 42.24%**.
- No sample reaches an illustrative 80% memory-pressure threshold. That threshold is a diagnostic check, not a fitted warning rule.
- SwapTotal and SwapFree are equal throughout; pswpin and pswpout remain zero. Swap is available but unused in this block.
- All inspected disk counters/rates for the monitored partition remain constant/zero. They are not informative model inputs in this block; this does not prove the entire computer performs no disk I/O.
- RAM, CPU and page-fault measurements vary. A model can be genuinely multivariate with these inputs, but this block cannot establish the added predictive value of swap and disk I/O.
- The events were deliberately injected on a real machine. They are not verified naturally occurring production leaks.
- Forecast MAE/RMSE and leak-warning precision/recall/detection delay are possible. Time before actual memory exhaustion or crash is **not evaluable from this block**.

Numerical evidence: `data/metadata/antarex_audit.json` and `data/metadata/antarex_subset_manifest.json`.

## Westermo

- **19 systems**, **1,640,857 total observations**, over a 30-day timestamp extent.
- 16 files have 24 columns including timestamp; systems 8, 11 and 17 have 23 because sys-thermal is absent. Thermal data are not required for the proposed model.
- Nominal sampling is **30 seconds**.
- **12 gaps**, corresponding to **762 missing observations** on the complete 30-second grids. System 1 contains the largest gap: 19,590 seconds between adjacent rows, or 652 missing samples.
- No empty/nonfinite cells, negative values, duplicate timestamps, reversed timestamps or out-of-range derived memory-pressure fractions were found in the audit.
- RAM, CPU, swap and disk fields are present; page-fault fields are absent. Published CPU fields are aggregated rates, not directly percentages bounded by 100 or fractions bounded by one. Keep their native units unless core normalization can be justified.
- Several metrics are already rates. Do not difference these again.
- `server-up` is a reporting/availability indicator, not a memory-leak label. There are no confirmed leak annotations; lack of a label does not establish normality.
- Westermo can support forecasting MAE/RMSE and descriptive warning counts. Precision/recall for real leaks cannot be calculated without independently established labels.

Numerical evidence: `data/metadata/westermo_audit.json`; provenance: `data/metadata/westermo_tree.json` and `data/metadata/download_manifest.json`.

## Acceptance for the pilot

The required pilot data exist locally. Timestamp alignment, rate conversion, split isolation and label mapping were subsequently implemented and verified on 8 September 2026; see [PREPROCESSING_RESULTS.md](PREPROCESSING_RESULTS.md). The [raw Colab input package](../data/packages/review2_pilot_raw.zip) contains the selected unmodified source files and their provenance, and the [processed package](../data/packages/review2_preprocessed.zip) contains the checked model inputs.

Do not concatenate unrelated machines or datasets into one timeline. Do not create synthetic page-fault columns for Westermo or present injected signals as observed OS responses.
