# Project Guidelines & Agent Instructions

## Project Overview

This project focuses on the automated, end-to-end extraction and digitization of materials science data from academic literature. It originates from the landmark study published in *Nature Scientific Data*:
> **Reference Paper:** *A database of alloy corrosion information curated from literature*  
> **Source:** [Nature Scientific Data (2021) 8:840](https://www.nature.com/articles/s41597-021-00840-y)  
> **Originators:** Researchers from Citrine Informatics.

In that study, domain experts manually reviewed dozens of research papers on corrosion-resistant alloys (CRAs) and extracted extensive experimental corrosion data into the Citrine database (`citrine_database/CRA_database_Scientific_Data_Publication_12102020.xlsx`). A key component of this dataset is the pitting corrosion sheet, exported as `citrine_database/pitting_potential.csv`.

Because this dataset was created entirely through manual human labor, the curation process was labor-intensive, time-consuming, expensive, and subject to human error and selective extraction.

---

## Project Goals

1. **Autonomous Reconstruction (Primary Goal):**  
   Design and implement an autonomous, agentic multi-modal pipeline capable of reading the PDF research papers in `/papers/` and reconstructing the `pitting_potential.csv` dataset with high accuracy and fidelity relative to the ground-truth annotations.

2. **Multi-Modal Extraction (Text + Tables + Figures):**  
   Scientific papers convey critical data across multiple modalities:
   - **Text & Tables:** Nominal/measured alloy chemical compositions, heat treatments, microstructural classifications, scan rates, and solution specifications.
   - **Plots & Figures:** Many pitting potential ($E_{pit}$) values are not printed in tables or text; they must be visually extracted from polarization curves (e.g., current density vs. potential plots) or property scatter/line plots. Agents must leverage Vision-Language Models (VLMs) and computer vision techniques to tabularize these plots into structured numeric data.

3. **High Recall & Robustness:**  
   The pipeline should aim for comprehensive extraction. Extracting a superset of valid experimental data (capturing valid alloys or plots that human curators missed or excluded) is preferred over missing reported data.

4. **Generalization & Scale (Long-term Goal):**  
   Once the pipeline reliably matches the benchmark papers, extend the framework to ingest new, unseen literature to generate larger, high-value materials science datasets at near-zero marginal human cost.

---

## Repository Structure & Key Assets

- `papers/`: Contains the source literature PDFs. Each file is named with a prefix corresponding to its reference number in the ground-truth dataset (e.g., `1_J. Horvath...pdf`, `49_Malik, A. U., et al...pdf`, `80_G.S. Frankel...pdf`). References range from 1 to 85.

- `citrine_database/`:
  - `CRA_database_Scientific_Data_Publication_12102020.xlsx`: Original full multi-sheet Excel dataset from Citrine.
  - `pitting_potential.csv`: Ground-truth CSV for pitting potential experiments across all references.
  - `paper_<N>.csv`: Reference-filtered subsets of the ground truth (e.g., `paper_3.csv`, `paper_9.csv`, `paper_49.csv`, `paper_80.csv`) used for per-paper evaluation.
  
- `mineru_output/`:
    - MinerU was used to parse the collection of pdf papers. For each paper, the output of MinerU is as follows:
        - `{paper_name}.md`: The pdf contents converted into Markdown format. Tables are converted into HTML form embedded in the Markdown.
        - `{paper_name}_content_list.json`: A json document that classifies every parsed section of the pdf file.
        - `{paper_name}_content_list_v2.json`: Also a json document that classifies every parsed section of the pdf file, but classification is more granular. Different sections are classifies as "title", "paragraph", "page_header", "chart", "table", "equation" and so on.
        - `{paper_name}_layout.pdf`: The original pdf file, where every parsed section is highlighted in a different color.
        - `{paper_name}_middle.json`: Every line of the original pdf file parsed into a separate json object.
        - `{paper_name}_model.json`: Appears to just be a listing of the different parsed sections, without the content.
        - `{paper_name}_origin.pdf`: The original, unmodified pdf file that was parsed.
        - `{paper_name}_span.pdf`: The original pdf file with every line highlighted in red.
        - `images/`: A folder of all the plots/figures/tables from the pdf extracted as jpg images.
        
For the time being, only four representative papers are included:
    - `3_N. Pessall, J. I. Nurminen, Corrosion 30 (1974)_ p. 381..pdf`
    - `9_W. M. Carroll, E. E. Lynskey, Corros. Sci. 36 (1994)_ p. 1667.pdf`
    - `49_Malik, A. U., et al. Corrosion science 37.10 (1995)_ 1521-1535.pdf`
    - `80_G.S. Frankel, R.C. Newman, C.V. Jahnes, M.A. Russak, J Electrochem Soc, 140 (1993) 2192-2197.pdf`
    
Once we have the agentic extraction pipeline working correctly for these four papers, the pipeline will be adapted as needed to accommodate each of the other papers one by one.
   
---

## Ground Truth / Targets & Schema Specifications

The `citrine_database/pitting_potential.csv` file serves as the ground truth target schema. Any extracted row represents an alloy tested under a specific set of environmental and electrochemical conditions.

### Column Definitions

1. **Alloy Elemental Composition (wt%):**
   - Individual elemental columns (e.g., `Fe`, `Cr`, `Ni`, `Mo`, `W`, `N`, `Nb`, `C`, `Si`, `Mn`, `Cu`, `P`, `S`, `Al`, `V`, `Ta`, `Ti`, `Co`, etc.) specified in weight percent (wt%).
   - If an element is absent or trace, it is left empty or marked 0.

2. **Target Pitting Potential:**
   - `Avg. Epit, mV (SCE)`: The average/reported pitting potential in millivolts (mV) referenced against the Saturated Calomel Electrode (SCE).
   - `Min Epit, mV (SCE)` / `Max Epit, mV (SCE)`: Lower and upper bounds if the pitting potential is reported as an experimental range or error interval rather than a single discrete value.
   - *Note on Reference Electrodes:* If the paper reports potentials against other reference electrodes (e.g., SHE, Ag/AgCl, MSE), values must be converted to mV vs. SCE.

3. **Environmental & Solution Parameters:**
   - `Test Temp. C`: Temperature of the electrolyte solution in °C. If not explicitly mentioned, assume room temperature (~25 °C).
   - `Test Solution`: Textual chemical formulation of the electrolyte (e.g., `3.5% NaCl`, `0.1 M NaCl + 0.1 M Na2SO4`, `1N H2SO4 + 0.5N NaCl`).
   - `[Cl-] M`: Chloride ion molarity (mol/L). This is usually calculated/derived from the test solution composition rather than explicitly printed.
   - `pH`: Electrolyte pH. May be explicitly reported or calculated based on acid/base/salt concentrations.

4. **Electrochemical Procedure:**
   - `Test Method`: Procedure description (e.g., `potentiodynamic polarization`, `potentiostatic polarization`, `scratch test`, `galvanostatic`). Can be a whole paragraph text description if a paper provides additional details of a test procedure.  
   - `Scan Rate mV/s`: Potential sweep rate in mV/s for potentiodynamic polarization experiments.

5. **Material & Microstructural History:**
   - `Heat treatment`: Text description of prior thermal or mechanical processing (e.g., `solution annealed at 1050 C for 1h followed by water quench`, `as-cast`, `cold-rolled`).
   - `Microstructures`: Microstructural phase composition and morphology (e.g., `austenitic`, `ferritic`, `martensitic`, `duplex`, `amorphous`, `nano-crystalline`).
   - `Material class`: High-level category: `"Fe Alloy"`, `"NiCrMo Alloy"`, `"Al Alloy"`, `"HEA"`, or `"Other"`.

6. **Metadata & Notes:**
   - `Reference`: Integer identifier matching the PDF filename prefix in `/papers/` (1–85).
   - `Comments`: Annotations regarding specific alloy designations, sample conditions, or unusual experimental observations.

---

## Known Nuances & Discrepancies in the Ground Truth

When benchmarking agents against `pitting_potential.csv`, agents must account for human curation quirks and known ground-truth imperfections:

1. **Human Transcription & Annotation Errors:**
   - The manual database contains occasional human transcription errors. For example, in Paper 49 (Malik et al.), sulfur (S) concentrations in the database were entered 10× higher than the values actually printed in the paper.
   - Ground truth should be treated as a benchmark for comparison, but the ground truth text/numbers from the source PDF are the ultimate physical truth.

2. **Omissions & Selective Curation:**
   - Human curators often excluded certain alloys, figures, or data points. For instance, alloys lacking standardized UNS designations or commercial names (e.g., Remanit 4565/4575 in Paper 49) or specific alloy series in plots (e.g., Al-V, Al-Mn, Al-W curves from Figure 3 in Paper 80) were omitted from the database.
   - **Agent Policy:** The pipeline should extract all valid experimental data reported in the paper. Producing a superset of the ground truth is expected and encouraged; the agent should never skip valid data simply because a human curator omitted it.

3. **Assumed / Unstated Default Parameters:**
   - Papers frequently omit ambient conditions. Human curators imputed default values (e.g., room temperature = 25 °C, neutral aqueous solution pH = 7). Agents should recognize when parameters are unstated and apply standard domain defaults. As stated before, pH values might have to be calculated based on given acid/base/salt concentrations in the test solution.

4. **Cited & External Data in Datasets:**
   - In some cases (such as Paper 80), human curators included experimental rows that originated from earlier papers cited within the text (e.g., 14 rows with pH 10 from an earlier study by the same authors). Agents evaluating discrepancy reports should distinguish between native paper experiments and referenced external studies.

---

## Unit Normalization & Automated Python Computation

Source papers report measurements in diverse units that do not always match the target schema in `pitting_potential.csv`. The extraction pipeline must detect these unit mismatches and execute Python conversions to harmonize all data into standard schema units:

1. **Alloy Compositions (at.% $\leftrightarrow$ wt%):**
   - Many papers report alloy compositions in atomic percent (at.%) rather than weight percent (wt%), especially for sputtered films or binary/ternary model alloys.
   - The pipeline must convert at.% to wt% using IUPAC standard atomic weights:
     $$\text{wt\%}_i = \frac{x_i \cdot M_i}{\sum_j (x_j \cdot M_j)} \times 100$$
     (where $x_i$ is atomic fraction and $M_i$ is atomic molar mass in g/mol).

2. **Reference Electrodes ($E \rightarrow \text{mV vs. SCE}$):**
   - Potentials reported against SHE, NHE, Ag/AgCl, MSE ($Hg/Hg_2SO_4$), or other electrodes must be converted to mV vs. SCE using standard electrochemical potential offsets (e.g., $E_{\text{SCE}} \approx E_{\text{SHE}} - 241\text{ mV}$).

3. **Chloride Concentration ($[Cl^-]\text{ M}$):**
   - Concentrations given as wt% NaCl (e.g., 3.5% NaCl $\approx$ 0.6 M $Cl^-$), normality (N), or ppm must be converted into molarity (mol/L).

4. **Scan Rates & Temperatures:**
   - Scan rates in mV/min or V/h must be normalized to $\text{mV/s}$.
   - Temperatures in K or °F must be converted to °C.

5. **Test solution pH values**
   - If the pH value of a test solution is explicitly stated, use the reported value. If the pH value is not stated, but the precise chemical composition of the test solution is provided in sufficient detail that its pH value can be calculated, then report the calculated value.

6. **Composition 'Balance' Element**
   - If a given alloy composition lists one element as 'Balance', its value should be calculated by subtracting the values of all other elements from 100%. Generate an execute a Python function to perform this balance calculation.

---

## Multi-Modal Data Extraction Strategy

To achieve human-level accuracy, extraction agents should decompose the problem into modular stages:

1. **Entity & Context Extraction (Text & Tables):**
   - Identify alloy composition tables and map sample identifiers (e.g., "Alloy A", "316L", "Sample 1") to elemental wt% breakdowns.
   - Extract experimental conditions (solution chemistry, pH, temperature, scan rate, heat treatment) from the "Experimental Procedure" or "Materials and Methods" sections.

2. **VLM-Based Plot Digitization (Figures):**
   - Identify any figures that plot pitting potential ($E_{pit}$) vs. any relevant metric, such as alloy or test solution composition, test solution pH value, or ambient temperature. For example, Paper 80 (80_G.S. Frankel, R.C. Newman, C.V. Jahnes, M.A. Russak, J Electrochem Soc, 140 (1993) 2192-2197.pdf) includes several plots of pitting potential vs. concentrations of niobium, molybdenum, and chromium in aluminum alloys. Figure 9 of Paper 9 (9_W. M. Carroll, E. E. Lynskey, Corros. Sci. 36 (1994)_ p. 1667.pdf) plots pitting potential vs. pH value for several different metals in two different test solutions. 
   - Identify polarization curves and $E_{pit}$ trend plots from extracted figures.
   - Use multi-modal Vision-Language Models with specialized prompts to:
     - Identify axes, units, and scales (linear vs. log).
     - Locate breakdown/pitting potential inflection points ($E_{pit}$) for each curve/sample.
     - Tabularize the coordinates into structured CSV data.

3. **Data Synthesis & Unit Conversion:**
   - Generate and execute the necessary Python conversion scripts for composition (at.% to wt%), reference electrode offsets, $[Cl^-]\text{ M}$ molarity, pH values, and scan rates.
   - Align extracted $E_{pit}$ data points with corresponding alloy compositions and experimental parameters.
   - Categorize alloy into appropriate `Material class`.

4. **Validation & Benchmarking:**
   - Compare extracted records against the reference ground truth in `citrine_database/paper_<N>.csv`.
   - Compute metrics: match rate, precision, recall, and numerical error (MAE / RMSE on $E_{pit}$), accounting for known ground-truth nuances.

5. **Logging:**
    - For every extracted datapoint, add an entry in a log file. 
    - This entry should indicate whether the value was extracted verbatim from the paper, whether it was extracted but converted to different units, or whether it was calculated/derived from something else (e.g., such as if a pH value was calculated from a test solution composition rather than explicitly stated in the paper).
    - If any value exists in the ground truth dataset that cannot be found or derived from the source material - whether due to human transcription error, or the data having come from a different source - note this in the log.
