import pandas as pd
import numpy as np
import os
import yaml
import shutil

# config
with open('config.yaml', 'r') as file:
    config = yaml.safe_load(file)
prefix = config['emb_classification_infer']['infer_path_prefix']
sep_char = ','


for drama in os.listdir(prefix):
    temp_path = os.path.join(prefix, drama, 'temp')
    if not os.path.exists(temp_path):
        continue
    
    for epi in os.listdir(temp_path):
        csv_files = [f for f in os.listdir(os.path.join(temp_path, epi)) if f.endswith('.csv')]
        combined_df = pd.DataFrame()
        for idx, file in enumerate(csv_files):
            file_path = os.path.join(temp_path, epi, file)
            df = pd.read_csv(file_path, sep=sep_char)
            if combined_df.empty:
                combined_df = df
            else:
                combined_df['prob'] = combined_df['prob'].combine_first(df['prob'])
        
        pe_prob = combined_df['prob'].values
        out_path = os.path.join(prefix, drama, 'csv', f'{epi}.csv')
        if not os.path.exists(os.path.dirname(out_path)):
            os.makedirs(os.path.dirname(out_path))
        out_df = pd.read_csv(out_path, sep=sep_char)
        out_df['pe_prob'] = pe_prob
        out_df.to_csv(out_path, index=False, sep=sep_char)

    shutil.rmtree(temp_path)
