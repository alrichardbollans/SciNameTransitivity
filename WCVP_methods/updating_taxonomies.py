import os

import pandas as pd
from pkg_resources import resource_filename
from wcvpy.wcvp_download import get_all_taxa, add_authors_to_col
from wcvpy.wcvp_name_matching import get_genus_from_full_name

repo_path = os.environ.get('KEWSCRATCHPATH')
this_repo_path = os.path.join(repo_path, 'TaxoDrift')
_output_path = os.path.join(this_repo_path, 'WCVP_methods', 'outputs')
_input_path = os.path.join(this_repo_path, 'WCVP_methods', 'inputs')

if not os.path.isdir(_output_path):
    os.mkdir(_output_path)


def get_accepted_name_from_record(record: pd.DataFrame, reported_name: str):
    if len(record.index) == 0:
        print(f'{reported_name} has no taxon record')
        raise ValueError
    else:
        accepted_names = record['accepted_name_w_author'].dropna().unique().tolist()

        if len(set(accepted_names)) > 1:
            print(f'{reported_name} resolves to more than one taxon record')
            print(record)
            print(accepted_names)
            raise ValueError
        if len(accepted_names) == 1:
            return accepted_names[0]
        else:
            return None


def chain_two_databases(older_taxa_version: pd.DataFrame, newer_taxa_version: pd.DataFrame, old_tag: str, new_tag: str, out_dir: str):
    # Pick non-duplicated names
    unique_names = older_taxa_version['taxon_name_w_authors'].dropna().unique().tolist()

    # Collect the records in the old and new database directly
    # relevant records
    v12_records = older_taxa_version[older_taxa_version['taxon_name_w_authors'].isin(unique_names)][
        ['taxon_name_w_authors', 'accepted_name_w_author']]
    v12_records = v12_records.dropna(subset=['accepted_name_w_author'])
    v12_records = v12_records.drop_duplicates(keep='first')
    v12_records = v12_records.drop_duplicates(subset=['taxon_name_w_authors'],
                                              keep=False)  # Ignore cases with multiple resolutions, as these are ambiguous anyway
    # I think Cubeba Raf. and Lamottea Pomel are examples but they are less interesting for this analysis
    if out_dir is not None:
        v12_records = v12_records.rename(
            columns={'accepted_name_w_author': old_tag + '_accepted_name_w_author'})
        v12_records.describe(include='all').to_csv(os.path.join(out_dir, old_tag + '_old_records_summary.csv'))

    # accepted names in old database
    relevant_v13_names_for_chaining = v12_records[old_tag + '_accepted_name_w_author'].dropna().unique().tolist()
    # names in new database where taxon name is accepted name in old database
    v13_records_for_chaining = newer_taxa_version[newer_taxa_version['taxon_name_w_authors'].isin(relevant_v13_names_for_chaining)][
        ['taxon_name_w_authors', 'accepted_name_w_author', 'accepted_species']]
    v13_records_for_chaining = v13_records_for_chaining.drop_duplicates(keep='first')
    v13_records_for_chaining = v13_records_for_chaining.drop_duplicates(subset=['taxon_name_w_authors'],
                                                                        keep=False)  # Ignore cases with multiple resolutions, as these are ambiguous anyway
    v13_records_for_chaining = v13_records_for_chaining.rename(
        columns={'taxon_name_w_authors': new_tag + '_taxon_name_w_authors', 'accepted_name_w_author': new_tag + '_chained_accepted_name_w_author',
                 'accepted_species': new_tag + '_chained_accepted_species'})
    # chained result where taxon_name_w_authors are resolved to v13_chained_accepted_name_w_author, mediated by old database
    chained_updated_records = pd.merge(v12_records, v13_records_for_chaining, left_on=old_tag + '_accepted_name_w_author',
                                       right_on=new_tag + '_taxon_name_w_authors')

    return chained_updated_records


def get_direct_name_updates(v12_taxa: pd.DataFrame, v13_taxa: pd.DataFrame, new_tag: str, out_dir: str):
    # Pick non-duplicated names
    unique_names = v12_taxa['taxon_name_w_authors'].dropna().unique().tolist()

    # relevant names in new database where taxon name is taxon name in old database
    v13_updated_records = v13_taxa[v13_taxa['taxon_name_w_authors'].isin(unique_names)][
        ['taxon_name_w_authors', 'accepted_name_w_author', 'accepted_species']]
    v13_updated_records = v13_updated_records.dropna(subset=['accepted_name_w_author'])
    v13_updated_records = v13_updated_records.drop_duplicates(keep='first')
    v13_updated_records = v13_updated_records.drop_duplicates(subset=['taxon_name_w_authors'],
                                                              keep=False)  # Ignore cases with multiple resolutions, as these are ambiguous anyway
    v13_updated_records = v13_updated_records.rename(
        columns={'accepted_name_w_author': new_tag + '_direct_accepted_name_w_author',
                 'accepted_species': new_tag + '_direct_accepted_species'})
    v13_updated_records.describe(include='all').to_csv(os.path.join(out_dir, 'direct_updated_records_summary.csv'))

    return v13_updated_records


