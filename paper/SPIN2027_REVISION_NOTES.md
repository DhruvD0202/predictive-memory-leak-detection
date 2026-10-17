# SPIN 2027 revision — 16 October 2026

This version responds to the professor's 23 comments. Earlier named and two-column drafts are retained as historical versions; `paper/spin2027/main.tex` is the revised source. Do not submit the older two-column PDF to SPIN on the assumption that its layout is compliant.

## Verified submission instructions

The [SPIN paper-submission guidelines](https://conferences.amity.edu/SPIN2027/Paper-Submission-Guidelines.aspx) require an **anonymous initial submission, Springer single-column format, 8–15 pages, and no page numbers**. Author names, registration numbers, affiliation and identifying acknowledgements are therefore omitted from this initial-submission version. Retain the three authors in the conference submission system as required; add their names to a camera-ready manuscript only at the appropriate stage. No affiliation has been invented.

The [important dates](https://conferences.amity.edu/SPIN2027/ImportantDates.aspx), checked on 16 October 2026, list **31 October 2026** as the paper deadline. Submission, author registration, copyright transfer and acceptance are not performed or implied by this revision.

The [Springer proceedings author page](https://www.springernature.com/gp/authors/publish-a-book/step-by-step-conference-proceedings) links the [official LaTeX package](https://cms-resources.apps.public.k8s.springernature.io/springer-cms/rest/v1/content/26361882/data/v8). That download contains **LLNCS 2.25, dated 3 September 2026**, described as supporting LNCS and other proceedings series. Its `llncs.cls` and `splncs04.bst` are included unchanged. The manuscript uses its default text dimensions and font sizes. The package SHA-256 is `42afb32ed4fadc9e209134ec65dab1bd2a7ead42f9a3f8abb184f250c4a197b9`.

Springer's [engineering-proceedings instructions](https://cms-resources.apps.public.k8s.springernature.io/springer-cms/rest/v1/content/26362278/data/v2) and [current author instructions including AI disclosure](https://cms-resources.apps.public.k8s.springernature.io/springer-cms/rest/v1/content/53830640/data/v3) were checked. The initial PDF contains a first-page AI-assistance footnote, an end disclosure and concise figure/table acknowledgements. These describe assistance actually used; they do not certify that the authors have completed their final review.

## Evidence and wording

- New title: **Memory-Pressure Forecasting and Growth-Based Warnings: An Empirical Study**.
- Original Colab results remain clearly identified as one seed-42 experiment. They are not overwritten by the new CPU runs.
- The revision adds a fixed five-seed, two-feature-set study on all four recordings: 40 models. The memory-only ablation retains the multivariate coverage mask, splits, history, horizons and training settings.
- All seed results are reported; no best test seed is selected. Mean and sample SD concern training randomness on reused holdouts, not independent replication on new machines.
- The missed original event is identified from saved labels and decision scores. No heap-allocation diagnosis is inferred from aggregate RAM.
- Pre-exhaustion warning, naturally occurring leak diagnosis, individual-feature usefulness and production deployment performance remain unproven.
- No additional labeled recording was acquired. A bounded Windows collection was attempted but failed before collecting a sample because performance counters were inaccessible in the restricted environment. An unrestricted benchmark was not executed because automatic approval review was unavailable; the user then requested that the limitation be documented. The successful benchmark measures archived replay and saved-model inference only. No live performance or CPU-overhead measurement is claimed.
- The retained 36 distinct references meet the earlier request for at least 30 references. Bibliographic records and limited claim support are checked; not every subscription full text has been read. See the existing reference audit and the revision citation map.

The prose was rewritten around specific measurements and limitations, with citations for external ideas. No manuscript was uploaded to a third-party plagiarism or AI detector. No similarity percentage, detector result or guarantee of an “AI-free” manuscript is claimed. The team must read the final text, verify its account of their work and comply with the publisher's disclosure requirements before submission.

## Author decisions still required before actual submission

1. Read and approve the revised interpretation, including unfavorable results and reused-holdout limitations.
2. Confirm the conference's current instructions and author information in its submission portal. This file records the requirements visible on the checked date.
3. Arrange an anonymous reviewer-access route for the code and required data packages. The GitHub repository is private; a local supplementary ZIP does not make it public or automatically attach it to a conference submission.
4. Check any institutional requirements and originality declaration. Do not claim independent authorship without disclosing the assistance actually used.

Compilation, page count, numerical checks and archive verification are recorded in `SPIN2027_FINAL_CHECKS.md` after the final build.
