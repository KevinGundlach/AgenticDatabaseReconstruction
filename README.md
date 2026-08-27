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




