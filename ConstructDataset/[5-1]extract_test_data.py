import os
import os.path as osp
import random
import json
import shutil
import yaml
import pandas as pd
from utils import lang_dict, process_assfile_2_csvfile
from prompt_template import proper_noun_train_template, proper_noun_slot_dict
from yaml_config import save_pn_infer_config


def ass2csv(source_path, target_path, src_lang_str):
    file_names = [file_name for file_name in sorted(os.listdir(source_path)) if f'{src_lang_str}.ass' in file_name]
    for file_name in file_names:
        process_assfile_2_csvfile(source_path, target_path, file_name)

def extract_proper_noun_queries(target_path, template, pn_fewshot, proper_noun_slot_dict, lang, step=35):
    queries = []
    file_names = sorted(os.listdir(target_path))
    for file_name in file_names:
        file_path = osp.join(target_path, file_name)
        csv_reader = pd.read_csv(open(file_path, 'r', encoding='utf-8'), sep='\t')
        texts = csv_reader['Text'].tolist()

        begin = 0
        end = step
        while begin < len(texts):
            if len(texts[begin:end]) > min(10, step):
                fewshot = random.choice(pn_fewshot)
                query = template.format(*proper_noun_slot_dict[lang][:-2], fewshot["dialogue"], fewshot["term"], '\n'.join(texts[begin:end]))
                queries.append(query)
            begin += step
            end += step
    return queries


if __name__ == '__main__':
    dirname = osp.dirname(osp.abspath(__file__))
    config_path = osp.join(dirname, '..', 'config.yaml')
    with open(config_path, 'r', encoding='utf-8') as file:
        config = yaml.safe_load(file)
    trpe_model = config['trpe_model']
    tr_model = config['tr_model']
    filter_threshold = config['filter_threshold']
    model_path = config['model_path']
    lang = config['lang']
    src_lang_str = lang_dict[lang.split('2')[0]]
    lang_str = lang_dict[lang.split('2')[1]]
    context_len = config['context_len']
    step = config['step']
    proper_noun_step = step + 2 * context_len

    source_dir = osp.join(dirname, '..', 'Data', lang, 'source(test)')
    data_dir = osp.join(dirname, '..', 'Data', lang, 'test')
    info_dir = osp.join(dirname, 'info', lang)
    play_names = list(filter(lambda file: file != '.DS_Store', sorted(os.listdir(source_dir))))
    
    output_dir = osp.join(dirname, '..', 'LLaMA-Factory', 'TermRecognition', 'test', f'{tr_model}_{trpe_model}', lang)
    if osp.exists(output_dir):
        shutil.rmtree(output_dir)
    os.makedirs(output_dir)

    pn_fewshot = json.load(open(osp.join(info_dir, f'proper_noun_fewshot_{trpe_model}_{lang}.json'), 'r', encoding='utf-8'))

    print('Ass file to csv...')
    if osp.exists(data_dir):
        shutil.rmtree(data_dir)
    os.makedirs(data_dir)

    for play_name in play_names:
        source_path = osp.join(source_dir, play_name)
        target_path = osp.join(data_dir, play_name)
        os.makedirs(target_path)
        ass2csv(source_path, target_path, src_lang_str)
    print('Ass file to csv done.')

    print('Constructing tr queries for test set...')
    queries = []
    queries_index = {}
    beigin = 0
    for play_name in play_names:
        target_path = osp.join(data_dir, play_name)
        dialogue_queries = extract_proper_noun_queries(target_path, proper_noun_train_template, pn_fewshot, proper_noun_slot_dict, lang, step=proper_noun_step)
        for query in dialogue_queries:
            queries.append({"instruction": query, "input": None, "output": None})
        queries_index[play_name] = {"begin": beigin, "end": beigin + len(dialogue_queries)}
        beigin += len(dialogue_queries)
    json.dump(queries, open(osp.join(dirname, '..', 'LLaMA-Factory', 'data', f'term_recognition_test_{tr_model}_{trpe_model}_{lang}.json'), 'w', \
                            encoding='utf-8'), ensure_ascii=False, indent=4)
    json.dump(queries_index, open(osp.join(output_dir, 'proper_noun_queries_index.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=4)
    save_pn_infer_config(model_path, tr_model, trpe_model, lang)
    print('Constructing tr queries for test set done.')