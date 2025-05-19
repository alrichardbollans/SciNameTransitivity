import os.path

import pandas as pd
import seaborn as sns
from matplotlib import pyplot as plt
from scipy import stats

from WFO_methods.get_WFO import all_wfo_version_strings, oldest_wfo_version_string, wfo_version_comparable_to_v10_string, \
    wfo_version_strings_after_v10

repo_path = os.environ.get('KEWSCRATCHPATH')
this_repo_path = os.path.join(repo_path, 'TaxoDrift')
_wcvp_output_path = os.path.join(this_repo_path, 'WCVP_methods', 'outputs')
_wfo_output_path = os.path.join(this_repo_path, 'WFO_methods', 'outputs')


def get_wcvp_species_results():
    data = [['2022-10', 0]]
    version_dict = {'2023-04': 'v11', '2023-09': 'v12', '2024-05': 'v13'}
    for y in version_dict:
        result_df = pd.read_csv(os.path.join(_wcvp_output_path, f'v10_{version_dict[y]}', 'result_summary.csv'), index_col=0)
        species_percent = result_df['Percentages'].loc['species_disagreements']
        print(species_percent)
        data.append([y, species_percent])
    return data


def get_wfo_species_results():
    data = [[oldest_wfo_version_string[:4] + '-' + oldest_wfo_version_string[4:], 0]]
    for y in all_wfo_version_strings:
        if y != oldest_wfo_version_string:
            result_df = pd.read_csv(os.path.join(_wfo_output_path, f'{oldest_wfo_version_string}_{y}', 'result_summary.csv'), index_col=0)
            species_percent = result_df['Percentages'].loc['species_disagreements']
            # print(species_percent)
            y_formatted = y[:4] + '-' + y[4:]
            data.append([y_formatted, species_percent])
    return data


def get_wfo_after_v10_species_results():
    data = [[wfo_version_comparable_to_v10_string[:4] + '-' + wfo_version_comparable_to_v10_string[4:], 0]]
    for y in wfo_version_strings_after_v10:
        if y != wfo_version_comparable_to_v10_string:
            result_df = pd.read_csv(os.path.join(_wfo_output_path, f'{wfo_version_comparable_to_v10_string}_{y}', 'result_summary.csv'), index_col=0)
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

    wfo_after_v10_df = pd.DataFrame(get_wfo_after_v10_species_results(), columns=['Date', 'Species Discrepancy (%)'])
    wfo_after_v10_df['Taxonomy'] = 'WFO (>2022-10)'

    df = pd.concat([wcvp_df, wfo_df, wfo_after_v10_df])
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

    plt.savefig('outputs/species_discrepancy_over_time_forwards.png', dpi=300)


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

    wfo_after_v10_df = get_wfo_after_v10_species_results()

    y = [wfo_after_v10_df.index(c) for c in wfo_after_v10_df[1:]]  ## remove first case as thats a given

    x = [c[1] for c in wfo_after_v10_df[1:]]
    res_exact = do_permutation_spearman_test(x, y)
    print(res_exact)
    print(res_exact.statistic)
    print(res_exact.pvalue)
    out_data.append([res_exact.statistic, res_exact.pvalue, 'WFO (>2022-10)'])

    out_df = pd.DataFrame(out_data, columns=['Spearman Correlation', 'P-value', 'Taxonomy'])
    out_df.to_csv('outputs/spearman_tests_forwards.csv')



if __name__ == '__main__':
    plot_changes()
    spearman_tests()
