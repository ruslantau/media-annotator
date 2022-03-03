import pandas as pd


def convert_human_to_bytes(size: str):
    power = 2 ** 10
    power_labels = {'': 0, 'K': 1, 'M': 2, 'G': 3, 'T': 4}
    number, label = size[:-1], size[-1]
    return float(number) * power ** power_labels[label]


def get_models_table():
    url = r'https://alphacephei.com/vosk/models'
    tables = pd.read_html(url)
    table = tables[0]
    temp = table[table['Size'].isna()].reset_index().rename(columns={'index': 'n_rows'})
    temp['n_rows'] = temp['n_rows'].rolling(window=2).apply(lambda x: x.iloc[1] - x.iloc[0])
    temp['n_rows'] = temp['n_rows'].shift(-1).fillna(2).astype(int)
    temp['n_rows'] = temp.apply(lambda x: x['n_rows'] * [x.name], axis=1)
    temp = temp.explode('n_rows').reset_index(drop=True)
    table['Language'] = temp['Model']
    table = table[~table['Size'].isna()]
    table['Size_bytes'] = table['Size'].map(convert_human_to_bytes).astype(int)
    table = table.sort_values(['Language', 'Size_bytes'])
    return table