def compare_and_output_chained_and_direct_updates(chained_updated_records, direct_updated_records, old_tag: str, new_tag: str, out_dir: str):
    merged_df = pd.merge(chained_updated_records, direct_updated_records, on='taxon_name_w_authors')

    # remove cases with no direct accepted name in new version
    results_df = merged_df.dropna(subset=[new_tag + '_direct_accepted_name_w_author'])

    # get results where chaining provides no results even though direct match does
    unresolved_via_chaining = results_df[results_df[new_tag + '_chained_accepted_name_w_author'].isna()]
    unresolved_via_chaining.to_csv(os.path.join(out_dir, '_'.join([old_tag, new_tag]) + '_unresolved_via_chaining.csv'))

    results_df = results_df.dropna(subset=[new_tag + '_chained_accepted_name_w_author'])
    results_df.to_csv(os.path.join(out_dir, '_'.join([old_tag, new_tag]) + '.csv'))
    results_df = results_df[results_df[new_tag + '_direct_accepted_name_w_author'] != results_df[new_tag + '_chained_accepted_name_w_author']]

    # Add longer chains

    results_df.to_csv(os.path.join(out_dir, 'all_results.csv'))
    results_df.describe(include='all').to_csv(os.path.join(out_dir, 'all_results_summary.csv'))

    species_ambiguity_results = results_df.dropna(subset=[new_tag + '_direct_accepted_species'])
    species_ambiguity_results = species_ambiguity_results[
        species_ambiguity_results[new_tag + '_direct_accepted_species'] != species_ambiguity_results[
            new_tag + '_chained_accepted_species']]

    species_ambiguity_results.to_csv(os.path.join(out_dir, 'species_results.csv'))
    species_ambiguity_results.describe(include='all').to_csv(os.path.join(out_dir, 'species_results_summary.csv'))

    species_ambiguity_results[new_tag + '_chained_accepted_genus'] = species_ambiguity_results[new_tag + '_chained_accepted_species'].apply(
        get_genus_from_full_name)
    species_ambiguity_results[new_tag + '_direct_accepted_genus'] = species_ambiguity_results[new_tag + '_direct_accepted_species'].apply(
        get_genus_from_full_name)

    genus_ambiguity_results = species_ambiguity_results.dropna(subset=[new_tag + '_direct_accepted_genus'])
    genus_ambiguity_results = genus_ambiguity_results[
        genus_ambiguity_results[new_tag + '_chained_accepted_genus'] != genus_ambiguity_results[new_tag + '_direct_accepted_genus']]
    genus_ambiguity_results.to_csv(os.path.join(out_dir, 'genus_results.csv'))
    genus_ambiguity_results.describe(include='all').to_csv(os.path.join(out_dir, 'genus_results_summary.csv'))
    # cases_that_cant_update_df.to_csv(os.path.join(out_dir, 'v12_v13_cases_cant_update.csv'))
    # names_in_old_with_multiple_resolutions_df.to_csv(os.path.join(out_dir, 'v12_v13_names_in_old_with_multiple_resolutions.csv'))

    # do full summary

    return results_df


def compare_two_versions(v12_taxa: pd.DataFrame, v13_taxa: pd.DataFrame, old_tag: str, new_tag: str):
    # For all taxa with unique names (inc. author strings) in old taxon database
    # If the name resolves uniquely to a non-nan accepted name in both the old and new database
    # Find the accepted name resolution when the name is resolved first to the old taxonomy then the new taxonomy
    # If no such name exists, ignore, if not check if this name is the same as the name when directly resolved using the new database.
    out_dir = os.path.join(_output_path,
                           '_'.join([old_tag, new_tag]))
    os.makedirs(out_dir, exist_ok=True)

    chained_updated_records = chain_two_databases(v12_taxa, v13_taxa, old_tag, new_tag, out_dir)
    chained_updated_records.describe(include='all').to_csv(os.path.join(out_dir, 'chained_updated_records_summary.csv'))

    # relevant names in new database where taxon name is taxon name in old database
    v13_updated_records = get_direct_name_updates(v12_taxa, v13_taxa, new_tag, out_dir)
    results_df = compare_and_output_chained_and_direct_updates(chained_updated_records, v13_updated_records, old_tag, new_tag, out_dir)

    # Add a check here that no accepted names in v12 are in output
    problems = results_df[results_df['taxon_name_w_authors'] == results_df[f'{old_tag}_accepted_name_w_author']]
    assert len(problems) == 0
    return results_df


def compare_all_pairs():
    v10_taxa, v11_taxa, v12_taxa, v13_taxa = get_all_databases()

    compare_two_versions(v10_taxa, v13_taxa,
                         'v10', 'v13')
    compare_two_versions(v10_taxa, v12_taxa,
                         'v10', 'v12')
    compare_two_versions(v11_taxa, v13_taxa,
                         'v11', 'v13')

    compare_two_versions(v10_taxa, v11_taxa,
                         'v10', 'v11')
    compare_two_versions(v11_taxa, v12_taxa,
                         'v11', 'v12')
    compare_two_versions(v12_taxa, v13_taxa, 'v12', 'v13')


