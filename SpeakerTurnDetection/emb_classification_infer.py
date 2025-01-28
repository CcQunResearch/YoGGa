import torch
import torch
import numpy as np
import os
import pandas as pd
from torch.nn import CosineSimilarity
import torch
from concurrent.futures import ThreadPoolExecutor
import yaml
# some config
with open('config.yaml', 'r') as file:
    config = yaml.safe_load(file)
prefix = config['emb_classification_infer']['infer_path_prefix']
low_threshold = config['construct_dataset_pseudo']['low_threshold']
high_threshold = config['construct_dataset_pseudo']['high_threshold']
model_path = f'model_ckpt/emb_classification_train_{low_threshold}_{high_threshold}.pkl'

with open(model_path, 'rb') as f:
    model = torch.load(f)


def get_embedding_path(drama,file_path):
    path = prefix + drama + '/embedding' + file_path.split('slice')[-1]
    return path.replace('wav','npy')

def inference(model, input):
    with torch.no_grad():
        y_pred_proba = model.predict_proba([input])[0][1]
        return y_pred_proba

def process_drama(drama):
    cosine_sim = CosineSimilarity(dim=-1, eps=1e-6)
    paths = os.listdir(os.path.join(prefix, drama, 'csv'))
    print(f"Drama: {drama}, 共{len(paths)}个episode")
    for epi in paths:
        if epi.endswith('.csv'):
            file_path = os.path.join(prefix, drama, 'csv', epi)
            df = pd.read_csv(file_path)
            if 'lg_pred' in df.columns:
                del df['lg_pred']
            df.loc[0, 'lg_pred'] = None
            for i in range(1, len(df)):
                row1 = df.iloc[i-1]
                row2 = df.iloc[i]
                
                npy_file1 = get_embedding_path(drama,str(row1['files']))
                npy_file2 = get_embedding_path(drama,str(row2['files']))
                if os.path.exists(npy_file1) and os.path.exists(npy_file2):
                    embedding1 = np.load(npy_file1)
                    embedding2 = np.load(npy_file2)
                    
                    similarity = cosine_sim(torch.from_numpy(embedding1).unsqueeze(0), torch.from_numpy(embedding2).unsqueeze(0)).item()
                    combined_embedding = np.concatenate([[similarity],embedding1, embedding2])
                    x_test = np.array(combined_embedding)
                    pred = inference(model, x_test)
                    df.loc[i, 'lg_pred'] = float(pred)
                else:
                    print(f"Drama: {drama}, Epi: {epi}, npy文件不存在: {npy_file1}, {npy_file2}")
            df.to_csv(file_path, index=False)
            df = pd.read_csv(file_path)

def get_dataset():
    with ThreadPoolExecutor(max_workers=8) as executor:
        futures = [executor.submit(process_drama, drama) for drama in os.listdir(prefix)]


get_dataset()