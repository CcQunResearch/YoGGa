import os
import pandas as pd
import numpy as np
import torch
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor
import os
import pandas as pd
import numpy as np
import torch.nn as nn
import torch
from torch.nn import CosineSimilarity
from tqdm import tqdm
import json
import time
import yaml
# some config
with open('config.yaml', 'r') as file:
    config = yaml.safe_load(file)
prefix = config['construct_dataset_pseudo']['emb_path_prefix']
low_threshold = config['construct_dataset_pseudo']['low_threshold']
high_threshold = config['construct_dataset_pseudo']['high_threshold']
output = 'emb_train_data/'

def get_embedding_path(prefix,drama,file_path):
    path = prefix + drama + '/embedding' + file_path.split('slice')[-1]
    return path.replace('wav','npy')
def save_to_json(data, filename='sft_dataset.json'):
    # print(data[0])
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def process_drama(drama,this_prefix,test_flag=False):
    res = []
    cosine_sim = CosineSimilarity(dim=-1, eps=1e-6)
    alld, effd = 0, 0
    start = time.time()
    if '.ipynb_checkpoints' not in drama:
        for epi in os.listdir(os.path.join(this_prefix, drama, 'csv')):
            if epi.endswith('.csv'):
                file_path = os.path.join(this_prefix, drama, 'csv', epi)
                df = pd.read_csv(file_path)
                
                for i in range(1, len(df)):
                    row1 = df.iloc[i-1]
                    row2 = df.iloc[i]
                    # if pd.notna(row1['files']) and pd.notna(row2['files']):
                    npy_file1 = get_embedding_path(this_prefix,drama,str(row1['files']))
                    npy_file2 = get_embedding_path(this_prefix,drama,str(row2['files']))
                    
                    if os.path.exists(npy_file1) and os.path.exists(npy_file2):
                        
                        embedding1 = np.load(npy_file1)

                        embedding2 = np.load(npy_file2)
                        similarity = cosine_sim(torch.from_numpy(embedding1).unsqueeze(0), torch.from_numpy(embedding2).unsqueeze(0)).item()
                        
                        text1 = row1['zh_text'] if 'zh_text' in row1 else row1['text']
                        text2 = row2['zh_text'] if 'zh_text' in row2 else row2['text']
                        pseudo_label = -1
                        if similarity >= high_threshold:
                            pseudo_label = 1
                        if similarity <= low_threshold:
                            pseudo_label = 0
                        alld += 1
                        if test_flag:
                            if 'spk' in row1:
                                same_speaker = int(row1['spk'] == row2['spk'])  
                            elif '角色' in row1:
                                same_speaker = int(row1['角色'] == row2['角色'])
                            elif 'spk_name' in row1:
                                same_speaker = int(row1['spk_name'] == row2['spk_name'])
                            elif '说话人' in row1:
                                same_speaker = int(row1['说话人'] == row2['说话人'])
                            elem = {"text":text2,"position":f"{drama}-{epi}","emb1": npy_file1, "emb2": npy_file2, "similarity": round(similarity, 4), "label": same_speaker}
                            res.append(elem)
                            effd += 1
                        else:
                            if pseudo_label!=-1:
                                elem = {"emb1": npy_file1, "emb2": npy_file2, "similarity": round(similarity, 4), "label": pseudo_label}
                                res.append(elem)
                                effd += 1

    if alld == 0:
        print(f'No samples found for {drama}')
    else:
        print(f'Finished processing {drama}: {effd}/{alld} rate,---get {len(res)} samples per episode.---time:{time.time()-start}')
    return res

def get_dataset(test_flag=False):
    res = []
    test_prefix = prefix + 'test/' 
    test_dramas = [drama.split('.')[0] for drama in os.listdir(test_prefix)]
    with ThreadPoolExecutor(max_workers=8) as executor:
        if test_flag:
            futures = [executor.submit(process_drama, drama,test_prefix,test_flag) for drama in test_dramas]
        else:
            train_prefix = prefix + 'train/' 
            futures = [executor.submit(process_drama, drama,train_prefix,test_flag) for drama in os.listdir(train_prefix) if drama not in test_dramas]
        for future in futures:
            gX = future.result()
            res.extend(gX)
    return res



start = time.time()
test = get_dataset(test_flag=True)
save_to_json(test, output+'emb_classification_test.json')
print(f'Finished getting test dataset---time:{time.time()-start}')

# train
start = time.time()
train = get_dataset(test_flag=False)
save_to_json(train, output+f'emb_classification_train_{low_threshold}_{high_threshold}.json')
print(f'Finished getting train dataset---time:{time.time()-start}')
