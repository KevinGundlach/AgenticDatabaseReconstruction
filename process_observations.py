import json 
import os
from pathlib import Path 
import models.observation_enrichment as reg
from pydantic import TypeAdapter
from typing import Literal, Tuple


def save_matched_observations(paper_reference_number):

    ref = paper_reference_number
    registry_file = Path('observation_registry', f'paper_{ref}.json')
    matches_file = Path('observation_matches', f'paper_{ref}.json')
    output_file = Path('observation_registry', f'paper_{ref}_matched_only.json')

    with open(registry_file, encoding='utf-8') as f:
        registry = json.load(f) 

    with open(matches_file, encoding='utf-8') as f:
        matches = json.load(f) 

    matched_observation_ids = set() 

    for obs in matches['observations']:
        if len(obs['matches']) > 0:
            matched_observation_ids.add(obs['observation_id'])

    registry['observations'] = [
        obs for obs in registry['observations']
        if obs['observation_id'] in matched_observation_ids
    ]

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(registry, f, indent=2)


def load_extraction(json_file) -> reg.ObservationEnrichment:

    with open(f"enrich-observations\\{json_file}", encoding="utf-8") as f:
        content = f.read()

    adapter = TypeAdapter(reg.ObservationEnrichment)
    extraction : reg.ObservationEnrichment = adapter.validate_json(content)

    return extraction



def main():

    paper_49_extraction = load_extraction('paper_49_matched_only.json')
    paper_3_extraction = load_extraction('paper_3_matched_only.json')
    paper_9_extraction = load_extraction('paper_9_matched_only.json')



if __name__ == "__main__":
    main()
    print("Done!")
