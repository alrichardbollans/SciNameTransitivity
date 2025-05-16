import os

import pandas as pd
from wcvpy.wcvp_download import wcvp_columns, wcvp_accepted_columns

repo_path = os.environ.get('KEWSCRATCHPATH')
this_repo_path = os.path.join(repo_path, 'TaxoDrift')
_output_path = os.path.join(this_repo_path, 'analyse_number_of_changes', 'outputs')


def get_species_differences(df1: pd.DataFrame, df2: pd.DataFrame, old_tag: str, new_tag: str, with_authorship: bool = False):
    tag = '_'.join([old_tag, new_tag])
    out_dir = os.path.join(_output_path, tag)
    os.makedirs(out_dir, exist_ok=True)

    if with_authorship:
        acc_species_col = 'accepted_species_w_author'
        name_col = 'taxon_name_w_authors'
        addendum = 'but this could be due to orthographic changes with authorship'
        file_tag = 'w_author'
    else:
        acc_species_col = 'accepted_species'
        name_col = 'taxon_name'
        addendum = ''
        file_tag = ''

    old_accepted_species = df1[acc_species_col].dropna().unique().tolist()
    new_accepted_species = df2[acc_species_col].dropna().unique().tolist()

    print(
        f'New has {len(new_accepted_species)} accepted species names, old has {len(old_accepted_species)} accepted species names')

    new_accepted_species_that_were_published_in_old = df1[df1[name_col].isin(new_accepted_species)][
        name_col].dropna().unique().tolist()
    print(f'New has {len(new_accepted_species_that_were_published_in_old)} accepted species names which were previously published')

    new_species_not_in_old = set(new_accepted_species) - set(old_accepted_species)
    old_species_not_in_new = set(old_accepted_species) - set(new_accepted_species)

    old_species = df1[df1[wcvp_columns['rank']] == 'Species'][name_col].unique().tolist()
    new_species = df2[df2[wcvp_columns['rank']] == 'Species'][name_col].unique().tolist()

    new_species_not_in_old = set(new_species) - set(old_species)
    old_species_not_in_new = set(old_species) - set(new_species)
    print(f'New has {len(new_species)} species names, old has {len(old_species)} species names')
    print(f'new has {len(new_species_not_in_old)} species names not in old')
    print(
        f'{len(old_species_not_in_new)} species names have disappeared, but this could be due to orthographic changes with authorship if with_authorship is True')

    out_df = pd.DataFrame(
        [len(new_accepted_species), len(old_accepted_species),
         len(new_accepted_species_that_were_published_in_old),
         len(new_species), len(old_species),
         len(new_species_not_in_old), len(old_species_not_in_new)])
    out_df.columns = [tag]

    out_df.index = ['number of new accepted species names', 'number of old accepted species names',
                    'new accepted species names which were previously published',
                    'number of new species names', 'number of old species names',
                    'new species names not in old', 'species names have disappeared' + addendum]

    out_df.to_csv(os.path.join(out_dir, f'species_differences_summary_{file_tag}.csv'))

    df1[df1[name_col].isin(old_species_not_in_new)].to_csv(os.path.join(out_dir, f'dissappeared_species_{file_tag}.csv'))


def get_accepted_species_that_become_unaccepted(df1, df2, old_tag: str, new_tag: str, with_authorship: bool = True):
    tag = '_'.join([old_tag, new_tag])
    out_dir = os.path.join(_output_path, tag, 'accepted_species_that_become_unaccepted')
    os.makedirs(out_dir, exist_ok=True)

    if with_authorship:

        file_tag = 'w_author'
    else:
        raise ValueError('I think with_authorship should be True for this particular analysis')

    old_accepted_species = df1[wcvp_accepted_columns['species_w_author']].dropna().unique().tolist()

    non_accepted_new_df = df2[~df2[wcvp_columns['status']].isin(['Accepted', 'Artificial Hybrid'])]

    old_names_that_are_no_longer_accepted_df = non_accepted_new_df[non_accepted_new_df['taxon_name_w_authors'].isin(old_accepted_species)]
    old_names_that_are_no_longer_accepted = old_names_that_are_no_longer_accepted_df['taxon_name_w_authors'].unique().tolist()

    print(f'{len(old_names_that_are_no_longer_accepted)} old accepted species names are no longer accepted out of {len(old_accepted_species)}')

    out_list = [str(len(old_accepted_species)), str(len(old_names_that_are_no_longer_accepted))]
    out_index = ['number of old accepted species names', 'old accepted species names are no longer accepted']
    for status in old_names_that_are_no_longer_accepted_df[wcvp_columns['status']].unique().tolist():
        print('###########')
        print(status)
        old_accepted_names_that_are_now_status_df = old_names_that_are_no_longer_accepted_df[
            old_names_that_are_no_longer_accepted_df[wcvp_columns['status']] == status]
        if 'homotypic_synonym' in old_accepted_names_that_are_now_status_df.columns:
            homotypic = old_accepted_names_that_are_now_status_df[old_accepted_names_that_are_now_status_df['homotypic_synonym'] == 'T']
            heterotypic = old_accepted_names_that_are_now_status_df[old_accepted_names_that_are_now_status_df['homotypic_synonym'] != 'T']
            print(
                f'{len(old_accepted_names_that_are_now_status_df['taxon_name_w_authors'].unique().tolist())} old accepted species names are now {status}, of which {len(homotypic['taxon_name_w_authors'].unique().tolist())} are homotypic and {len(heterotypic['taxon_name_w_authors'].unique().tolist())} are heterotypic')
            out_list.append('/'.join([str(len(old_accepted_names_that_are_now_status_df['taxon_name_w_authors'].unique().tolist())),
                                      str(len(homotypic['taxon_name_w_authors'].unique().tolist())),
                                      str(len(heterotypic['taxon_name_w_authors'].unique().tolist()))]))
            out_index.append(f'Number which are now {status} of which (homotypic)/(heterotypic)')
        else:
            out_list.append(str(len(old_accepted_names_that_are_now_status_df['taxon_name_w_authors'].unique().tolist())))
            out_index.append(f'Number which are now {status}')

        old_accepted_names_that_are_now_status_df.to_csv(os.path.join(out_dir, f'accepted_species_that_become_{status}_{file_tag}.csv'))
    out_df = pd.DataFrame(out_list)
    out_df.columns = [tag]

    out_df.index = out_index

    out_df.to_csv(os.path.join(out_dir, f'accepted_species_that_become_unaccepted_summary_{file_tag}.csv'))


