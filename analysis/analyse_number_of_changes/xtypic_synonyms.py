import os

import pandas as pd

from WCVP_versions.updating_wcvp import get_all_databases
from analysis.analyse_number_of_changes.helper_functions import this_repo_path

def get_discrepancy_results_for_pair(folder, taxonomy_name:str):
    if taxonomy_name == 'wcvp':
        value_dir = os.path.join(this_repo_path, 'WCVP_versions', 'outputs', folder)
    if taxonomy_name == 'wfo':
        value_dir = os.path.join(this_repo_path, 'WFO_versions', 'outputs', folder)

    disagreements_df = pd.read_csv(os.path.join(value_dir, 'all_results.csv'), index_col=0)
    return disagreements_df

def main():
    v10_taxa, v11_taxa, v12_taxa, v13_taxa, v14_taxa = get_all_databases()

    folder = 'v10_v14'
    discrepancy_results = get_discrepancy_results_for_pair(folder, 'wcvp')
    v10_where_discrepancies_arise = v10_taxa[v10_taxa['taxon_name_w_authors'].isin(discrepancy_results['taxon_name_w_authors'].values)]
    homoytpic_synonyms = v10_where_discrepancies_arise[v10_where_discrepancies_arise['homotypic_synonym'] == 'T']
    heteroytpic_synonyms = v10_where_discrepancies_arise[v10_where_discrepancies_arise['homotypic_synonym'] != 'T']
    assert len(homoytpic_synonyms) + len(heteroytpic_synonyms) == len(v10_where_discrepancies_arise)

    output_folder = os.path.join('outputs','wcvp',folder)
    homoytpic_synonyms.to_csv(os.path.join(output_folder, 'homoytpic_synonyms_in_v10_where_discrepancies_arise.csv'), index=False)
    homoytpic_synonyms.describe(include='all').to_csv(os.path.join(output_folder, 'homoytpic_synonyms_in_v10_where_discrepancies_arise_summary.csv'), index=False)
    heteroytpic_synonyms.to_csv(os.path.join(output_folder, 'heteroytpic_synonyms_in_v10_where_discrepancies_arise.csv'), index=False)
    heteroytpic_synonyms.describe(include='all').to_csv(os.path.join(output_folder, 'heteroytpic_synonyms_in_v10_where_discrepancies_arise_summary.csv'), index=False)

    results_from_homotypic_synonyms = discrepancy_results[discrepancy_results['taxon_name_w_authors'].isin(homoytpic_synonyms['taxon_name_w_authors'].values)]
    results_from_heterotypic_synonyms = discrepancy_results[discrepancy_results['taxon_name_w_authors'].isin(heteroytpic_synonyms['taxon_name_w_authors'].values)]
    assert len(results_from_homotypic_synonyms) + len(results_from_heterotypic_synonyms) == len(discrepancy_results)

    results_from_homotypic_synonyms.to_csv(os.path.join(output_folder, 'results_from_homotypic_synonyms.csv'), index=False)
    results_from_homotypic_synonyms.describe(include='all').to_csv(os.path.join(output_folder, 'results_from_homotypic_synonyms_summary.csv'), index=False)
    results_from_heterotypic_synonyms.to_csv(os.path.join(output_folder, 'results_from_heterotypic_synonyms.csv'), index=False)
    results_from_heterotypic_synonyms.describe(include='all').to_csv(os.path.join(output_folder, 'results_from_heterotypic_synonyms_summary.csv'), index=False)



if __name__ == '__main__':
    main()
