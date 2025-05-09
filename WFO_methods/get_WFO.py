###

import os
import zipfile
from pathlib import Path

import numpy as np
import pandas as pd
from wcvpy.wcvp_download import clean_whitespaces_in_names
from wcvpy.wcvp_name_matching import remove_spacelike_chars, add_space_around_hybrid_chars_and_infraspecific_epithets

_wfo_downloads_path = os.path.join(Path.home(), '.wfo_downloads')

_all_ranks = list(sorted(
    ['variety', 'species', 'form', 'subspecies', 'unranked', 'prole', 'subvariety', 'lusus', 'subform', 'section', 'subseries', 'series',
     'subsection', 'subgenus', 'genus', 'family', 'tribe', 'subtribe', 'supertribe', 'subfamily', 'order', 'superorder', 'subclass', 'class',
     'phylum', 'kingdom', 'suborder', 'subkingdom']))

ranks_to_use = list(sorted(
    ['variety', 'species', 'form', 'forma', 'nothospecies', 'subspecies', 'unranked', 'prole', 'subvariety', 'lusus', 'subform', 'section',
     'subseries', 'series',
     'subsection', 'subgenus', 'genus']))


def wfo_sanity_checks(all_wfo_data_untouched, all_wfo_data, accepted_data, resolved_wfo_data):
    ###################
    ### Sanity checks
    accepted_check = resolved_wfo_data[resolved_wfo_data['taxonomicStatus'] == 'Accepted']
    pd.testing.assert_series_equal(accepted_check['taxon_name_w_authors'], accepted_data['accepted_name_w_author'], check_names=False,
                                   check_index=False)

    ### Check statuses in data
    statuses = all_wfo_data_untouched['taxonomicStatus'].dropna().unique().tolist()
    print(statuses)
    for c in statuses:
        print(c)
        assert c in ['Synonym', 'Doubtful', 'Accepted', 'Heterotypicsynonym', 'Homotypicsynonym', 'Unchecked', 'Ambiguous']

    ### Check statuses again
    statuses = resolved_wfo_data['taxonomicStatus'].unique().tolist()
    assert (list(sorted(statuses)) == ['Accepted', 'Synonym']) or (
            statuses == ['Synonym', 'Accepted', 'Heterotypicsynonym', 'Homotypicsynonym'])

    ahhhh = list(sorted(all_wfo_data['taxonRank'].unique().tolist()))
    for a in ahhhh:
        example = all_wfo_data[all_wfo_data['taxonRank'] == a]
        assert a in ranks_to_use

    # Cases where accepted_ids in resolved_wfo_data aren't found in accepted_data
    nan_issues = resolved_wfo_data[resolved_wfo_data['accepted_name_w_author'].isna()]
    if len(nan_issues) > 0:
        # In old version, some taxa resolve to an ID which isn't counted as accepted. These will just be removed
        to_check = resolved_wfo_data[~resolved_wfo_data['accepted_name_id'].isin(accepted_data['acc_id'].values)]
        things_that_have_been_removed = all_wfo_data_untouched[all_wfo_data_untouched['taxonID'].isin(to_check['accepted_name_id'].values)]
        to_check2 = resolved_wfo_data[~resolved_wfo_data['accepted_name_id'].isin(all_wfo_data_untouched['taxonID'].values)]

        what_are_these = all_wfo_data_untouched[all_wfo_data_untouched['taxonID'].isin(nan_issues['accepted_name_id'].values)]
        what_are_these = what_are_these[
            ~what_are_these['taxonRank'].isin(
                ['family', 'tribe', 'subfamily', 'order', 'class', 'subtribe'])]  # a family/tribe etc.. was erroneously included
        print(what_are_these['taxonomicStatus'].unique().tolist())
        assert 'Accepted' not in what_are_these['taxonomicStatus'].values


def parse_wfo_data(all_wfo_data):
    ## Get a copy that wont be edited, just for sanity checks
    all_wfo_data_untouched = all_wfo_data.copy(deep=True)

    # restrict to genus and lower
    # some genus names werent correctly set
    all_wfo_data['genus'] = np.where(all_wfo_data['taxonRank'] == 'genus', all_wfo_data['scientificName'], all_wfo_data['genus'])
    all_wfo_data = all_wfo_data[~all_wfo_data['genus'].isna()]

    ### set scientificnames to include authors
    all_wfo_data['taxon_name_w_authors'] = all_wfo_data['scientificName'] + ' ' + all_wfo_data['scientificNameAuthorship'].fillna('').astype(str)

    ## Add a species name
    print(all_wfo_data['taxonRank'].unique().tolist())
    all_wfo_data['species_name'] = np.where(all_wfo_data['taxonRank'] == 'genus', np.nan,
                                            all_wfo_data['genus'] + ' ' + all_wfo_data['specificEpithet'].fillna('').astype(str))

    ### Set accepted_name_ids either from taxonID (for accepted names) or acceptedNameUsageID
    all_wfo_data['accepted_name_id'] = np.where(all_wfo_data['taxonomicStatus'] == 'Accepted', all_wfo_data['taxonID'],
                                                all_wfo_data['acceptedNameUsageID'])
    ### Remove instances without accepted ids
    resolved_wfo_data = all_wfo_data.dropna(subset=['accepted_name_id'])

    ### Use the accepted IDs to get accepted names from the original dataframe
    accepted_data = all_wfo_data[all_wfo_data['taxonomicStatus'] == 'Accepted'][['taxonID', 'taxon_name_w_authors', 'species_name', 'genus']]
    accepted_data = accepted_data.dropna(subset=['taxonID'])
    accepted_data = accepted_data.rename(
        columns={'taxonID': 'acc_id', 'taxon_name_w_authors': 'accepted_name_w_author', 'species_name': 'accepted_species',
                 'genus': 'accepted_genus'})

    resolved_wfo_data = pd.merge(resolved_wfo_data, accepted_data, how='left', left_on=['accepted_name_id'], right_on=['acc_id'])

    wfo_sanity_checks(all_wfo_data_untouched, all_wfo_data, accepted_data, resolved_wfo_data)

    ## Only return cases with accepted names
    resolved_wfo_data = resolved_wfo_data.dropna(subset=['accepted_name_w_author'])

    ### and only return used columns
    return resolved_wfo_data[['taxonID', 'taxon_name_w_authors', 'accepted_name_w_author', 'accepted_name_id', 'accepted_species', 'accepted_genus']]


