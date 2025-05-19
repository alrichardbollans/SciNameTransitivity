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
    ['Variety', 'Species', 'Form', 'Forma', 'Nothospecies', 'Subspecies', 'Unranked', 'Prole', 'Subvariety', 'Lusus', 'Subform', 'Section',
     'Subseries', 'Series',
     'Subsection', 'Subgenus', 'Genus']))

class WFO_Version():

    def __init__(self, tag, extension, DOI):
        self.tag = tag
        self.extension = extension
        self.DOI = DOI

    def get_csv_file(self):
        input_zip_file = os.path.join(_wfo_downloads_path, f'WFOTaxonomicBackbone_{self.tag}.zip')
        zf = zipfile.ZipFile(input_zip_file)
        csv_file = zf.open(f'classification.{self.extension}')
        return csv_file


def all_versions():
    out_list = [WFO_Version('201807', 'txt', 'https://zenodo.org/records/7460142'),
                # dont use these versions. 201903 comes without headers. 201904 is 27Gb for some reason
                # WFO_Version('201903', 'txt', 'https://zenodo.org/records/7460932'),
                # WFO_Version('201904', 'txt', 'https://zenodo.org/records/7461831'),
                WFO_Version('201905', 'txt', 'https://zenodo.org/records/7462137'),
                WFO_Version('202112', 'txt', 'https://zenodo.org/records/7462229'),
                WFO_Version('202204', 'txt', 'https://zenodo.org/records/7462427'),
                WFO_Version('202207', 'txt', 'https://zenodo.org/records/7462490'),
                ## Versions after 202212 seems to have been overhauled and has different file extension and encoding
                # Downloaded from zenodo _DwC_backbone
                WFO_Version('202212', 'csv', 'https://zenodo.org/records/7467360'),
                WFO_Version('202306', 'csv', 'https://zenodo.org/records/8079052'),
                WFO_Version('202312', 'csv', 'https://zenodo.org/records/10425161'),
                WFO_Version('202406', 'csv', 'https://zenodo.org/records/12171908'),
                WFO_Version('202412', 'csv', 'https://zenodo.org/records/14538251'),
                ]
    return out_list

WFO_VERSIONS = all_versions()

latest_wfo_version_string = WFO_VERSIONS[-1].tag
oldest_wfo_version_string = WFO_VERSIONS[0].tag
other_version_strings = ['201905', '202112', '202204','202207','202212','202306','202312','202306','202406']
all_wfo_version_strings = [oldest_wfo_version_string] + other_version_strings + [latest_wfo_version_string]
wfo_version_comparable_to_v10_string = '202212'
wfo_version_strings_after_v10 = ['202306','202312','202306','202406']


def get_version_from_tag(tag:str):
    for c in all_versions():
        if c.tag == tag:
            return c
    raise ValueError

def wfo_sanity_checks(all_wfo_data_untouched, all_wfo_data, accepted_data, resolved_wfo_data):
    """
    Performs a series of sanity checks on WFO (World Flora Online) data. The function performs various validations on
    the provided dataframes to ensure data consistency and correctness, particularly focusing on taxonomic status and
    related information. It generates a CSV file listing specific attributes from one of the datasets and runs checks
    on taxonomic statuses, accepted name references, and unresolved data issues.

    :param all_wfo_data_untouched: Original WFO dataset, untouched and used as a reference for validations
        and comparisons.
    :type all_wfo_data_untouched: pandas.DataFrame
    :param all_wfo_data: Processed or modified WFO dataset that requires validation.
    :type all_wfo_data: pandas.DataFrame
    :param accepted_data: Data containing information about accepted taxon names for validation against the WFO data.
    :type accepted_data: pandas.DataFrame
    :param resolved_wfo_data: Processed WFO data, where taxonomic issues have been resolved or partially resolved.
        This dataset is the focus of several validations.
    :type resolved_wfo_data: pandas.DataFrame
    :return: None
    :rtype: NoneType
    """
    resolved_wfo_data[
        ['taxonID', 'taxon_name', 'taxon_name_w_authors', 'accepted_name', 'accepted_name_w_author', 'accepted_name_id', 'accepted_species',
         'accepted_species_w_author', 'accepted_genus',
         'taxon_rank', 'taxon_status']].head(1000).to_csv('wfo_sanity_check.csv')
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
                ['Family', 'Tribe', 'Subfamily', 'Order', 'Class', 'Subtribe'])]  # a family/tribe etc.. was erroneously included
        print(what_are_these['taxonomicStatus'].unique().tolist())
        assert 'Accepted' not in what_are_these['taxonomicStatus'].values


