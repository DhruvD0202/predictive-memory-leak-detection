# Reference audit and relevance map

External sources checked: 14 September 2026. Current scope: Introduction through Preliminary Results and Discussion. The 15 September architecture, setup and results additions use local implementation/experiment records and existing references [3]-[6], [31]-[34]; the 36-entry bibliography is unchanged. See `DRAFTING_NOTES.md` and `RESULTS_EVIDENCE.md` for evidence maps. New experimental values are not attributed to external papers.

The user approved the Introduction and requested at least 30+ references. This checkpoint contains **36 distinct works**, each cited in the current manuscript. The sources are a mixture of journal/conference publications, books, a dataset and explicitly identified arXiv records. They are not described as 36 peer-reviewed research articles. Different versions or hosting pages of one work count once.

Verification means bibliographic identity and the limited claims used in the draft were checked against publisher pages, original paper text, author/institutional records or publisher-deposited Crossref metadata. It does **not** mean every cited work was read in full. Subscription abstracts support only the broad descriptions stated in the survey, not unexamined implementation details or numerical comparisons. No results from another paper are presented as results of this project.

The original Review 1 report was read in full. Source titles, authors and dates were corrected where necessary; its references were not copied without checking. Titles use the published wording; ASCII transliterations of diacritics are used in the current PDF bibliography where needed.

## Evidence and role of each reference

