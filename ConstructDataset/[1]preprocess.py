import os
import os.path as osp
import shutil
import json
import yaml
from utils import lang_dict,extract_meta_info, process_assfile_2_csvfile,statistic_interval,extract_dialogue_translation


def align_file_names(source_path):
    file_names = sorted(os.listdir(source_path))
    for file_name in file_names:
        file_path = osp.join(source_path, file_name)
        file_name = file_name.replace('\xa0', ' ')
        new_file_path = osp.join(source_path, file_name.strip())
        os.rename(file_path, new_file_path)


def ass2csv(source_path, target_path, meta_info, src_lang_str, lang_str, audio_path=None, merge_audio_path=False):
    target_play_name = meta_info['target name']
    for episode in meta_info['episodes']:
        file_name = f'{target_play_name}{episode}_{src_lang_str}.ass'
        if merge_audio_path:
            audio_csv_path = osp.join(audio_path, f'{int(episode)}.csv')
            process_assfile_2_csvfile(source_path, target_path, file_name, audio_csv_path, merge_audio_path)
        else:
            process_assfile_2_csvfile(source_path, target_path, file_name)
    
    for episode in meta_info['episodes']:      
        file_name = f'{target_play_name}{episode}_{lang_str}.ass'
        process_assfile_2_csvfile(source_path, target_path, file_name)

if __name__ == '__main__':
    dirname = osp.dirname(osp.abspath(__file__))
    config_path = osp.join(dirname, '..', 'config.yaml')
    with open(config_path, 'r', encoding='utf-8') as file:
        config = yaml.safe_load(file)
    threshold_limit = config['threshold_limit']
    context_len = config['context_len']
    as_data_path = config['as_data_path']
    merge_audio_path = config['merge_audio_path']
    step = config['step']
    lang = config['lang']
    src_lang_str = lang_dict[lang.split('2')[0]]
    lang_str = lang_dict[lang.split('2')[1]]
    if src_lang_str != '简体中文':
        merge_audio_path = False
        
    model_path = config['model_path']
    os.makedirs(osp.join(model_path, 'vanilla'), exist_ok=True)
    os.makedirs(osp.join(model_path, 'llamafactory'), exist_ok=True)
    os.makedirs(osp.join(model_path, 'alignment'), exist_ok=True)

    source_dir = osp.join(dirname, '..', 'Data', lang, 'source(train)')
    data_dir = osp.join(dirname, '..', 'Data', lang,'train')
    info_dir = osp.join(dirname, 'info', lang)
    play_names = list(filter(lambda file: file != '.DS_Store', sorted(os.listdir(source_dir))))

    print('Align file names...')
    for play_name in play_names:
        source_path = osp.join(source_dir, play_name)
        align_file_names(source_path)
    print('Align file names done.')

    print('Extract meta info...')
    if osp.exists(info_dir):
        shutil.rmtree(info_dir)
    os.makedirs(info_dir)
    
    meta = {}
    for play_name in play_names:
        source_path = osp.join(source_dir, play_name)
        meta_info = extract_meta_info(source_path, src_lang_str, lang_str)
        meta[play_name] = meta_info
    json.dump(meta, open(osp.join(info_dir, 'meta.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=4)
    print('Extract meta info done.')

    print('Ass file to csv...')
    if osp.exists(data_dir):
        shutil.rmtree(data_dir)
    os.makedirs(data_dir)

    for play_name in play_names:
        source_path = osp.join(source_dir, play_name)
        target_path = osp.join(data_dir, play_name)
        os.makedirs(target_path)
        audio_path = osp.join(as_data_path, 'separate_backup', 'train', play_name, 'csv')
        ass2csv(source_path, target_path, meta[play_name], src_lang_str, lang_str, audio_path, merge_audio_path)
    print('Ass file to csv done.')

    print('Map source to target lang...')
    map_results = {}
    for play_name in play_names:
        target_path = osp.join(data_dir, play_name)
        map_result = statistic_interval(target_path, meta[play_name], src_lang_str, lang_str, threshold_limit=threshold_limit)
        map_results[play_name] = map_result
    json.dump(map_results, open(osp.join(info_dir, 'map_results.json'), 'w', encoding='utf-8'),
              ensure_ascii=False, indent=4)
    print('Map source to target lang done.')

    print('Extract dialogue fragment...')
    episode_results_dir = osp.join(info_dir, 'episode_results')
    if osp.exists(episode_results_dir):
        shutil.rmtree(episode_results_dir)
    os.makedirs(episode_results_dir)
    for play_name in play_names:
        target_path = osp.join(data_dir, play_name)
        episode_result = extract_dialogue_translation(target_path, meta[play_name], map_results[play_name], src_lang_str,
                                                      lang_str, context_len=context_len, step=step, merge_audio_path=merge_audio_path)
        json.dump(episode_result,
                  open(osp.join(episode_results_dir, f'{play_name}.json'), 'w', encoding='utf-8'),
                  ensure_ascii=False, indent=4)
    print('Extract dialogue fragment done.')