def parse_wfo_data(all_wfo_data):
    ## Get a copy that wont be edited, just for sanity checks
    all_wfo_data_untouched = all_wfo_data.copy(deep=True)

    # restrict to genus and lower
    # some genus names werent correctly set
    all_wfo_data['genus'] = np.where(all_wfo_data['taxonRank'] == 'Genus', all_wfo_data['scientificName'], all_wfo_data['genus'])
    all_wfo_data = all_wfo_data[~all_wfo_data['genus'].isna()]

    ### set scientificnames to include authors
    all_wfo_data['taxon_name'] = all_wfo_data['scientificName']
    all_wfo_data['taxon_name_w_authors'] = all_wfo_data['taxon_name'] + ' ' + all_wfo_data['scientificNameAuthorship'].fillna('').astype(str)

    ## Add a species name
    print(all_wfo_data['taxonRank'].unique().tolist())
    all_wfo_data['species_name'] = np.where(all_wfo_data['taxonRank'] == 'Genus', np.nan,
                                            all_wfo_data['genus'] + ' ' + all_wfo_data['specificEpithet'].fillna('').astype(str))
    all_wfo_data['species_name_w_author'] = np.where(all_wfo_data['species_name'].isna(), np.nan,
                                                     all_wfo_data['species_name'] + ' ' + all_wfo_data['scientificNameAuthorship'].fillna('').astype(
                                                         str))

    ### Set accepted_name_ids either from taxonID (for accepted names) or acceptedNameUsageID
    all_wfo_data['accepted_name_id'] = np.where(all_wfo_data['taxonomicStatus'] == 'Accepted', all_wfo_data['taxonID'],
                                                all_wfo_data['acceptedNameUsageID'])
    ### Remove instances without accepted ids
    resolved_wfo_data = all_wfo_data.dropna(subset=['accepted_name_id'])

    ### Use the accepted IDs to get accepted names from the original dataframe
    accepted_data = all_wfo_data[all_wfo_data['taxonomicStatus'] == 'Accepted'][
        ['taxonID', 'taxon_name', 'taxon_name_w_authors', 'species_name', 'species_name_w_author', 'genus']]
    accepted_data = accepted_data.dropna(subset=['taxonID'])
    accepted_data = accepted_data.rename(
        columns={'taxonID': 'acc_id', 'taxon_name': 'accepted_name', 'taxon_name_w_authors': 'accepted_name_w_author',
                 'species_name': 'accepted_species',
                 'species_name_w_author': 'accepted_species_w_author',
                 'genus': 'accepted_genus'})

    resolved_wfo_data = pd.merge(resolved_wfo_data, accepted_data, how='left', left_on=['accepted_name_id'], right_on=['acc_id'])
    resolved_wfo_data['taxon_rank'] = resolved_wfo_data['taxonRank']
    resolved_wfo_data['taxon_status'] = resolved_wfo_data['taxonomicStatus']

    wfo_sanity_checks(all_wfo_data_untouched, all_wfo_data, accepted_data, resolved_wfo_data)

    ## Only return cases with accepted names
    resolved_wfo_data = resolved_wfo_data.dropna(subset=['accepted_name_w_author'])

    ### and only return used columns

    return resolved_wfo_data[
        ['taxonID', 'taxon_name', 'taxon_name_w_authors', 'accepted_name', 'accepted_name_w_author', 'accepted_name_id', 'accepted_species',
         'accepted_species_w_author', 'accepted_genus',
         'taxon_rank', 'taxon_status']]


def clean_columns(all_wfo_data):
    all_wfo_data['taxonRank'] = all_wfo_data['taxonRank'].str.capitalize()  # in old version they use upper case :(
    all_wfo_data['taxonomicStatus'] = all_wfo_data['taxonomicStatus'].str.capitalize()  # in old version they use upper case :(
    all_wfo_data['taxonomicStatus'] = np.where(all_wfo_data['taxonomicStatus'] == 'Accetped', 'Accepted',
                                               all_wfo_data['taxonomicStatus'])  # spelling mistake

    ## Fix some issues around hybrid characters and generally clean
    all_wfo_data['scientificName'] = all_wfo_data['scientificName'].apply(remove_spacelike_chars)
    all_wfo_data['scientificName'] = all_wfo_data['scientificName'].apply(add_space_around_hybrid_chars_and_infraspecific_epithets)
    all_wfo_data['scientificName'] = all_wfo_data['scientificName'].apply(clean_whitespaces_in_names)

    return all_wfo_data


def get_version_data(version: WFO_Version):
    csv_file = version.get_csv_file()

    all_wfo_data = pd.read_csv(csv_file, sep='\t', encoding='latin1')

    all_wfo_data = all_wfo_data.rename(columns={'ï»¿taxonID': 'taxonID'})  ## This was a weird error in the earliest version

    all_wfo_data['scientificName'] = all_wfo_data['scientificName'].str.encode('latin1').str.decode('utf-8', errors='replace')
    all_wfo_data['scientificNameAuthorship'] = all_wfo_data['scientificNameAuthorship'].str.encode('latin1').str.decode('utf-8', errors='replace')
    cleaned = clean_columns(all_wfo_data)
    resolved = parse_wfo_data(cleaned)

    csv_file.close()

    return resolved

def get_latest_version():
    version = get_version_from_tag(latest_wfo_version_string)
    return get_version_data(version), latest_wfo_version_string


def get_oldest_version():
    version = get_version_from_tag(oldest_wfo_version_string)
    return get_version_data(version), oldest_wfo_version_string

def get_version_comparable_to_v10():
    version = get_version_from_tag(wfo_version_comparable_to_v10_string)
    return get_version_data(version), wfo_version_comparable_to_v10_string

def get_other_versions():
    out_dict = {}
    for tag in other_version_strings:
        print(f'Getting data for version {tag}')
        version = get_version_from_tag(tag)
        resolved = get_version_data(version)
        out_dict[tag] = resolved

    return out_dict

def get_versions_after_v10(other_versions:dict):
    out_dict = {}
    for v in other_versions:
        if v in wfo_version_strings_after_v10:
            out_dict[v] = other_versions[v]
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
    get_other_versions()
    new, new_tag = get_latest_version()
    old, old_tag = get_oldest_version()
    look_at_example(old, new, 'Senecio bowenkampi Phil.')
    look_at_example(old, new, 'Haplopappus wigginsii S.F.Blake')
    look_at_example(old, new, 'Helichrysum leptolepis DC.')
    #
    # get_other_versions()
    # get_latest_version()
