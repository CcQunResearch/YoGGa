import os
import os.path as osp
import json
import yaml
import shutil
from prompt_template import proper_noun_pe_template, proper_noun_slot_dict
from yaml_config import save_pn_pe_config

def extract_proper_noun_queries(episode_result, template, proper_noun_slot_dict, lang):
    queries = []
    for episode, dialogue in episode_result.items():
        for st_pair_dict in dialogue:
            st_pair_list = list(zip(st_pair_dict["chinese"], st_pair_dict["target"]))
            st_content = '\n'.join([f'{st_pair[0]}({st_pair[1]})' for st_pair in st_pair_list])
            slots = proper_noun_slot_dict[lang]
            query = template.format(*slots, st_content)
            queries.append(query)
    return queries


if __name__ == '__main__':
    dirname = osp.dirname(osp.abspath(__file__))
    config_path = osp.join(dirname, '..', 'config.yaml')
    with open(config_path, 'r', encoding='utf-8') as file:
        config = yaml.safe_load(file)
    trpe_model = config['trpe_model']
    lang = config['lang']
    model_path = config['model_path']
    info_dir = osp.join(dirname, 'info', lang)
    dialogue_file_names = sorted([file for file in os.listdir(osp.join(info_dir, 'episode_results')) if 'json' in file])
    output_dir = osp.join(dirname, '..', 'LLaMA-Factory', 'TermRecognition', 'train', trpe_model, lang)
    os.makedirs(output_dir, exist_ok=True)

    print('Constructing proper noun queries...')
    queries = []
    queries_index = {}
    begin = 0
    for dialogue_file_name in dialogue_file_names:
        play_name = dialogue_file_name.strip('.json')
        episode_result = json.load(
            open(osp.join(info_dir, 'episode_results', dialogue_file_name), 'r', encoding='utf-8'))
        dialogue_queries = extract_proper_noun_queries(episode_result, proper_noun_pe_template, proper_noun_slot_dict, lang)
        for query in dialogue_queries:
            queries.append({"instruction": query, "input": None, "output": None})
        queries_index[play_name] = {"begin": begin, "end": begin + len(dialogue_queries)}
        begin += len(dialogue_queries)
    json.dump(queries, open(osp.join(dirname, '..', 'LLaMA-Factory', 'data', f'proper_noun_queries_train_{lang}.json'), \
                            'w', encoding='utf-8'), ensure_ascii=False, indent=4)
    json.dump(queries_index, open(osp.join(output_dir, f'proper_noun_queries_index.json'), 'w', encoding='utf-8'),
              ensure_ascii=False, indent=4)
    save_pn_pe_config(model_path,trpe_model,lang)
    print('Constructing proper noun queries done.')
