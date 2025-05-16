import os.path

import numpy as np
import pandas as pd
import seaborn as sns
from matplotlib import pyplot as plt

from WFO_methods.get_WFO import all_wfo_version_strings, oldest_wfo_version_string

repo_path = os.environ.get('KEWSCRATCHPATH')
this_repo_path = os.path.join(repo_path, 'TaxoDrift')
_wcvp_output_path = os.path.join(this_repo_path, 'WCVP_methods', 'outputs')
_wfo_output_path = os.path.join(this_repo_path, 'WFO_methods', 'outputs')

def get_wcvp_species_results():
    data = [['2022-10',0]]
    version_dict = {'2023-04':'v11', '2023-09': 'v12', '2024-05':'v13'}
    for y in version_dict:
        result_df = pd.read_csv(os.path.join(_wcvp_output_path, f'v10_{version_dict[y]}','result_summary.csv'), index_col=0)
        species_percent = result_df['Percentages'].loc['species_disagreements']
        print(species_percent)
        data.append([y, species_percent])
    return data

def get_wfo_species_results():
    data = [[oldest_wfo_version_string,0]]
    for y in all_wfo_version_strings:
        if y != oldest_wfo_version_string:
            result_df = pd.read_csv(os.path.join(_wfo_output_path, f'{oldest_wfo_version_string}_{y}','result_summary.csv'), index_col=0)
            species_percent = result_df['Percentages'].loc['species_disagreements']
            print(species_percent)
            y_formatted = y[:4] + '-' + y[4:]
            data.append([y_formatted, species_percent])
    return data

def plot_changes():
    # flights = sns.load_dataset("flights")

    wcvp_df = pd.DataFrame(get_wcvp_species_results(),
                           columns=['Year', 'Species Discrepancy (%)'])
    wcvp_df['Taxonomy'] = 'WCVP'

    wfo_df = pd.DataFrame(get_wfo_species_results(), columns=['Year', 'Species Discrepancy (%)'])
    wfo_df['Taxonomy'] = 'WFO'

    df = pd.concat([wcvp_df, wfo_df])
    df["Year"] = df["Year"].astype(str)
    df = df.sort_values(by='Year', ascending=True)
    df = df.reset_index(drop=True)
    plot = sns.lineplot(
        # ax=ax
        data=df, x="Year", y="Species Discrepancy (%)", hue='Taxonomy'
        # , hue=df["Data"].isna().cumsum()
        # , palette=["blue"] * sum(df["Data"].isna())
    )

    # ax.set_xticklabels([])

    plt.show()


if __name__ == '__main__':
    plot_changes()
