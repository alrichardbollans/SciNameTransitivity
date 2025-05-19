import os.path

import pandas as pd
import seaborn as sns
from matplotlib import pyplot as plt
from scipy import stats

from WFO_methods.get_WFO import all_wfo_version_strings, latest_wfo_version_string

repo_path = os.environ.get('KEWSCRATCHPATH')
this_repo_path = os.path.join(repo_path, 'TaxoDrift')
_wcvp_output_path = os.path.join(this_repo_path, 'WCVP_methods', 'outputs')
_wfo_output_path = os.path.join(this_repo_path, 'WFO_methods', 'outputs')


def get_wcvp_species_results():
    data = [['2024-05', 0]]
    version_dict = {'2022-10': 'v10', '2023-04': 'v11', '2023-09': 'v12'}
    for y in version_dict:
        result_df = pd.read_csv(os.path.join(_wcvp_output_path, f'{version_dict[y]}_v13', 'result_summary.csv'), index_col=0)
        species_percent = result_df['Percentages'].loc['species_disagreements']
        print(species_percent)
        data.append([y, species_percent])
    return data


def get_wfo_species_results():
    data = [[latest_wfo_version_string[:4] + '-' + latest_wfo_version_string[4:], 0]]
    for y in all_wfo_version_strings:
        if y != latest_wfo_version_string:
            result_df = pd.read_csv(os.path.join(_wfo_output_path, f'{y}_{latest_wfo_version_string}', 'result_summary.csv'), index_col=0)
            species_percent = result_df['Percentages'].loc['species_disagreements']
            # print(species_percent)
            y_formatted = y[:4] + '-' + y[4:]
            data.append([y_formatted, species_percent])
    return data


def plot_changes():
    # flights = sns.load_dataset("flights")
    sns.set_theme()
    wcvp_df = pd.DataFrame(get_wcvp_species_results(),
                           columns=['Date', 'Species Discrepancy (%)'])
    wcvp_df['Taxonomy'] = 'WCVP'

    wfo_df = pd.DataFrame(get_wfo_species_results(), columns=['Date', 'Species Discrepancy (%)'])
    wfo_df['Taxonomy'] = 'WFO'

    df = pd.concat([wcvp_df, wfo_df])
    df["Date"] = df["Date"].astype(str)
    df = df.sort_values(by='Date', ascending=True)
    df = df.reset_index(drop=True)
    plot = sns.lineplot(
        # ax=ax
        data=df, x="Date", y="Species Discrepancy (%)", hue='Taxonomy'
        # , hue=df["Data"].isna().cumsum()
        # , palette=["blue"] * sum(df["Data"].isna())
    )
    plt.xticks(rotation=30, ha='right')
    plt.tight_layout()
    # ax.set_xticklabels([])

    plt.savefig('outputs/species_discrepancy_over_time_backwards.png', dpi=300)


def do_permutation_spearman_test(x, y):
    def statistic(x):  # permute only `x`

        return stats.spearmanr(x, y).statistic

    res_exact = stats.permutation_test((x,), statistic,

                                       permutation_type='pairings')
    return res_exact


def spearman_tests():
    out_data = []
    wcvp_data = get_wcvp_species_results()

    # Test monotonic relationships of data over time
    y = [wcvp_data.index(c) for c in wcvp_data[1:]]  ## remove first case as thats a given

    x = [c[1] for c in wcvp_data[1:]]
    res_exact = do_permutation_spearman_test(x, y)
    out_data.append([res_exact.statistic, res_exact.pvalue, 'WCVP'])
    print(res_exact)
    print(res_exact.statistic)
    print(res_exact.pvalue)

    wfo_data = get_wfo_species_results()

    y = [wfo_data.index(c) for c in wfo_data[1:]]  ## remove first case as thats a given

    x = [c[1] for c in wfo_data[1:]]
    res_exact = do_permutation_spearman_test(x, y)
    print(res_exact)
    print(res_exact.statistic)
    print(res_exact.pvalue)
    out_data.append([res_exact.statistic, res_exact.pvalue, 'WFO'])

    out_df = pd.DataFrame(out_data, columns=['Spearman Correlation', 'P-value', 'Taxonomy'])
    out_df.to_csv('outputs/spearman_tests_backwards.csv')


if __name__ == '__main__':
    plot_changes()
    spearman_tests()
