import json 
import os
from pathlib import Path 
from models.observation_enrichment import ObservationEnrichment, EnrichedExperiment, Measurement
from models.alignment import ObservationAlignment, ObservationMatch
from pydantic import TypeAdapter
from typing import List, Dict, Any
import pandas as pd 

from utils.weight_pct_conversion import get_alloy_units, to_weight_percent_strict, InvalidAlloyCompositionError
from collections import Counter
import utils.weight_pct_conversion as wpc

import re 
import os 



def load_enriched_observations() -> List[ObservationEnrichment]:

    documents = []

    for ref in range(100):

        filepath = f"enriched_observations\\paper_{ref}.json"

        if not os.path.isfile(filepath):
            continue

        with open(filepath, encoding="utf-8") as f:
            content = f.read()

        adapter = TypeAdapter(ObservationEnrichment)
        doc : ObservationEnrichment = adapter.validate_json(content)
        documents.append(doc)

    # Observation IDs can be reused for different papers
    # since the agent skills were run in batches.
    # Prefix them with the paper number to make them global. 
    
    for doc in documents:
        for exp in doc.experiments:
            exp.observation_id = f"{doc.reference_number}-{exp.observation_id}"

    return documents


def load_aligned_observations() -> List[ObservationAlignment]:

    documents = []

    for ref in range(100):

        filepath = f"matched_observations\\paper_{ref}.json"

        if not os.path.isfile(filepath):
            continue

        with open(filepath, encoding="utf-8") as f:
            content = f.read()

        adapter = TypeAdapter(ObservationAlignment)
        doc : ObservationAlignment = adapter.validate_json(content)
        documents.append(doc)

    # Observation IDs can be reused for different papers
    # since the agent skills were run in batches.
    # Prefix them with the paper number to make them global. 

    for doc in documents:
        for obs in doc.observations:
            obs.observation_id = f"{doc.reference_number}-{obs.observation_id}"

    return documents



def load_cra_records() -> List[Dict[str, Any]]:
    filepath = f"citrine_database\\pitting_potential_complete.csv"    
    dataframe = pd.read_csv(filepath)
    records = dataframe.to_dict(orient='records')
    return records



