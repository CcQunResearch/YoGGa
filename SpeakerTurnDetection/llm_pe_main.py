
import time
import pandas as pd
import json
import os
import pandas as pd
import time
import yaml
from tqdm import tqdm
from llm_request import *
from prompts import *
from utils import *
# 一些参数
with open('config.yaml', 'r') as file:
    config = yaml.safe_load(file)
prefix = config['emb_classification_infer']['infer_path_prefix']
seg_span = config['pe_infer']['infer_seg_span']
batch_size = config['pe_infer']['infer_batch_size']
prompt_flag = str(config['pe_infer']['infer_prompt_flag'])
csv_sep = ','

def get_prob_from_csv(input_path):
    start = time.time()
    df = pd.read_csv(input_path,sep=csv_sep)
    prompts = []
    if 'zh_text' in df.columns:
        df.fillna({'zh_text': ''}, inplace=True)
        text_zh = df['zh_text'].tolist()
    elif 'Text' in df.columns:
        df.fillna({'Text': ''}, inplace=True)
        text_zh = df['Text'].tolist()
    else:
        df.fillna({'text': ''}, inplace=True)
        text_zh = df['text'].tolist()
    
    for i in range(0, len(text_zh), seg_span):
        if i+seg_span <= len(text_zh):
            segment = text_zh[i:i+seg_span]
            if i+seg_span < len(text_zh):
                segment = segment + [text_zh[i+seg_span]]
        else:
            segment = text_zh[i:]
        prompts.append({
            "src_zh": segment,
            "instruction": ins("\n".join(segment)) if prompt_flag != 'ab' else ins_ab("\n".join(segment)),
            "output": "",
            "start_index": i,
            "end_index": i+len(segment),
        })
    prompt_batchs = split_into_batches(prompts, batch_size)
    prob_records = []
    for batch in prompt_batchs:
        prob_records.extend(muti_processer(batch))
    df = update_dataframe(df, prob_records)
    output_path = input_path
    df.to_csv(output_path, index=False,sep=csv_sep)
    print(f"file {input_path} processed done, time: {time.time()-start}")

def get_dataset():
    for drama in tqdm(os.listdir(prefix), desc="Processing Dramas"):
        if '.ipynb_checkpoints' not in drama:
            start = time.time()
            print(f"\nProcessing {drama}...")

            for epi in tqdm(os.listdir(os.path.join(prefix, drama, 'csv')), desc=f"{drama} Episodes", leave=False):
                if epi.endswith('.csv'):
                    input_path = os.path.join(prefix, drama, 'csv', epi)
                    get_prob_from_csv(input_path)
            
            print(f"Processing {drama} done, time: {time.time() - start:.2f}s")

get_dataset()