def get_csv_file(tag, extension):
    input_zip_file = os.path.join(_wfo_downloads_path, f'WFOTaxonomicBackbone_{tag}.zip')
    zf = zipfile.ZipFile(input_zip_file)
    csv_file = zf.open(f'classification.{extension}')
    return csv_file


def clean_columns(all_wfo_data):
    all_wfo_data['taxonRank'] = all_wfo_data['taxonRank'].str.lower()  # in old version they use upper case :(
    all_wfo_data['taxonomicStatus'] = all_wfo_data['taxonomicStatus'].str.capitalize()  # in old version they use upper case :(
    all_wfo_data['taxonomicStatus'] = np.where(all_wfo_data['taxonomicStatus'] == 'Accetped', 'Accepted',
                                               all_wfo_data['taxonomicStatus'])  # spelling mistake


    ## Fix some issues around hybrid characters and generally clean
    all_wfo_data['scientificName'] = all_wfo_data['scientificName'].apply(remove_spacelike_chars)
    all_wfo_data['scientificName'] = all_wfo_data['scientificName'].apply(add_space_around_hybrid_chars_and_infraspecific_epithets)
    all_wfo_data['scientificName'] = all_wfo_data['scientificName'].apply(clean_whitespaces_in_names)

    return all_wfo_data


def get_version(version: str, extension: str):
    csv_file = get_csv_file(version, extension)

    all_wfo_data = pd.read_csv(csv_file, sep='\t', encoding='latin1')

    all_wfo_data = all_wfo_data.rename(columns={'ï»¿taxonID':'taxonID'}) ## This was a weird error in the earliest version

    all_wfo_data['scientificName'] = all_wfo_data['scientificName'].str.encode('latin1').str.decode('utf-8', errors='replace')
    all_wfo_data['scientificNameAuthorship'] = all_wfo_data['scientificNameAuthorship'].str.encode('latin1').str.decode('utf-8', errors='replace')
    cleaned = clean_columns(all_wfo_data)
    resolved = parse_wfo_data(cleaned)

    csv_file.close()

    return resolved


def get_latest_version():
    ## Versions after 2023 seems to have been overhauled and has different file extension and encoding
    # Downloaded from zenodo _DwC_backbone
    tag = '202406'
    return get_version(tag, 'csv'), tag


def get_oldest_version():
    tag = '201807'
    return get_version(tag, 'txt'), tag


def get_other_versions():
    out_dict = {}
    for c in ['201905', '202112', '202207']:
        resolved = get_version(c, 'txt')
        out_dict[c] = resolved

    for c in ['202306']:
        resolved = get_version(c, 'csv')
        out_dict[c] = resolved

    return out_dict


def look_at_example(old_wfo_data, new_wfo_data, taxon_name_w_authors):
    example = old_wfo_data[old_wfo_data['taxon_name_w_authors'] == taxon_name_w_authors]
    new_example = new_wfo_data[new_wfo_data['taxon_name_w_authors'] == taxon_name_w_authors]

    acc_name_from_old = example['accepted_name_w_author'].iloc[0]
    chained_example = new_wfo_data[new_wfo_data['taxon_name_w_authors'] == acc_name_from_old]

    try:
        direct_resolution = new_example['accepted_name_w_author'].iloc[0]
    except IndexError:
        direct_resolution = None
        print(f'No direct resolution found for {taxon_name_w_authors}')
    print(
        f'Name: {taxon_name_w_authors} resolves to {acc_name_from_old} and then {chained_example["accepted_name_w_author"].iloc[0]}. Direct resolution is {direct_resolution}')


if __name__ == '__main__':
    new,new_tag = get_latest_version()
    old, old_tag = get_oldest_version()
    look_at_example(old,new,'Senecio bowenkampi Phil.')
    look_at_example(old,new,'Haplopappus wigginsii S.F.Blake')
    look_at_example(old,new,'Helichrysum leptolepis DC.')
    #
    # get_other_versions()
    # get_latest_version()

