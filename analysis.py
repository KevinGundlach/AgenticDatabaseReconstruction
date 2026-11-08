import utils.postgres as pg 
import os 
import json 
import pandas as pd 
import re 
from utils.traversal import fill_measurement_objects

def load_pitting_potential_csv():
    
    df = pd.read_csv(
        "citrine_database/pitting_potential_complete.csv",
        encoding="utf-8",
        keep_default_na=False,
        na_values=["", "NA"],
    )

    pitting_potential_dataset = (
        df.astype(object)
        .where(df.notna(), None)
        .to_dict(orient="records")
    )

    return pitting_potential_dataset


def load_json_files(folder, filter=None):

    if filter is None:
        filter = lambda x: True

    json_files = [
        os.path.join(folder, f) 
        for f in os.listdir(folder) 
        if f.endswith('.json') and filter(f)]

    objects = []

    for fname in json_files:
        with open(fname, 'r', encoding='utf-8') as f:
            obj = json.load(f)
            objects.append(obj)

    return objects 


def import_data():

    pitting_potential_dataset = load_pitting_potential_csv()
    
    observation_registry = load_json_files('observation_registry', lambda f: f.startswith('paper_9'))
    observation_matches = load_json_files('observation_matches', lambda f: f.startswith('paper_9'))

    measurement_paths = [
        ".observations.locations.conditions.value",
        ".observations.locations.coordinates.value"
    ]

    fill_measurement_objects(observation_registry, measurement_paths)
    
    datasets = {
        "citrine": pitting_potential_dataset,
        "observation_registry": observation_registry,
        "observation_matches": observation_matches,
    }

    pg.recreate_and_insert_many(datasets, "agenticdb")


def identify_missing_papers():

    existing_papers = os.listdir('papers')

    for i in range(len(existing_papers)):
        existing_papers[i] = int(re.match(r"(\d+)_.*", existing_papers[i]).group(1))
    
    existing_papers = set(existing_papers)
    citrine_papers = set(row['Reference'] for row in load_pitting_potential_csv())
    all_papers = set(range(1, 86))
    missing_papers = all_papers.difference(existing_papers)
    missing_citrine_papers = citrine_papers.difference(existing_papers)

    print(missing_papers)
    print(missing_citrine_papers)


def count_records_by_reference():
    
    dataset = load_pitting_potential_csv() 
    records_by_reference = {}
    
    for row in dataset:

        if row['Reference'] not in records_by_reference:
            records_by_reference[row['Reference']] = 0

        records_by_reference[row['Reference']] += 1

    reference_count_list = list(records_by_reference.items())
    count_reference_list = [(c,r) for (r,c) in reference_count_list]
    count_reference_list.sort(reverse=True)
    print(count_reference_list)


def split_pitting_potential_csv():

    dataset = load_pitting_potential_csv()

    dataset_by_reference = {}

    for row in dataset:

        ref = row['Reference']
        
        if ref not in dataset_by_reference:
            dataset_by_reference[ref] = []

        dataset_by_reference[ref].append(row)

    references = sorted(dataset_by_reference)

    for ref in references:
        subset = dataset_by_reference[ref]
        subset = pd.DataFrame(subset)
        subset.to_csv(f'citrine_database\\by_reference\\pitting_potential_{ref}.csv', index=False)


def main():
    import_data()

if __name__ == "__main__":
    main()
    print("Done!")

