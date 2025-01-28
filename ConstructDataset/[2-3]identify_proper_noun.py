import os
import os.path as osp
import json
import yaml
from utils import extract_proper_noun, filter_proper_noun_result, easy_filter_proper_noun_result

if __name__ == '__main__':
    dirname = osp.dirname(osp.abspath(__file__))
    config_path = osp.join(dirname, '..', 'config.yaml')
    with open(config_path, 'r', encoding='utf-8') as file:
        config = yaml.safe_load(file)
    filter_threshold = config['filter_threshold']
    trpe_model = config['trpe_model']
    lang = config['lang']

    dirname = osp.dirname(osp.abspath(__file__))
    tr_dir = osp.join(dirname, '..', 'LLaMA-Factory', 'TermRecognition', 'train', trpe_model, lang)
    info_dir = osp.join(dirname, 'info', lang)
    os.makedirs(osp.join(info_dir, 'proper_noun'), exist_ok=True)
    dialogue_file_names = sorted([file for file in os.listdir(osp.join(info_dir, 'episode_results')) if 'json' in file])

    generation_results = []
    with open(osp.join(tr_dir,'generated_predictions.jsonl'), 'r', encoding='utf-8') as f:
        for line in f:
            generation_results.append(json.loads(line))
    queries_index = json.load(open(osp.join(tr_dir, 'proper_noun_queries_index.json'), 'r', encoding='utf-8'))

    print('Identify proper noun...')
    for dialogue_file_name in dialogue_file_names:
        play_name = dialogue_file_name.strip('.json')
        episode_result = json.load(open(osp.join(info_dir, 'episode_results', dialogue_file_name), 'r', encoding='utf-8'))
        dialogue_results = generation_results[queries_index[play_name]["begin"]:queries_index[play_name]["end"]]
        proper_noun_result = extract_proper_noun(dialogue_results)
        json.dump(proper_noun_result, open(osp.join(info_dir, 'proper_noun', f'{play_name}_identify.json'), 'w',
                        encoding='utf-8'), ensure_ascii=False, indent=4)
    print('Identify proper noun done.')

    print('Filter proper noun...')
    for dialogue_file_name in dialogue_file_names:
        play_name = dialogue_file_name.strip('.json')
        proper_noun_result = json.load(
            open(osp.join(info_dir, 'proper_noun', f'{play_name}_identify.json'), 'r', encoding='utf-8'))
        filter_result = filter_proper_noun_result(proper_noun_result, threshold=filter_threshold)
        json.dump(filter_result,
                  open(osp.join(info_dir, 'proper_noun', f'{play_name}_filter.json'), 'w', encoding='utf-8'),
                  ensure_ascii=False, indent=4)
        easy_filter_result = easy_filter_proper_noun_result(proper_noun_result)
        json.dump(easy_filter_result,
                  open(osp.join(info_dir, 'proper_noun', f'{play_name}_filter_tr.json'), 'w', encoding='utf-8'),
                  ensure_ascii=False, indent=4)
    print('Filter proper noun done.')
