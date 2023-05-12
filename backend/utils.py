import json
import pandas as pd
from pathlib import Path


class ProjectManager:
    projects_dict = {}
    max_project_id = None

    def __init__(self, projects_json_path: str or Path):
        self.projects_json_path = Path(projects_json_path)
        assert self.projects_json_path.parent.exists(), FileExistsError("Directory doesn't exist")
        if not self.projects_json_path.exists():
            self.write()
        self.read()

    def read(self):
        with open(self.projects_json_path, mode='r', encoding='utf-8') as f:
            self.projects_dict = json.load(f)
        self.update_last_id()

    def write(self):
        with open(self.projects_json_path, mode='w', encoding='utf-8') as f:
            json.dump(self.projects_dict, f, ensure_ascii=False, indent=4)

    def remove_project(self, id):
        del self.projects_dict[str(id)]
        self.write()
        self.update_last_id()

    def add_project(self, new_data: dict):
        new_data.update({'id': str(new_data['id'])})
        self.projects_dict[str(new_data['id'])] = new_data
        self.write()
        self.update_last_id()

    def update_project(self, new_data: dict):
        new_data.update({'id': str(new_data['id'])})
        self.projects_dict[str(new_data['id'])].update(new_data)
        self.write()

    def update_last_id(self):
        self.max_project_id = max(list(map(int, self.projects_dict.keys())) + [0])


def convert_human_to_bytes(size: str):
    power = 2 ** 10
    power_labels = {'': 0, 'K': 1, 'M': 2, 'G': 3, 'T': 4}
    label_index = [c.isalpha() for c in size].index(True)
    number, label = size[:label_index], size[label_index:]
    return float(number) * power ** power_labels.get(label, 0)


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
    table['Size_bytes'] = table['Size'].map(convert_human_to_bytes).astype(float)
    table = table.sort_values(['Language', 'Size_bytes'])
    return table
