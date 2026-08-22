import os 
import json 
import shutil
from pathlib import Path 

# Goal: Find out how many images to tabularize.
ROOT_PATH = Path("mineru_output")

OUTPUT_PATH = Path("pitting_potential_plots")

def prep_output_path():

    os.makedirs(OUTPUT_PATH, exist_ok=True)

    for f in os.listdir(OUTPUT_PATH):
        os.remove(Path(OUTPUT_PATH) / f)
    

def main():

    prep_output_path()

    paper_folders = os.listdir(ROOT_PATH)

    for paper_name in paper_folders:
        paper_folder = ROOT_PATH / Path(paper_name)
        simple_plots_file = paper_folder / (paper_name + "_simple_plots.json")

        with open(simple_plots_file, encoding="utf-8") as fin:
            simple_plots_metadata = json.load(fin) 

        paper_reference = simple_plots_metadata['paper_reference']
        source_chart_manifest = simple_plots_metadata['source_chart_manifest']
        
        for plot_metadata in simple_plots_metadata['simple_plots']:

            chart_id = plot_metadata['chart_id']
            image_path = paper_folder / plot_metadata['image_path']

            output_image_path = OUTPUT_PATH / (paper_name + "_" + chart_id + ".jpg")
            shutil.copyfile(image_path, output_image_path)

            output_image_metadata_path = OUTPUT_PATH / (paper_name + "_" + chart_id + ".json")

            # TODO: maybe include the paper-level metadata as well.
            
            output_object = {
                'paper_reference': paper_reference,
                'source_chart_manifest': source_chart_manifest,
                'plot_metadata': plot_metadata,
                'plot_data': [],
            }

            with open(output_image_metadata_path, "w", encoding="utf-8") as fout:
                json.dump(output_object, fout, indent=4)
       

if __name__ == "__main__":

    pass 

    # papers = ['paper_2_', 'paper_3_', 'paper_4_']

    # files = [f for f in os.listdir('pitting_potential_plots')
    #          if any(f.startswith(p) for p in papers) and f.endswith('.jpg')]

    # for f in files:
    #     print(f)

    # main() 

