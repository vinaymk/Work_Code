from utils import load_csv,load_master_list,clean_company_name,not_seen_records
from pathlib import Path
from collections import Counter
from fuzzywuzzy import process, fuzz  
from config import output_dir, master_list_path, similarity_threshold, master_match_threshold, enable_fallback_clustering, final_output
from utils import load_csv, load_master_list, clean_company_name, not_seen_records,map_the_master,correcting_new_entities,creating_canonical_map, cluster_finding, save_results,find_pair_worker,cluster_finding
import pandas as pd


if __name__ == "__main__":
    # Load the source CSV file
    source_file_path = "C:/Users/FCI/Documents/My_Projects/Sponsor_Name_IQVIA/Input/regulatory_fda_202508181800.csv"
    source_df = load_csv(source_file_path)

    # Load the master list CSV file
    master_file_path = "C:/Users/FCI/Documents/My_Projects/Sponsor_Name_IQVIA/Input/master_list.xlsx"
    master_df = load_master_list(master_file_path)
    master_df = None

    source_df['cleaned_name'] = source_df['original_name'].apply(clean_company_name)
    if master_df is None:
            # --- First Run Logic ---
            print("\n--- Executing First Run ---")
            final_mapping = correcting_new_entities(source_df)
            print("In first run, output",len(final_mapping))
    else:        
        print("\n--- Executing Incremental Run ---")
        unseen_df = not_seen_records(source_df, master_df)
        
        if unseen_df.empty:
            print("No new records to process. Master list is up to date.")
            final_mapping = master_df
        else:
            mapped_to_master, remaining_df = map_the_master(unseen_df, master_df)
            
            if not remaining_df.empty and enable_fallback_clustering:
                print("\n--- Fallback: Clustering remaining records ---")
                newly_resolved = correcting_new_entities(remaining_df)
                final_mapping = pd.concat([master_df, mapped_to_master, newly_resolved], ignore_index=True)
            elif not remaining_df.empty:
                print("\n--- Fallback disabled: Labeling remaining as 'FOR_REVIEW' ---")
                remaining_df['canonical_name'] = 'FOR_REVIEW'
                final_mapping = pd.concat([master_df, mapped_to_master, remaining_df[['original_name', 'canonical_name']]], ignore_index=True)
            else:
                final_mapping = pd.concat([master_df, mapped_to_master], ignore_index=True)

    # --- Save Final Results ---
    save_results(final_mapping)