def get_unaccepted_species_that_become_accepted(df1, df2, old_tag: str, new_tag: str, with_authorship: bool = True):
    tag = '_'.join([old_tag, new_tag])
    out_dir = os.path.join(_output_path, tag, 'unaccepted_species_that_become_accepted')
    os.makedirs(out_dir, exist_ok=True)

    if with_authorship:

        file_tag = 'w_author'
    else:
        raise ValueError('I think with_authorship should be True for this particular analysis')


    old_species = df1[df1[wcvp_columns['rank']] == 'Species']
    old_non_accepted_species_df = old_species[~old_species[wcvp_columns['status']].isin(['Accepted', 'Artificial Hybrid'])]
    new_accepted_species = df2[wcvp_accepted_columns['species_w_author']].dropna().unique().tolist()
    old_non_accepted_species_that_become_accepted_df = old_non_accepted_species_df[
        old_non_accepted_species_df['taxon_name_w_authors'].isin(new_accepted_species)]

    out_list = [str(len(old_non_accepted_species_df['taxon_name_w_authors'].unique().tolist())),
                str(len(old_non_accepted_species_that_become_accepted_df['taxon_name_w_authors'].unique().tolist()))]
    out_index = ['number of old unaccepted species names', 'old unaccepted species names are now accepted']
    statuses = old_non_accepted_species_that_become_accepted_df[wcvp_columns['status']].unique().tolist()
    for status in statuses:
        old_status_species = \
            old_non_accepted_species_that_become_accepted_df[old_non_accepted_species_that_become_accepted_df[wcvp_columns['status']] == status]

        print(
            f'{len(old_status_species)} old {status} species are now accepted out of {len(old_non_accepted_species_df)}')
        old_status_species.to_csv(os.path.join(out_dir, f'{status}_species_that_become_accepted_{file_tag}.csv'))

        out_list.append(str(len(old_status_species['taxon_name_w_authors'].unique().tolist())))
        out_index.append(f'Number of old {status}s which are now accepted')

    out_df = pd.DataFrame(out_list)
    out_df.columns = [tag]

    out_df.index = out_index

    out_df.to_csv(os.path.join(out_dir, f'unaccepted_species_that_become_accepted_summary_{file_tag}.csv'))


def get_names_that_resolve_in_old_but_not_in_new(v12_taxa: pd.DataFrame, v13_taxa: pd.DataFrame, old_tag: str, new_tag: str,
                                                 with_authorship: bool = False):
    """
    Identify taxon names that resolve in the earlier dataset (v12) but not in the newer dataset (v13).

    If authorship is included you get some incorrect examples like
    Ozanonia alpina where the author is (L. ex Hartm.) Gand. in the old but (L.) Gand. in the new

    :param v12_taxa: Dataset containing taxon information for the older dataset.
    :type v12_taxa: pd.DataFrame
    :param v13_taxa: Dataset containing taxon information for the newer dataset.
    :type v13_taxa: pd.DataFrame
    :return: A set of taxon names resolved in the v12 dataset but not in the v13 dataset.
    :rtype: set
    """
    tag = '_'.join([old_tag, new_tag])
    out_dir = os.path.join(_output_path, tag)
    os.makedirs(out_dir, exist_ok=True)

    if with_authorship:
        taxon_name_col = 'taxon_name_w_authors'
    else:
        taxon_name_col = 'taxon_name'

    v12_with_resolution = v12_taxa[~v12_taxa[wcvp_accepted_columns['name']].isna()]

    names_that_resolve_in_v12 = v12_with_resolution[taxon_name_col].unique().tolist()

    v13_with_resolution = v13_taxa[~v13_taxa[wcvp_accepted_columns['name']].isna()]

    names_that_resolve_in_v13 = v13_with_resolution[taxon_name_col].unique().tolist()

    names_that_resolve_in_old_but_not_in_new = set(names_that_resolve_in_v12) - set(names_that_resolve_in_v13)
    # print(names_that_resolve_in_old_but_not_in_new)

    names_that_resolve_in_old_but_not_in_new_df = v12_taxa[v12_taxa[taxon_name_col].isin(names_that_resolve_in_old_but_not_in_new)]

    names_that_resolve_in_old_but_not_in_new_df[['taxon_name', 'taxon_name_w_authors']].to_csv(
        os.path.join(out_dir, 'names_that_resolve_in_old_but_not_in_new.csv'))

    num_of_original_names = len(names_that_resolve_in_v12)
    out_df = pd.DataFrame([num_of_original_names, len(names_that_resolve_in_old_but_not_in_new)])
    out_df.columns = [tag]
    out_df.index = ['number of original_names', 'names_that_resolve_in_old_but_not_in_new']

    out_df['Percentages'] = 100 * out_df[tag] / num_of_original_names
    out_df.to_csv(os.path.join(out_dir, 'names_that_resolve_in_old_but_not_in_new_summary.csv'))

    return names_that_resolve_in_old_but_not_in_new_df
