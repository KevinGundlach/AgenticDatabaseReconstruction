# Agentic Database Reconstruction

## Introduction

The Agentic Database Reconstruction project is to serve as part of a masters thesis titled "Automated Ontology Construction For Explainable Feature Discovery In Alloy Corrosion Resistance".

The overall goal of the thesis is to develop an agentic framework capable of autonomously building a structured dataset of alloy corrosion metrics and environmental parameters, then develop machine learning models and heuristics to identify the impact that each parameter has on an alloy's corrosion resistance, and on pitting potential in particular.

## Background

### Electrochemical metrics for corrosion resistant alloys

In 2021, Citrine Informatics published the paper [Electrochemical metrics for corrosion resistant alloys](https://www.nature.com/articles/s41597-021-00840-y), in which they describe the construction of a hand-crafted database of alloy corrosion metrics and environmental parameters derived from an archive of 85 research papers in materials science.

This database has been downloaded and placed in [CRA_database_Scientific_Data_Publication_12102020.xlsx](./citrine_database/CRA_database_Scientific_Data_Publication_12102020.xlsx). The particular spreadsheet of interest, "pitting potential", is saved in csv format as [pitting_potential.csv](./citrine_database/pitting_potential.csv).

Most of the original research papers have been obtained in pdf format and saved under [papers](./papers). They are named according to the format `{reference_number}_{paper_name}.pdf` where `reference_number` corresponds to the `Reference` column in the pitting_potential spreadsheet and csv, thereby identifying the source of each record in the Citrine database.

### Deep learning framework for uncovering compositional and environmental contributions to pitting resistance in passivating alloys

In 2022, Sasidhar and collaborators at the Max Planck Institute for Sustainable Materials published [Deep learning framework for uncovering compositional and environmental contributions to pitting resistance in passivating alloys](https://www.nature.com/articles/s41529-022-00281-x), in which they trained a deep neural network on the numerical & categorical features of the Citrine database to predict pitting potential. A multi-dimensional gradient descent was then applied over the trained DNN to systematically search the input feature space and find conditions or compositions that maximize pitting resistance.

### Enhancing corrosion-resistant alloy design through natural language processing and deep learning

In 2023, Sasidhar and collaborators published [Enhancing corrosion-resistant alloy design through natural language processing and deep learning](https://www.science.org/doi/full/10.1126/sciadv.adg7992), in which they build on their earlier work to develop a "Process Aware DNN" that makes use of an NLP pipeline to transform the textual columns from the Citrine database (namely "Test Methods", "Heat Treatment", "Scan Rate", and "Comments") into a feature vector that the neural network can train on.

They found that incorporating this additional information significantly improved prediction accuracy compared to the baseline results of their earlier 2022 paper.

This paper also explores a "Feature Transformed DNN" in which the compositional parameters of the alloys have been transformed into a set of different descriptors making use of different atomic, physical, and chemical properties of the constituent elements. This allows the model to generalize over alloy compositions involving elements not seen during training. Unlike the "Process Aware DNN", however, this model does not make use of the textual input. 

## Repository Structure

### Folders:

* `citrine_database/`: Contains the original corrosion resistance database (CRA_database_Scientific_Data_Publication_12102020.xlsx) along with the pitting potential spreadsheet from that database saved as a csv (pitting_potential.csv).

* `papers/`: Contains the corpus of literature, in pdf format, from which the Citrine database was created.

* `mineru_output/`: The [MinerU](https://opendatalab.github.io/MinerU/) utility was used to parse each research paper, the output of which is placed in this folder. Each subfolder is named according to `paper_{reference_number}/`. 

* `pitting_potential_plots/images`: Contains jpg files of all of the figures that represent plots of "pitting potential" vs. another metric, along with corresponding metadata (e.g, figure captions). This information comes from the `MinerU` output and the `classify-pitting-plots` agent skill.

* `pitting_potential_plots/tabularized`: Contains the output of the `tabularize-plots` skill applied to each of the figures in `pitting_potential_plots/images`.

* `schemas/digitized_pitting_potential_plot.schema.json` A complete schema with descriptions of the json files output by the `tabularize-plots` skill.

* `corrosion_tables/images`: Staging area for table images classified as processable, paired with source and catalog metadata sidecars.

* `corrosion_tables/tabularized`: Contains source-faithful structured JSON produced by the `parse-corrosion-tables` skill.

* `schemas/digitized_corrosion_table.schema.json`: Canonical schema for parsed corrosion tables, including merged cells, raw and parsed values, and hierarchical header links.

### Agents:

* `classify_pitting_plots`: Traverses the parsed images of all papers in the `mineru_output` folder, identifying those figures which represent plots of pitting potential vs. another metric. It's these figures from which much of the information in the Citrine Database was derived. Results are saved to `paper_{reference_number}_charts.json` and `paper_{reference_number}_simple_plots.json`.

* `tabularize-plots`: Takes every image identified by `classify_pitting_plots` and converts every plotted datapoint into tabular/json form, along with properly identifying axes and separately labeled series within each plot.

* `catalog-corrosion-tables`: Inventories every MinerU table in a paper, preserves its structured source context, classifies its purpose and processability, maps visible headers to Citrine fields, and stages processable images.

* `parse-corrosion-tables`: Reconstructs staged table images into schema-compliant JSON while preserving physical cell spans, exact visible text, conservative parsed values, footnotes, and row/column header relationships.

## Current Goals:

- [ ] Develop a set of agent skills capable of reliably and autonomously reconstructing the Citrine pitting potential dataset from the literature in `papers/`. 

    + Every piece of data must be directly traceable to its source - not merely to the paper its from, but to the precise figure or quote from the paper's text. This will help to ensure accurate extraction. 

    + The system will first generate an unnormalized database containing the raw values as cited in the papers, in their original units. Deterministic python scripts will then be used to convert all values into consistent units.  

- [ ] Extend the framework to identify and record additional metrics/details related to pitting potential that is mentioned in the papers, but was not included in the Citrine database. A meta-ontology such as [GEMD](https://citrineinformatics.github.io/gemd-docs/) may be used to record this information if data sparsity makes a tabular format unsuitable. 

- [ ] Develop machine learning models and heuristics to quantify the effect that each extracted feature has on the pitting potential, in an attempt to explain the causes and factors that impact alloy corrosion resistance.