def print_basic_stats():

    enriched_documents = load_enriched_observations()
    aligned_documents = load_aligned_observations()
    cra_records = load_cra_records()

    docs_by_obs_id = {
        exp.observation_id:doc 
        for doc in enriched_documents
        for exp in doc.experiments
    }

    experiments_by_obs_id = {
        exp.observation_id : exp 
        for doc in enriched_documents   
        for exp in doc.experiments
    }

    matches_by_obs_id = {
        obs.observation_id : obs 
        for doc in aligned_documents
        for obs in doc.observations
    }

    cra_records_by_number = {
        row['No.'] : row 
        for row in cra_records 
    }

    print("Total Experiments:", len(experiments_by_obs_id))
    print("Total With Match Objects:", len(matches_by_obs_id))

    print("  Matched:", len([m for m in matches_by_obs_id.values() if m.status == 'matched']))

    print("    Number Matches Per Match Object", 
          set(len(m.matches) for m in matches_by_obs_id.values() if m.status == "matched"))

    print("    Number Candidates Per Match Object", 
          set(len(m.candidates) for m in matches_by_obs_id.values() if m.status == "matched"))

    
    print("  Unmatched:", len([m for m in matches_by_obs_id.values() if m.status == 'unmatched']))
    
    print("    Number Matches Per Match Object", 
          set(len(m.matches) for m in matches_by_obs_id.values() if m.status == "unmatched"))

    print("    Number Candidates Per Match Object", 
          set(len(m.candidates) for m in matches_by_obs_id.values() if m.status == "unmatched"))


    print("  Ambiguous:", len([m for m in matches_by_obs_id.values() if m.status == 'ambiguous']))

    print("    Number Matches Per Match Object", 
          set(len(m.matches) for m in matches_by_obs_id.values() if m.status == "ambiguous"))

    print("    Number Candidates Per Match Object", 
          set(len(m.candidates) for m in matches_by_obs_id.values() if m.status == "ambiguous"))


    cra_papers = set(row['Reference'] for row in cra_records)

    unmatched_papers = set(docs_by_obs_id[id].reference_number 
                        for id in experiments_by_obs_id
                        if id not in matches_by_obs_id)

    print("  All Others Excluded from CRA Records?", all(p not in cra_papers for p in unmatched_papers))
    
    # As a sanity check... all the matches are from the same papers, right?
    print("All Match Objects From Same Papers?",
        all(docs_by_obs_id[obs_id].reference_number == cra_records_by_number[m.citrine_no]['Reference']
            for obs_id in matches_by_obs_id 
            for m in matches_by_obs_id[obs_id].matches))

    print("All Candidate Objects From Same Papers?",
        all(docs_by_obs_id[obs_id].reference_number == cra_records_by_number[m.citrine_no]['Reference']
            for obs_id in matches_by_obs_id 
            for m in matches_by_obs_id[obs_id].candidates))

    cra_row_numbers = set(row['No.'] for row in cra_records)
    matched_cra_row_numbers = set(m.citrine_no for obs in matches_by_obs_id.values() for m in obs.matches)
    candidate_cra_row_numbers = set(m.citrine_no for obs in matches_by_obs_id.values() for m in obs.candidates)

    print("Total CRA Rows:", len(cra_row_numbers))

    print("  Unmatched CRA Rows:", 
          len(cra_row_numbers - matched_cra_row_numbers))
    
    print("  Unmatched CRA Rows (minus candidates):",
          len(cra_row_numbers - matched_cra_row_numbers - candidate_cra_row_numbers))

    known_papers = set(doc.reference_number for doc in enriched_documents)
    
    missing_papers = cra_papers - known_papers 
    missing_paper_cra_row_numbers = set(rec['No.'] for rec in cra_records if rec['Reference'] in missing_papers)
    known_cra_row_numbers = cra_row_numbers - missing_paper_cra_row_numbers

    print("  Number of CRA Rows From Missing Papers:", len(missing_paper_cra_row_numbers))

    matched_cra_row_numbers = set(m.citrine_no for obs in matches_by_obs_id.values() for m in obs.matches)
    candidate_cra_row_numbers = set(m.citrine_no for obs in matches_by_obs_id.values() for m in obs.candidates)

    print("  Unmatched (Known) CRA Rows:", 
          len(known_cra_row_numbers - matched_cra_row_numbers))
    
    print("  Unmatched (Known) CRA Rows (minus candidates):",
          len(known_cra_row_numbers - matched_cra_row_numbers - candidate_cra_row_numbers))

    print("Number Of Known Papers (From Enriched Observations):", len(known_papers))
    print("Number Of Missing Papers (With CRA Rows):", len(missing_papers))
    print("Missing Papers (With CRA Rows):", missing_papers)






def print_alloy_conversion_failure_counts(experiments : List[EnrichedExperiment]):
    
    success = 0 
    failed = 0
    total = 0 

    failure_counts = Counter()

    for exp in experiments:

        try:
            to_weight_percent_strict(exp.alloy)    
            success += 1
        except InvalidAlloyCompositionError as error:
            failed += 1 
            failure_counts[error.reason] += 1

        total += 1


    print(f"{total=}, {success=}, {failed=}")
    for reason, count in failure_counts.most_common():
        print(f"  {reason}: {count}") 



