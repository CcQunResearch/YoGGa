import os
import os.path as osp
import random
import yaml
import json
from prompt_template import proper_noun_train_template, proper_noun_slot_dict
from utils import Trie, proper_noun_retrieve, lang_dict
from yaml_config import save_tr_train_config

def extract_pn_training_queries_and_responses(episode_result, proper_noun_dict, template, pn_fewshot, proper_noun_slot_dict, lang):
    play_data = []

    # 构建词典树
    trie = Trie()
    for word in set(proper_noun_dict.keys()):
        trie.insert(word)

    for _, dialogue in episode_result.items():
        for ce_pair_dict in dialogue:
            ce_pair_list = list(zip(ce_pair_dict["chinese"], ce_pair_dict["target"]))
            dialogue_content = '\n'.join([ce_pair[0] for ce_pair in ce_pair_list])

            proper_noun_list = proper_noun_retrieve(dialogue_content, trie)
            proper_noun_list = sorted(proper_noun_list, key=lambda x: dialogue_content.index(x))
            proper_noun_pairs = [(p, proper_noun_dict[p]['type'], proper_noun_dict[p]['translation']) for p in proper_noun_list]
            proper_noun_content = '\n'.join(
                [f'{pair[0]}（{pair[1]}） - {pair[2]}' for pair in proper_noun_pairs]) if proper_noun_pairs else '无专有名词'
            fewshot = random.choice(pn_fewshot)
            prompt = template.format(*proper_noun_slot_dict[lang][:-2], fewshot["dialogue"], fewshot["term"], dialogue_content)
            response = proper_noun_content
            play_data.append({'instruction': prompt, 'input': None, 'output': response})
    return play_data


if __name__ == '__main__':
    dirname = osp.dirname(osp.abspath(__file__))
    config_path = osp.join(dirname, '..', 'config.yaml')
    with open(config_path, 'r', encoding='utf-8') as file:
        config = yaml.safe_load(file)
    sft_model = config['sft_model']
    trpe_model = config['trpe_model']
    tr_model = config['tr_model']
    model_path = config['model_path']
    lang = config['lang']
    lang_str = lang_dict[lang.split('2')[1]]
    gpus = config['gpus']
    tr_global_batch_size = config['tr_global_batch_size']
    tr_lr = config['tr_lr']
    tr_epochs = config['tr_epochs']
    info_dir = osp.join(dirname, 'info', lang)
    dialogue_file_names = sorted([file for file in os.listdir(osp.join(info_dir, 'episode_results')) if 'json' in file])

    pn_fewshot = json.load(open(osp.join(info_dir, f'proper_noun_fewshot_{trpe_model}_{lang}.json'), 'r', encoding='utf-8'))

    print('Constructing tr queries and responses...')
    all_data = []
    for dialogue_file_name in dialogue_file_names:
        play_name = dialogue_file_name.strip('.json')
        episode_result = json.load(
            open(osp.join(info_dir, 'episode_results', dialogue_file_name), 'r', encoding='utf-8'))
        proper_noun_dict = json.load(
            open(osp.join(info_dir, 'proper_noun', f'{play_name}_filter_tr.json'), 'r', encoding='utf-8'))
        play_data = extract_pn_training_queries_and_responses(episode_result, proper_noun_dict, proper_noun_train_template, pn_fewshot, proper_noun_slot_dict, lang)
        all_data += play_data
    print('Constructing tr queries and responses done.')

    save_path_json = osp.join(dirname, '..', 'LLaMA-Factory', 'data', f'term_recognition_train_{trpe_model}_{lang}.json')
    save_file_json = open(save_path_json, 'w', encoding='utf-8')
    json.dump(all_data, save_file_json, ensure_ascii=False, indent=4)
    
    gpu_num = len(gpus.split(','))
    batch_size_per_gpu = 3
    gas = tr_global_batch_size // (batch_size_per_gpu * gpu_num)
    assert tr_global_batch_size == batch_size_per_gpu * gpu_num * gas, \
        "global_batch_size must be divisible by train_micro_batch_size_per_gpu * gpu_count"
    save_tr_train_config(model_path, tr_model, trpe_model,lang, gas, tr_lr, tr_epochs)
