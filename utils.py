import pandas as pd
import networkx as nx
from thefuzz import fuzz
from multiprocessing import Pool, cpu_count
import pandas as pd
from pathlib import Path
from thefuzz import process, fuzz
from collections import Counter
from config import output_dir, master_list_path, similarity_threshold, master_match_threshold, enable_fallback_clustering,final_output
import re
from pathlib import Path
from datetime import datetime
from config import output_dir, master_list_path, similarity_threshold, master_match_threshold, enable_fallback_clustering, final_output


def clean_company_name(text: str) -> str:
    """Cleans and standardizes a company name for better matching."""
    if not isinstance(text, str): return ""
    text = text.lower()
    suffixes = [
        'pharmaceuticals', 'pharma', 'laboratories', 'labs', 'healthcare',
        'solutions', 'therapeutics', 'diagnostics', 'sciences', 'biopharma',
        'biosciences', 'international', 'global', 'operations', 'generics',
        'gmbh', 'ltd', 'inc', 'llc', 'corp', 'ag', 'plc', 'bv', 's.a', 'pte',
        'usa', 'us', 'ireland', 'uk', 'eu', 'corp', 'co', 'holding', 'holdings'
    ]
    suffix_pattern = r'\b(' + r'|'.join(suffixes) + r')\b'
    text = re.sub(suffix_pattern, '', text, flags=re.IGNORECASE)
    text = re.sub(r'[^\w\s]', '', text)
    return ' '.join(text.split())

def get_timestamped_filepath(output_dir: Path, filename_prefix: str, extension: str) -> Path:
    """Creates a timestamped filename to avoid overwriting results."""
    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    filename = f"{filename_prefix}_{timestamp}.{extension}"
    return output_dir / filename

# clusterer = EntityClusterer(config)


def load_csv(file_path):
    df = pd.read_csv(file_path)
    ## name the column as original name
    df.dropna(subset=['original_name'], inplace=True)
    df['original_name'] = df['original_name'].astype(str)
    return df

def load_master_list(master_list_path) -> pd.DataFrame | None:
        """Loads the existing master list if it exists."""
        try:
            return pd.read_excel(master_list_path)
        except Exception as e:
            raise IOError(f"Failed to read master list Excel file: {e}")
        
### resolver ####

## resolver utils:

def not_seen_records(source_df, master_df):
    """Filters source data to find records not in the master list."""
    master_originals = set(master_df['original_name'])
    notseen_df = source_df[~source_df['original_name'].isin(master_originals)].copy()
    print(f"Found {len(notseen_df)} new/unseen records to process.")
    return notseen_df

def map_the_master(notseen_df, master_df):
    """Tries to map unseen records to existing canonical names in the master list."""
    print("Attempting to map new records to existing master canonicals...")
    master_canonicals = master_df['canonical_name'].unique()
    threshold = int(master_match_threshold)
    
    mappings = {}
    for name in notseen_df['original_name']:
        match_result = process.extractOne(name, master_canonicals, scorer=fuzz.token_set_ratio, score_cutoff=threshold)
        if match_result:
            mappings[name] = match_result[0]

    mapped_df = notseen_df[notseen_df['original_name'].isin(mappings.keys())].copy()
    mapped_df['canonical_name'] = mapped_df['original_name'].map(mappings)
    
    remaining_df = notseen_df[~notseen_df['original_name'].isin(mappings.keys())].copy()
    print(f"Mapped {len(mapped_df)} records to master. {len(remaining_df)} records remain.")
    return mapped_df[['original_name', 'canonical_name']], remaining_df


def creating_canonical_map(df, clusters):
    """
    Selects the best canonical name for each cluster using improved logic.
    """
    cleaned_to_originals = df.groupby('cleaned_name')['original_name'].apply(list)
    original_name_counts = Counter(df['original_name'])
    canonical_map = {}
    
    for cluster in clusters:
        original_names_in_cluster = [name for cleaned_name in cluster for name in cleaned_to_originals.get(cleaned_name, [])]
        if not original_names_in_cluster: continue
        
        # *** NEW IMPROVED LOGIC ***
        # 1. Prioritize by frequency first.
        # 2. Use shortest length as a tie-breaker.
        
        # Count frequencies of original names within this cluster
        cluster_name_counts = Counter(original_names_in_cluster)
        
        # Find the maximum frequency
        max_freq = max(cluster_name_counts.values())
        
        # Get all candidates with the maximum frequency
        candidates = [name for name, freq in cluster_name_counts.items() if freq == max_freq]
        
        # If there's a tie in frequency, sort the tied candidates by length
        if len(candidates) > 1:
            candidates.sort(key=len)

        # The best candidate is the first one in the list
        if candidates:
            canonical_name = candidates[0]
            for original_name in set(original_names_in_cluster):
                canonical_map[original_name] = canonical_name
    return canonical_map



def correcting_new_entities(df):
    """Runs the full clustering and canonicalization process on a dataframe."""
    df_to_process = df.copy()
    df_to_process_cleaned = df_to_process[df_to_process['cleaned_name'] != ''].copy()
    
    clusters = cluster_finding(list(df_to_process_cleaned['cleaned_name'].unique()),similarity_threshold,2)
    
    canonical_map = creating_canonical_map(df_to_process_cleaned, clusters)
    
    df_to_process['canonical_name'] = df_to_process['original_name'].map(canonical_map)
    df_to_process['canonical_name'] = df_to_process['canonical_name'].fillna(df_to_process['original_name'])


def save_results(final_df):
    """Saves the final dataframe to the master list path."""
    final_df_deduped = final_df.drop_duplicates(subset=['original_name'], keep='last')
    final_df_sorted = final_df_deduped.sort_values(by=['canonical_name', 'original_name']).reset_index(drop=True)
    
    try:
        final_df_sorted.to_excel(final_output, index=False)
    except Exception as e:
        print(f"Error: Could not save results to '{final_output}'. {e}")        


#### clusering utils:

def find_pair_worker(args):
    chunk, all_names, threshold = args
    similar_pairs = []
    for name1 in chunk:
        for name2 in all_names:
            if name1 >= name2: continue
            score = fuzz.token_set_ratio(name1, name2)
            if score >= threshold:
                similar_pairs.append((name1, name2))
    return similar_pairs  


def cluster_finding(names_to_cluster,threshold,num_cores):
    num_cores=num_cores
    threshold = threshold

    if not names_to_cluster:
        return []

    if num_cores > 1 and len(names_to_cluster) > 500:
        print(f"Starting parallel clustering with {num_cores} cores...")
        chunk_size = max(1, len(names_to_cluster) // num_cores)
        chunks = [names_to_cluster[i:i + chunk_size] for i in range(0, len(names_to_cluster), chunk_size)]
        pool_args = [(chunk, names_to_cluster, threshold) for chunk in chunks]
        
        with Pool(processes=num_cores) as pool:
            results = pool.map(find_pair_worker, pool_args)
        all_similar_pairs = [pair for sublist in results for pair in sublist]
    else:
        print("Starting single-threaded clustering (dataset is small or cores=1)...")
        all_similar_pairs = find_pair_worker((names_to_cluster, names_to_cluster, threshold))

    print(f"Found {len(all_similar_pairs)} similar pairs. Building graph...")
    G = nx.Graph()
    G.add_nodes_from(names_to_cluster)
    G.add_edges_from(all_similar_pairs)
    
    clusters = list(nx.connected_components(G))
    print(f"Identified {len(clusters)} new clusters.")
    return clusters