def full_chain_results():
    # Note when chaining like this, in intermediary steps ambiguous/non resolving names may be dropped.
    # This may somewhat reflect real world situations but is optimistic about the chaining process
    out_dir = os.path.join('outputs', 'full_chain')
    v10_taxa, v11_taxa, v12_taxa, v13_taxa = get_all_databases()
    # Start with 10 -> 11
    v10_11_chained = chain_two_databases(v10_taxa, v11_taxa, 'v10', 'v11', out_dir)
    v10_11_chained = v10_11_chained.rename(columns={'v11_chained_accepted_name_w_author': 'accepted_name_w_author'})
    v10_11_chained = v10_11_chained[['taxon_name_w_authors', 'accepted_name_w_author']]

    # Then chain -> 12
    v10_11_12_chained = chain_two_databases(v10_11_chained, v12_taxa, 'v10_11', 'v12', out_dir)
    v10_11_12_chained = v10_11_12_chained.rename(columns={'v12_chained_accepted_name_w_author': 'accepted_name_w_author'})
    v10_11_12_chained = v10_11_12_chained[['taxon_name_w_authors', 'accepted_name_w_author']]

    # Then -> 13
    v10_11_12_13_chained = chain_two_databases(v10_11_12_chained, v13_taxa, 'v10_11_12', 'v13', out_dir)

    direct_updated_records = get_direct_name_updates(v10_taxa, v13_taxa, 'v13', out_dir)
    results_df = compare_and_output_chained_and_direct_updates(v10_11_12_13_chained, direct_updated_records, 'v10_11_12', 'v13', out_dir)
    pass


def get_all_databases():
    # v10_taxa = get_all_taxa(version='10', output_csv=os.path.join(_input_path, 'v10_taxa.csv'))
    # v11_taxa = get_all_taxa(version='11', output_csv=os.path.join(_input_path, 'v11_taxa.csv'))
    # v12_taxa = get_all_taxa(version='12', output_csv=os.path.join(_input_path, 'v12_taxa.csv'))
    # v13_taxa = get_all_taxa(version=None, output_csv=os.path.join(_input_path, 'v13_taxa.csv'))

    v10_taxa = pd.read_csv(os.path.join(_input_path, 'v10_taxa.csv'), index_col=0)
    v11_taxa = pd.read_csv(os.path.join(_input_path, 'v11_taxa.csv'), index_col=0)
    v12_taxa = pd.read_csv(os.path.join(_input_path, 'v12_taxa.csv'), index_col=0)
    v13_taxa = pd.read_csv(os.path.join(_input_path, 'v13_taxa.csv'), index_col=0)

    v10_taxa['taxon_name_w_authors'] = add_authors_to_col(v10_taxa, 'taxon_name')
    v11_taxa['taxon_name_w_authors'] = add_authors_to_col(v11_taxa, 'taxon_name')
    v12_taxa['taxon_name_w_authors'] = add_authors_to_col(v12_taxa, 'taxon_name')
    v13_taxa['taxon_name_w_authors'] = add_authors_to_col(v13_taxa, 'taxon_name')

    return v10_taxa, v11_taxa, v12_taxa, v13_taxa


def summarise_results(dir_path: str, tag: str, old_tag='v10'):
    old_record_summary = pd.read_csv(os.path.join(dir_path, f'{old_tag}_old_records_summary.csv'), index_col=0)
    num_of_original_names = int(old_record_summary.at['unique', 'taxon_name_w_authors'])

    total_results = pd.read_csv(os.path.join(dir_path, 'all_results.csv'))
    num_total_results = len(total_results['taxon_name_w_authors'].unique().tolist())

    species_results = pd.read_csv(os.path.join(dir_path, 'species_results.csv'))
    num_species_results = len(species_results['taxon_name_w_authors'].unique().tolist())

    genus_results = pd.read_csv(os.path.join(dir_path, 'genus_results.csv'))
    num_genus_results = len(genus_results['taxon_name_w_authors'].unique().tolist())

    unresolved_via_chaining = pd.read_csv(os.path.join(dir_path, f'{tag}_unresolved_via_chaining.csv'))
    num_unresolved_via_chaining = len(unresolved_via_chaining['taxon_name_w_authors'].unique().tolist())

    out_df = pd.DataFrame([num_of_original_names, num_total_results, num_species_results, num_genus_results, num_unresolved_via_chaining])
    out_df.columns = [tag]
    out_df.index = ['original_names', 'total_disagreements', 'species_disagreements', 'genus_disagreements',
                    'unresolved_via_chaining_despite_a_direct_resolution']

    out_df['Percentages'] = 100 * out_df[tag] / num_of_original_names
    out_df.to_csv(os.path.join(dir_path, 'result_summary.csv'))
    pass


if __name__ == '__main__':
    compare_all_pairs()
    full_chain_results()
    summarise_results(os.path.join('outputs', 'v10_v13'), 'v10_v13')
    summarise_results(os.path.join('outputs', 'v10_v12'), 'v10_v12')
    summarise_results(os.path.join('outputs', 'v10_v11'), 'v10_v11')
    summarise_results(os.path.join('outputs', 'full_chain'), 'v10_11_12_v13')