def print_unit_breakdown():

    enriched_documents = load_enriched_observations()
    aligned_documents = load_aligned_observations()
    experiments = [exp for doc in enriched_documents for exp in doc.experiments]
    
    matched_obs_ids = set(
        obs.observation_id for doc in aligned_documents for obs in doc.observations
        if obs.status == "matched"
    )

    matched_experiments = [exp for exp in experiments if exp.observation_id in matched_obs_ids]
    
    print("==== All Experiments ====")
    print_alloy_conversion_failure_counts(experiments)
    print()

    print("==== Matched Experiments Only ====")
    print_alloy_conversion_failure_counts(matched_experiments)
    print()


    print("==== Unit Breakdown ====")
    alloys = [exp.alloy for doc in enriched_documents for exp in doc.experiments]
    matched_alloys = [exp.alloy for exp in matched_experiments]

    unit_counter = Counter()
    other_units = set()

    for alloy in alloys:
        for element in alloy.composition:
            if hasattr(element.amount, 'unit'):
                if element.amount.unit in wpc.WEIGHT_PERCENT_UNITS:
                    unit_counter['weight %'] += 1
                elif element.amount.unit in wpc.ATOMIC_PERCENT_UNITS:
                    unit_counter['atomic %'] += 1
                elif element.amount.unit in wpc.ATOMIC_RATIO_UNITS:
                    unit_counter['atomic ratio'] += 1
                elif element.amount.unit is None or element.amount.unit == '':
                    unit_counter['(null unit)'] += 1
                else:
                    unit_counter['other'] += 1
                    other_units.add(element.amount.unit)
            elif element.amount == "balance":
                unit_counter['balance'] += 1
            elif element.amount is None:
                unit_counter['(null amount)'] += 1
            else:
                unit_counter['(missing unit attribute)'] += 1

    for unit_normalized, count in unit_counter.most_common():
        print(f"{unit_normalized}: {count}")

    print("Other Units:", other_units)
    print()

    print("==== Unit Breakdown Convertible / Matched Only Experiments ====")

    unit_counter.clear()

    for alloy in matched_alloys:
        for element in alloy.composition:
            if element.amount is None:
                unit_counter["(null amount)"] += 1
            elif element.amount == "balance":
                unit_counter["valid"] += 1
            elif hasattr(element.amount, "unit"):
                if (element.amount.unit in wpc.WEIGHT_PERCENT_UNITS or 
                    element.amount.unit in wpc.ATOMIC_PERCENT_UNITS or 
                    element.amount.unit in wpc.ATOMIC_RATIO_UNITS):
                    unit_counter["valid"] += 1
                elif (element.amount.unit in {'ppm', '% (foil purity)', 'nominal %', '%', '% (purity)', 'pct'}):
                    unit_counter["maybe"] += 1
            else:
                unit_counter["(unknown)"] += 1
        
    for value, count in unit_counter.most_common():
        print(f"{value}: {count}")




def get_known_papers():
    
    papers = os.listdir("papers") 
    
    reference_numbers = set(
        int(re.match(r"(\d+)_", p).groups()[0]) for p in papers
    )
    
    return sorted(reference_numbers)

    
