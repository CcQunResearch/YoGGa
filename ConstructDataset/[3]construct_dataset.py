import os
import os.path as osp
import random
import yaml
import re
import json
from prompt_template import translation_template, proper_noun_slot_dict
from utils import lang_dict, extract_training_queries_and_responses
from yaml_config import save_sft_train_config


if __name__ == '__main__':
    random.seed(42)
    dirname = osp.dirname(osp.abspath(__file__))
    config_path = osp.join(dirname, '..', 'config.yaml')
    with open(config_path, 'r', encoding='utf-8') as file:
        config = yaml.safe_load(file)
    sampling_ratio = config['sampling_ratio']
    merge_audio_path = config['merge_audio_path']
    sft_model = config['sft_model']
    trpe_model = config['trpe_model']
    lang = config['lang']
    model_path = config['model_path']
    src_lang_str = lang_dict[lang.split('2')[0]]
    lang_str = lang_dict[lang.split('2')[1]]
    gpus = config['gpus']
    sft_global_batch_size = config['sft_global_batch_size']
    sft_lr = config['sft_lr']
    sft_epochs = config['sft_epochs']
    info_dir = osp.join(dirname, 'info', lang)
    dialogue_file_names = sorted([file for file in os.listdir(osp.join(info_dir, 'episode_results')) if 'json' in file])

    print('Constructing sft queries and responses...')
    all_data = []
    all_audio_complete_tag = []
    all_fewshot = []
    for dialogue_file_name in dialogue_file_names:
        play_name = dialogue_file_name.strip('.json')
        episode_result = json.load(
            open(osp.join(info_dir, 'episode_results', dialogue_file_name), 'r', encoding='utf-8'))
        proper_noun_dict = json.load(
            open(osp.join(info_dir, 'proper_noun', f'{play_name}_filter.json'), 'r', encoding='utf-8'))
        pn_identify_dict = json.load(
            open(osp.join(info_dir, 'proper_noun', f'{play_name}_identify.json'), 'r', encoding='utf-8'))
        play_data, pn_fewshot = extract_training_queries_and_responses(play_name, episode_result, proper_noun_dict, translation_template, src_lang_str,
                                                                       lang_str, pn_identify_dict=pn_identify_dict, pn_consis=True, merge_audio_path=merge_audio_path)
        
        all_data += play_data
        all_fewshot += pn_fewshot
        
    if len(all_fewshot) == 0:
        all_fewshot.append({"dialogue": re.sub(r'\([^)]*\)', '', proper_noun_slot_dict[lang][-2]), "term": proper_noun_slot_dict[lang][-1]})
    print('Constructing sft queries and responses done.')
    
    sampling_size = int(len(all_data) * sampling_ratio)
    if merge_audio_path:
        candidate_index = [i for i in range(len(all_data)) if all_data[i]["audio complete"]]
        sampled_index = random.sample(candidate_index, sampling_size)
        sft_data = [all_data[i] for i in range(len(all_data)) if i not in sampled_index]
        alignment_data = [all_data[i] for i in sampled_index]
    else:
        random.shuffle(all_data)
        sft_data = all_data[sampling_size:]
        alignment_data = all_data[:sampling_size]

    fewshot_path_json = osp.join(info_dir, f'proper_noun_fewshot_{trpe_model}_{lang}.json')
    fewshot_file_json = open(fewshot_path_json, 'w', encoding='utf-8')
    json.dump(all_fewshot, fewshot_file_json, ensure_ascii=False, indent=4)

    save_path_json = osp.join(dirname, '..', 'LLaMA-Factory', 'data', f'translation_train_{trpe_model}_{lang}.json')
    save_file_json = open(save_path_json, 'w', encoding='utf-8')
    json.dump(sft_data, save_file_json, ensure_ascii=False, indent=4)

    alignment_save_path_json = osp.join(dirname, '..','DPOSampling','raw', f'{trpe_model}_{lang}.json')
    alignment_save_file_json = open(alignment_save_path_json, 'w', encoding='utf-8')
    json.dump(alignment_data, alignment_save_file_json, ensure_ascii=False, indent=4)
    
    gpu_num = len(gpus.split(','))
    batch_size_per_gpu = 3
    gas = sft_global_batch_size // (batch_size_per_gpu * gpu_num)
    assert sft_global_batch_size == batch_size_per_gpu * gpu_num * gas, \
        "global_batch_size must be divisible by train_micro_batch_size_per_gpu * gpu_count"
    save_sft_train_config(model_path, sft_model, trpe_model, lang, gas, sft_lr, sft_epochs)