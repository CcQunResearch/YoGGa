import time
import yaml
import os
import pandas as pd
import numpy as np

with open('config.yaml', 'r') as file:
    config = yaml.safe_load(file)
prefix = config['emb_classification_infer']['infer_path_prefix']
alpha = config['weighted_fusion']['w']

for drama in os.listdir(prefix):
    for epi in os.listdir(os.path.join(prefix, drama, 'csv')):
        if epi.endswith('.csv'):
            file_path = os.path.join(prefix, drama, 'csv', epi)
            df = pd.read_csv(file_path)

            if 'lg_pred' in df.columns and 'pe_prob' in df.columns:
                df.loc[0, 'lg_pred'] = np.nan
                df.loc[0, 'pe_prob'] = np.nan
                df['lg_pred'] = pd.to_numeric(df['lg_pred'], errors='coerce')
                df['pe_prob'] = pd.to_numeric(df['pe_prob'], errors='coerce')
                # 计算 prob 列
                df['prob'] = df.apply(
                    lambda row: row['lg_pred'] if pd.isnull(row['pe_prob']) else (
                        row['pe_prob'] if pd.isnull(row['lg_pred']) else
                        row['lg_pred'] * alpha + row['pe_prob'] * (1 - alpha)
                    ),
                    axis=1
                )
                df.to_csv(file_path, index=False)

