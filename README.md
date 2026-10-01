# Agentic Database Reconstruction

## Introduction

The Agentic Database Reconstruction project is to serve as part of a masters thesis titled "Automated Ontology Construction For Explainable Feature Discovery In Alloy Corrosion Resistance".

The overall goal of the thesis is to develop an agentic framework capable of autonomously building a structured dataset of alloy corrosion metrics and environmental parameters, then develop machine learning models and heuristics to identify the impact that each parameter has on an alloy's corrosion resistance, and on pitting potential in particular.

## Background

### Electrochemical metrics for corrosion resistant alloys

In 2021, Citrine Informatics published the paper [Electrochemical metrics for corrosion resistant alloys](../2021 - Nyby.pdf), in which they describe the construction of a hand-crafted database of alloy corrosion metrics and environmental parameters derived from an archive of 85 research papers in materials science.

This database has been downloaded and placed in [CRA_database_Scientific_Data_Publication_12102020.xlsx](./citrine_database/CRA_database_Scientific_Data_Publication_12102020.xlsx). The particular spreadsheet of interest, "pitting potential", is saved in csv format as [pitting_potential.csv](./citrine_database/pitting_potential.csv).

Most of the original research papers have been obtained in pdf format and saved under [papers](./papers). They are named according to the format `{reference_number}_{paper_name}.pdf` where `reference_number` corresponds to the `Reference` column in the pitting_potential spreadsheet and csv, thereby identifying the source of each record in the Citrine database.

### Deep learning framework for uncovering compositional and environmental contributions to pitting resistance in passivating alloys

In 2022, Sasidhar and collaborators at the Max Planck Institute for Sustainable Materials published [Deep learning framework for uncovering compositional and environmental contributions to pitting resistance in passivating alloys](../2022 - Sasidhar.pdf), in which they trained a deep neural network on the numerical & categorical features of the Citrine database to predict pitting potential. A multi-dimensional gradient descent was then applied over the trained DNN to systematically search the input feature space and find conditions or compositions that maximize pitting resistance.

### Enhancing corrosion-resistant alloy design through natural language processing and deep learning

In 2023, Sasidhar and collaborators published [Enhancing corrosion-resistant alloy design through natural language processing and deep learning](../2023 - Sasidhar.pdf), in which they build on their earlier work to develop a "Process Aware DNN" that makes use of an NLP pipeline to transform the textual columns from the Citrine database (namely "Test Methods", "Heat Treatment", "Scan Rate", and "Comments") into a feature vector that the neural network can train on.

They found that incorporating this additional information significantly improved prediction accuracy compared to the baseline results of their earlier 2022 paper.

This paper also explores a "Feature Transformed DNN" in which the compositional parameters of the alloys have been transformed into a set of different descriptors making use of different atomic, physical, and chemical properties of the constituent elements. This allows the model to generalize over alloy compositions involving elements not seen during training. Unlike the "Process Aware DNN", however, this model does not make use of the textual input. 

## Repository Structure

### Folders:

* `citrine_database/`: Contains the original corrosion resistance database (CRA_database_Scientific_Data_Publication_12102020.xlsx) along with the pitting potential spreadsheet from that database saved as a csv (pitting_potential.csv).

* `papers/`: Contains the corpus of literature, in pdf format, from which the Citrine database was created.

* `series_extractions/`: The output of the `extract-series` skill applied to the corpus of literature. The schema used for the json files is locaed under `.agents/skills/extract-series/references/seriese_extraction.schema.json`. 

### Agent Skills:

* `extract-series`: Identifies all plots and tables that record pitting potential along with other metrics. These are saved as a series of datapoints (list of rows) in json format. The "pitting potential" column is marked as the target value.


## Current Goals:

- [ ] Develop a set of agent skills capable of reliably and autonomously reconstructing the Citrine pitting potential dataset from the literature in `papers/`. 

    + Every piece of data must be directly traceable to its source - not merely to the paper its from, but to the precise figure or quote from the paper's text. This will help to ensure accurate extraction. 

    + The system will first generate an unnormalized database containing the raw values as cited in the papers, in their original units. Deterministic python scripts will then be used to convert all values into consistent units.  

- [ ] Extend the framework to identify and record additional metrics/details related to pitting potential that is mentioned in the papers, but was not included in the Citrine database. A meta-ontology such as [GEMD](https://citrineinformatics.github.io/gemd-docs/) may be used to record this information if data sparsity makes a tabular format unsuitable. 

- [ ] Develop machine learning models and heuristics to quantify the effect that each extracted feature has on the pitting potential, in an attempt to explain the causes and factors that impact alloy corrosion resistance.