| Ref. | Work and role in the manuscript | Verification source and reading scope |
|---|---|---|
| 1 | Jindal et al. (2021): detection from memory utilization; not our exact warning algorithm. | [arXiv record and abstract](https://arxiv.org/abs/2106.08938). Preprint; original title and six authors checked. |
| 2 | Assi et al. (2022): direct Box-Jenkins/LSTM comparison for OS performance. | Local publisher PDF, `Time series forecast modeling for the Windows operating.pdf`; title, authors, journal, pages, DOI and comparative scope checked. |
| 3 | Antarex v1.0: dataset provenance and controlled injected faults. | [Zenodo record](https://zenodo.org/records/2553224), saved provider metadata and dataset Readme. Metadata publication date is 2018-10-10; record creation is in 2019. |
| 4 | Netti et al., FINJ (2019): injection tool attribution. | [Institutional publisher record](https://cris.unibo.it/handle/11585/668910). The proceedings title contains 2018, but publication is 2019. |
| 5 | Netti et al. (2018, revised 2019): associated HPC classification/data study. | [arXiv record and abstract](https://arxiv.org/abs/1810.11208). Cited as the identified arXiv version. |
| 6 | Strandberg and Marklund (2023): real industrial telemetry. | [arXiv record and abstract](https://arxiv.org/abs/2311.14510), plus the audited dataset repository. No leak labels inferred. |
| 7 | Huang et al. (1995): established proactive rejuvenation direction. | [Publisher-deposited Crossref metadata](https://api.crossref.org/works/10.1109/FTCS.1995.466961), [IFIP award record](https://www.dependability.org/wg10.4/news-040219.html). Original publisher full text was unavailable; only the documented high-level concept is used. |
| 8 | Vaidyanathan and Trivedi (1999): workload-conditioned resource exhaustion. | [Duke record and abstract](https://scholars.duke.edu/publication/755326), [author manuscript in NCSU repository](https://repository.lib.ncsu.edu/bitstreams/a5ae841a-8785-4031-8631-fcf3d1db8c0e/download). Cite conference year 1999, not the 2000 technical-report deposit. |
| 9 | Grottke et al. (2006): aging under controlled web-server workload. | [Duke record and abstract](https://scholars.duke.edu/publication/687928), author publication listing and author manuscript. |
| 10 | Nethercote and Seward (2007): instrumentation and shadow values. | [Original paper](https://valgrind.org/docs/valgrind2007.pdf), official Valgrind documentation, Crossref authors/pages/DOI. |
| 11 | Mitchell and Sevitsky (2003): ranking and tracking suspicious heap structures. | [Springer chapter metadata and abstract](https://link.springer.com/chapter/10.1007/978-3-540-45070-2_16). Full subscription text not accessed. |
| 12 | Jump and McKinley (2007): garbage-collector-assisted growth diagnosis. | [Author publication listing](https://www.cs.utexas.edu/~mckinley/papers.html), [extended technical report](https://www.cs.utexas.edu/ftp/techreports/tr06-07.pdf) and Crossref conference metadata. Conference paper and report counted once. |
| 13 | Weninger et al. (2020): heap-evolution visualizations. | Local original paper and [Eurographics publisher record](https://diglib.eg.org/items/a44a0f98-e747-4540-8259-8a4bbd38c5e6/full). Authors, year, pages 63-75 and DOI checked. |
| 14 | Beneder et al. (2014): runtime telemetry on embedded Linux. | Local original paper, [author institution's publication list](https://embsys.technikum-wien.at/projects/vecs/publications/publications.php), Crossref metadata. Correct conference/year/authors for IEEE document 7005223. |
| 15 | Lou et al. (2022): detection, diagnosis and mitigation in production. | [USENIX record, abstract and BibTeX](https://www.usenix.org/conference/osdi22/presentation/lou-resin), original paper. No production benefit claimed for our prototype. |
| 16 | Box, Jenkins and Reinsel (2008): statistical forecasting foundations. | [Wiley fourth-edition record](https://onlinelibrary.wiley.com/doi/book/10.1002/9781118619193) and Crossref metadata. This DOI is the 2008 fourth edition with three authors, not the 2015 fifth edition. |
| 17 | Hyndman and Athanasopoulos (2021): meaningful simple benchmarks. | [Author/publisher book](https://otexts.com/fpp3/), especially [simple methods](https://otexts.com/fpp3/simple-methods.html). Original book year and online access date distinguished. Our OLS trend is not asserted to equal the book's endpoint drift rule. |
| 18 | Hochreiter and Schmidhuber (1997): LSTM foundations. | [Publisher record](https://direct.mit.edu/neco/article/9/8/1735/6109/Long-Short-Term-Memory) and [original author-hosted article](https://www.bioinf.jku.at/publications/older/2604.pdf). |
| 19 | Gers, Schmidhuber and Cummins (2000): forget gate. | [MIT Press record and abstract](https://direct.mit.edu/neco/article/12/10/2451/6415/Learning-to-Forget-Continual-Prediction-with-LSTM). |
| 20 | Zhang (2003): hybrid linear/nonlinear forecasting rationale. | [Publisher abstract and article excerpts](https://www.sciencedirect.com/science/article/pii/S0925231201007020). This is ARIMA-ANN, not ARIMA-LSTM. |
| 21 | Samal and Kumar (2025): hybrid ARIMA-LSTM for software faults. | [Springer metadata and abstract](https://link.springer.com/article/10.1007/s13198-025-02743-2). Full subscription text unavailable; do not add unverified architecture details or compare its scores with our memory task. |
| 22 | Battisti et al. (2022): hybrid aging forecasts. | [Publisher article](https://www.mdpi.com/2076-3417/12/13/6412), abstract, introduction and model section. Moving-average plus Conv-LSTM, not our single-layer LSTM. |
| 23 | Zeng et al. (2023): strong simple baselines despite model complexity. | [AAAI publication and abstract](https://ojs.aaai.org/index.php/AAAI/article/view/26317). Published proceedings cited, not the separate 2022 arXiv version. Do not transfer its long-horizon rankings to our task. |
| 24 | Mann (1945): rank-based trend foundation. | [Publisher-deposited Crossref metadata](https://api.crossref.org/works/10.2307/1907187) and original-article excerpt; contextual treatment checked in Hamed and Rao. JSTOR full text was not accessible. No new theorem or implementation claimed. |
| 25 | Sen (1968): pairwise-slope alternative to OLS. | [Publisher-deposited Crossref metadata](https://api.crossref.org/works/10.1080/01621459.1968.10480934) and original-article abstract excerpt. Publisher full text was not accessible. |
| 26 | Hamed and Rao (1998): autocorrelation affects trend-test behavior. | [Publisher record and abstract](https://www.sciencedirect.com/science/article/pii/S002216949700125X). The hydrological application supplies a statistical caution, not evidence of OS leak accuracy. |
| 27 | Tashman (2000): forecast origins and temporal evaluation choices. | [Publisher abstract and article excerpts](https://www.sciencedirect.com/science/article/pii/S0169207000000650). |
| 28 | Bergmeir, Hyndman and Koo (2018): conditional validity of autoregressive cross-validation. | [Publisher article](https://www.sciencedirect.com/science/article/pii/S0167947317302384) and [author manuscript](https://robjhyndman.com/papers/cv-wp.pdf). Do not claim all random cross-validation is always invalid. |
| 29 | Albelali and Ahmed (2025): sequence construction and leakage. | [arXiv record and abstract](https://arxiv.org/abs/2512.06932). Preprint explicitly labeled. Review 1 entries 4 and 10 describe the same work and count once. |
| 30 | Kapoor and Narayanan (2023): leakage and scientific claims. | [Published Patterns article](https://www.sciencedirect.com/science/article/pii/S2666389923001599) and authors' Princeton project. Cite the journal version rather than counting the preprint separately. |
| 31 | Hyndman and Koehler (2006): forecast metric interpretation. | [Publisher article](https://www.sciencedirect.com/science/article/pii/S0169207006000239), [author manuscript](https://robjhyndman.com/papers/mase.pdf) and Crossref bibliographic details. MASE is discussed in the source but is not claimed as implemented here. |
| 32 | Saito and Rehmsmeier (2015): precision-recall under imbalance. | [PLOS article and citation](https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0118432). Supports the relevance of precision/recall; it does not make precision invariant to prevalence. |
| 33 | Tatbul et al. (2018): interval-aware anomaly evaluation. | [NeurIPS publication and abstract](https://proceedings.neurips.cc/paper/2018/hash/8f468c873a32bb0619eaeb2050ba45d1-Abstract.html), original paper introduction. Our event scoring is distinct from its full framework. |
| 34 | Kim et al. (2022): misleading point adjustment. | [AAAI publication and abstract](https://ojs.aaai.org/index.php/AAAI/article/view/20680). Venue is AAAI, not CVPR. |
| 35 | Wu and Keogh (2023): benchmark quality and inflated progress. | [IEEE publication record and abstract](https://ieeexplore.ieee.org/document/9537291/), original arXiv abstract. Journal issue is 2023; online publication is 2021; preprint is 2020. One work counted. |
| 36 | Schmidl, Wenig and Papenbrock (2022): broad detector evaluation. | [Original PVLDB paper](https://vldb.org/pvldb/vol15/p1779-wenig.pdf), first-page citation and Crossref DOI/page metadata. |

## Corrections to the Review 1 bibliography

- Entry 1's IEEE URL identifies Beneder et al.'s embedded Linux paper, not the listed C/C++ SCAM paper. The corrected work appears as paper reference 14.
- Entry 3 is retained as paper reference 2 with complete bibliographic details.
- Entries 4 and 10 are consolidated as reference 29, with verified authors and arXiv identifier.
- Entries 6 and 7 are tutorials. The survey instead cites the original trend-method literature and an autocorrelation study; these methods remain unimplemented.
- Entry 9's DOI resolves to Samal and Kumar's 2025 software-reliability paper. Its title and authors are corrected in reference 21.
- Entry 12 is retained as reference 22, with its actual hybrid components identified.
- Entry 13 is retained as reference 1, with the source's actual title and authors.
- Entry 16 is retained as reference 15 using the USENIX publication record.
- Other original entries are not counted toward the 36 unless independently verified and used. The remaining uncertain thesis/URL mappings and uncited sources may be revisited if needed; they are not declared nonexistent.

## Scope of the survey

This is a focused narrative survey, not a systematic review or a claim of exhaustive coverage. The Research Gap and Problem Statement reuse the verified sources to motivate a bounded empirical evaluation question; they do not assert that prior work has never combined forecasting and leak detection. Proposed Methodology reuses existing citations and was checked against the implementation and protocols, as recorded in DRAFTING_NOTES.md. No new experimental results were generated in these drafting steps. Later sections must preserve the verified Colab results and separately identify unperformed work.