def print_additional_stats():
    
    enriched_documents = load_enriched_observations()
    aligned_documents = load_aligned_observations()
    cra_records = load_cra_records()
    enriched_experiments = [exp for doc in enriched_documents for exp in doc.experiments]

    obsid_to_row = {}
    row_to_obsid = {} 

    for doc in aligned_documents:
        for obs in doc.observations:
            for match in obs.matches:

                if obs.observation_id not in obsid_to_row:
                    obsid_to_row[obs.observation_id] = []
                
                if match.citrine_no not in row_to_obsid:
                    row_to_obsid[match.citrine_no] = []

                obsid_to_row[obs.observation_id].append(match.citrine_no)
                row_to_obsid[match.citrine_no].append(obs.observation_id)

    papers_in_corpus = get_known_papers()

    cra_papers = set(row['Reference'] for row in cra_records)
    
    enrichment_papers = set(
        doc.reference_number 
        for doc in enriched_documents
        if len(doc.experiments) >= 1
    )

    # 810
    print("Total Number Of CRA Rows:", len(cra_records))
    
    # 2176
    print("Total Number Of Enriched Observations:", len(enriched_experiments))

    # 850
    print("Total Number Of Matched Enriched Observations:", len(obsid_to_row))
    
    # 667
    print("Total Number Of Matched CRA Records:", len(row_to_obsid))    

    # 35
    print("Total Number of CRA Records From Missing Papers:", len(
        [1 for row in cra_records if row['Reference'] not in papers_in_corpus]
    ))

    # 143
    print("Total Number Of Unmatched CRA Records:", len([
        1 for row in cra_records if row['No.'] not in row_to_obsid
    ]))

    # 108
    print("Total Number of Unmatched CRA Records From Corpus:", len([
        1 for row in cra_records 
        if row['No.'] not in row_to_obsid 
        and row['Reference'] in papers_in_corpus
    ]))

    # 3
    print("Number Of Papers (In Corpus) With CRA Records But No Registered Observations:", len(set(
        row['Reference'] for row in cra_records
        if row['Reference'] not in enrichment_papers
        and row['Reference'] in papers_in_corpus
    )))

    # [10, 33, 77]
    print("    These papers are:", sorted(set(
        row['Reference'] for row in cra_records
        if row['Reference'] not in enrichment_papers
        and row['Reference'] in papers_in_corpus
    )))

    # 8
    print("Number Of CRA Records From Papers (In Corpus) With No Registered Observations:", len([
        row for row in cra_records 
        if row['Reference'] not in enrichment_papers
        and row['Reference'] in papers_in_corpus
    ]))


    # I also need to figure out which CRA rows are matched with multiple observation IDs,
    # and which observation IDs are matched to multiple CRA rows.
    # Then I can more closely investigate what's going on.

    # 22
    print("Number of Enriched Observations With Multiple CRA Matches:", len([
        obsid for obsid in obsid_to_row
        if len(obsid_to_row[obsid]) > 1
    ]))

    # [
    #       '71-obs_001', '71-obs_003', '71-obs_005', '71-obs_007', '71-obs_009', 
    #       '71-obs_011', '71-obs_013', '71-obs_015', '71-obs_017', '71-obs_019', 
    #       '71-obs_021', '71-obs_023', '71-obs_025', '71-obs_027', '71-obs_029', 
    #       '71-obs_031', '71-obs_033', '71-obs_035', '71-obs_037', 
    # 
    #       '73-obs_001', '73-obs_004', '73-obs_005'
    # ]

    print("    These Observations Are:", sorted([
        obsid for obsid in obsid_to_row
        if len(obsid_to_row[obsid]) > 1
    ]))

    # 45
    print("Number of CRA Records With Multiple Observation Matches:", len([
        rownum for rownum in row_to_obsid
        if len(row_to_obsid[rownum]) > 1        
    ]))


    # Prefixed by paper number:
    #
    # [
    #   '1-333', 
    #   '2-402', 
    #   '3-430', '3-446', 

    #   '37-105', '37-106', '37-107', '37-108', '37-109', 
    #   '37-110', '37-111', '37-112', '37-113', '37-114', 
    #   '37-115', '37-116', '37-117', '37-118', '37-119', 
    #   '37-120', 
    
    #   '39-797', 
    #   '41-142', '41-143', '41-144', '41-145', '41-146', '41-147', 
    #   '56-700', '56-701', '56-702', '56-703', '56-705', '56-707', 
    #   '6-458', '6-460', '6-461', '6-462', '6-463', '6-464', '6-465', '6-466', '6-467', 
    #   '67-551', 
    #   '8-470', '8-474'
    # ]

    print("    These Records Are:", sorted([

        f'{row['Reference']}-{row['No.']}' 
        for row in cra_records 
        if row['No.'] in row_to_obsid
        and len(row_to_obsid[row['No.']]) > 1
    ]))
