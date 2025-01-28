import os
import os.path as osp
import yaml
import json
import shutil
from utils import extract_proper_noun, filter_proper_noun_result, lang_dict, process_assfile_2_csvfile, extract_meta_info, statistic_interval, extract_dialogue_translation, extract_dialogue_translation_nogt, extract_training_queries_and_responses
from prompt_template import translation_template
from yaml_config import save_sft_infer_config


def ass2csv(source_path, target_path, meta_info, src_lang_str, lang_str, evaluation_mode):
    file_names = []
    english_play_name = meta_info['target name']
    for episode in meta_info['episodes']:
        file_names.append(f'{english_play_name}{episode}_{src_lang_str}.ass')
        if evaluation_mode:
            file_names.append(f'{english_play_name}{episode}_{lang_str}.ass')

    for file_name in file_names:
        process_assfile_2_csvfile(source_path, target_path, file_name)


if __name__ == '__main__':
    dirname = osp.dirname(osp.abspath(__file__))
    config_path = osp.join(dirname, '..', 'config.yaml')
    with open(config_path, 'r', encoding='utf-8') as file:
        config = yaml.safe_load(file)
    sft_model = config['sft_model']
    trpe_model = config['trpe_model']
    tr_model = config['tr_model']
    threshold_limit = config['threshold_limit']
    context_len = config['context_len']
    model_path = config['model_path']
    step = config['step']
    lang = config['lang']
    evaluation_mode = config['evaluation_mode']
    src_lang_str = lang_dict[lang.split('2')[0]]
    lang_str = lang_dict[lang.split('2')[1]]
    filter_threshold = config['filter_threshold']

    source_dir = osp.join(dirname, '..', 'Data', lang, 'source(test)')
    data_dir = osp.join(dirname, '..', 'Data', lang,  'test')
    info_dir = osp.join(dirname, 'info', lang)
    os.makedirs(osp.join(info_dir, 'proper_noun'),exist_ok=True)
    output_dir = osp.join(dirname, '..', 'LLaMA-Factory', 'TermRecognition', 'test', f'{tr_model}_{trpe_model}', lang)
    play_names = list(filter(lambda file: file != '.DS_Store', sorted(os.listdir(source_dir))))

    generation_results = []
    with open(osp.join(output_dir, 'generated_predictions.jsonl'), 'r', encoding='utf-8') as f:
        for line in f:
            generation_results.append(json.loads(line))
    queries_index = json.load(open(osp.join(output_dir, 'proper_noun_queries_index.json'), 'r', encoding='utf-8'))

    print('Extract meta info...')
    meta = {}
    for play_name in play_names:
        source_path = osp.join(source_dir, play_name)
        meta_info = extract_meta_info(source_path, src_lang_str, lang_str)
        meta[play_name] = meta_info
    json.dump(meta, open(osp.join(info_dir, 'meta(test).json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=4)
    print('Extract meta info done.')

    print('Ass file to csv...')
    if osp.exists(data_dir):
        shutil.rmtree(data_dir)
    os.makedirs(data_dir)

    for play_name in play_names:
        source_path = osp.join(source_dir, play_name)
        target_path = osp.join(data_dir, play_name)
        os.makedirs(target_path)
        ass2csv(source_path, target_path, meta[play_name], src_lang_str, lang_str, evaluation_mode)
    print('Ass file to csv done.')

    if osp.exists(osp.join(info_dir, 'map_results(test).json')):
        os.remove(osp.join(info_dir, 'map_results(test).json'))
    if evaluation_mode:
        print('Map source to target lang...')
        map_results = {}
        for play_name in play_names:
            target_path = osp.join(data_dir, play_name)
            map_result = statistic_interval(target_path, meta[play_name], src_lang_str, lang_str, threshold_limit=threshold_limit)
            map_results[play_name] = map_result
        json.dump(map_results, open(osp.join(info_dir, 'map_results(test).json'), 'w', encoding='utf-8'),
                ensure_ascii=False, indent=4)
        print('Map source to target lang done.')

    print('Extract dialogue fragment...')
    episode_results_dir = osp.join(info_dir, 'episode_results(test)')
    if osp.exists(episode_results_dir):
        shutil.rmtree(episode_results_dir)       
    os.makedirs(episode_results_dir)
    for play_name in play_names:
        target_path = osp.join(data_dir, play_name)
        if evaluation_mode:
            episode_result = extract_dialogue_translation(target_path, meta[play_name], map_results[play_name],
                                                        src_lang_str, lang_str, context_len=context_len, step=step)
        else:
            episode_result = extract_dialogue_translation_nogt(target_path, meta[play_name], src_lang_str, context_len=context_len, step=step)
        json.dump(episode_result,
                    open(osp.join(episode_results_dir, f'{play_name}.json'), 'w', encoding='utf-8'),
                    ensure_ascii=False, indent=4)
    print('Extract dialogue fragment done.')

    print('Identify proper noun...')
    for play_name in play_names:
        dialogue_results = generation_results[queries_index[play_name]["begin"]:queries_index[play_name]["end"]]
        proper_noun_result = extract_proper_noun(dialogue_results)
        json.dump(proper_noun_result,
                    open(osp.join(info_dir, 'proper_noun', f'{play_name}_identify.json'), 'w',
                        encoding='utf-8'), ensure_ascii=False, indent=4)
    print('Identify proper noun done.')

    print('Filter proper noun...')
    for play_name in play_names:
        proper_noun_result = json.load(
            open(osp.join(info_dir, 'proper_noun', f'{play_name}_identify.json'), 'r', encoding='utf-8'))
        filter_result = filter_proper_noun_result(proper_noun_result, threshold=filter_threshold)
        json.dump(filter_result,
                  open(osp.join(info_dir, 'proper_noun', f'{play_name}_filter.json'), 'w', encoding='utf-8'),
                  ensure_ascii=False, indent=4)
    print('Filter proper noun done.')

    print('Extract test data...')
    dialogue_file_names = sorted(os.listdir(osp.join(info_dir, 'episode_results(test)')))
    all_data = []
    for dialogue_file_name in dialogue_file_names:
        play_name = dialogue_file_name.strip('.json')
        episode_result = json.load(
            open(osp.join(info_dir, 'episode_results(test)', dialogue_file_name), 'r', encoding='utf-8'))
        proper_noun_dict = json.load(
            open(osp.join(info_dir, 'proper_noun', f'{play_name}_filter.json'), 'r', encoding='utf-8'))
        play_data, _ = extract_training_queries_and_responses(play_name, episode_result, proper_noun_dict, translation_template, src_lang_str, lang_str, evaluation_mode=evaluation_mode)
        all_data += play_data
    print('Extract test data done.')

    save_path_json = osp.join(dirname, '..', 'LLaMA-Factory', 'data', f'translation_test_{tr_model}_{trpe_model}_{lang}.json')
    save_file_json = open(save_path_json, 'w', encoding='utf-8')
    json.dump(all_data, save_file_json, ensure_ascii=False, indent=4)
    save_sft_infer_config(model_path, sft_model, tr_model, trpe_model, lang)