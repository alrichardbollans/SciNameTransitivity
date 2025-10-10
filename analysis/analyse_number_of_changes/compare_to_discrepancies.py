import os

import pandas as pd
import seaborn as sns
from matplotlib import pyplot as plt
from scipy import stats

from analysis.analyse_number_of_changes.helper_functions import this_repo_path


def get_data_for_pair(folder):
    # sp_number_df = pd.read_csv(os.path.join(folder, 'species_differences_summary_w_author.csv'), index_col=0)
    # sp_number = sp_number_df.loc['new species names not in old'].iloc[0]
    synonyn_df = pd.read_csv(
        os.path.join(folder, 'accepted_species_that_become_unaccepted', 'accepted_species_that_become_unaccepted_summary_w_author.csv'), index_col=0)
    synonymisations = int(synonyn_df.loc['old accepted species names are no longer accepted'].iloc[0])
    percent_synonymisations = synonymisations / int(synonyn_df.loc['number of old accepted species names'].iloc[0])

    ressurection_df = pd.read_csv(
        os.path.join(folder, 'unaccepted_species_that_become_accepted', 'unaccepted_species_that_become_accepted_summary_w_author.csv'), index_col=0)

    resurrections = int(ressurection_df.loc['old unaccepted species names are now accepted'].iloc[0])
    percent_resurrections = resurrections / int(ressurection_df.loc['number of old unaccepted species names'].iloc[0])

    return percent_synonymisations, percent_resurrections


def get_species_discrepancies_for_pair(folder, taxonomy_name:str):
    if taxonomy_name == 'wcvp':
        value_dir = os.path.join(this_repo_path, 'WCVP_methods', 'outputs', folder)
    if taxonomy_name == 'wfo':
        value_dir = os.path.join(this_repo_path, 'WFO_methods', 'outputs', folder)

    sp_disagreements_df = pd.read_csv(os.path.join(value_dir, 'result_summary.csv'), index_col=0)
    number = sp_disagreements_df[['Percentages']].loc['species_disagreements'].iloc[0]
    return number


def analyse_taxonomy_data(name):
    dir_path = os.path.join('outputs', name)
    data = []
    for folder in os.listdir(dir_path):
        if os.path.isdir(os.path.join(dir_path, folder)):
            resurrections, synonymisations = get_data_for_pair(os.path.join(dir_path, folder))
            sp_disrecepancies = get_species_discrepancies_for_pair(folder, name)
            data.append([sp_disrecepancies, resurrections, synonymisations])
    out_df = pd.DataFrame(data, columns = ['Species Discrepancies (%)', 'Synonymisations (%)', 'Resurrections (%)'])
    out_df['Synonymisations (%)'] = out_df['Synonymisations (%)'] * 100
    out_df['Resurrections (%)'] = out_df['Resurrections (%)'] * 100
    out_df['Taxonomy'] = name.upper()

    sns.set_theme()
    sns.scatterplot(data=out_df, x="Synonymisations (%)", y="Species Discrepancies (%)")
    plt.savefig(os.path.join(dir_path,'sp_vs_synonyms.jpg'), dpi=300)
    plt.close()

    sp_result = stats.spearmanr(out_df["Synonymisations (%)"].values, out_df['Species Discrepancies (%)'].values)
    spearman_data = []
    spearman_data.append([sp_result.statistic, sp_result.pvalue, 'Synonymisations (%)'])


    sns.scatterplot(data=out_df, y="Species Discrepancies (%)", x="Resurrections (%)")
    plt.savefig(os.path.join(dir_path,'sp_vs_ressurections.jpg'), dpi=300)
    plt.close()

    sp_result = stats.spearmanr(out_df["Resurrections (%)"].values, out_df['Species Discrepancies (%)'].values)

    spearman_data.append([sp_result.statistic, sp_result.pvalue, 'Resurrections (%)'])
    spearman_data = pd.DataFrame(spearman_data, columns=['Spearman Correlation', 'P-value', 'Type'])
    spearman_data.to_csv(os.path.join(dir_path,'spearman_tests.csv'))
    return out_df

def main():
    wcvp_results = analyse_taxonomy_data('wcvp')
    wfo_results = analyse_taxonomy_data('wfo')

    sns.scatterplot(data=pd.concat([wfo_results,wcvp_results]), y="Species Discrepancies (%)", x="Resurrections (%)", hue='Taxonomy')
    plt.savefig(os.path.join('outputs', 'sp_vs_ressurections.jpg'), dpi=300)
    plt.close()

    sns.scatterplot(data=pd.concat([wfo_results,wcvp_results]), y="Species Discrepancies (%)", x="Synonymisations (%)", hue='Taxonomy')
    plt.savefig(os.path.join('outputs', 'sp_vs_Synonymisations.jpg'), dpi=300)
    plt.close()

if __name__ == '__main__':
    main()
