import os
import os.path as osp
import yaml
import json
import shutil
import random
import pandas as pd
import concurrent.futures
from utils import lang_dict, process_assfile_2_csvfile, statistic_interval, extract_dialogue_translation
from eval import evaluate
from comet import download_model, load_from_checkpoint

def ass2csv(source_path, target_path, meta_info, src_lang_str, lang_str):
    file_names = []
    english_play_name = meta_info['target name']
    for episode in meta_info['episodes']:
        file_names.append(f'{english_play_name}{episode}_{src_lang_str}.ass')
        file_names.append(f'{english_play_name}{episode}_{lang_str}.ass')

    for file_name in file_names:
        process_assfile_2_csvfile(source_path, target_path, file_name)

if __name__ == '__main__':
    # # zh2en, zh2th, ko2zh
    # join_evaluation_list = [
    #     'Qwen2.5-14B-Instruct_Qwen2.5-14B-Instruct_Qwen2.5-72B-Instruct',
    #     'glm-4-9b-chat_Qwen2.5-14B-Instruct_Qwen2.5-72B-Instruct',
    #     'Llama3.1-8B-Chinese-Chat_Qwen2.5-14B-Instruct_Qwen2.5-72B-Instruct'
    # ]
    
    # # ja2zh
    # join_evaluation_list = [
    #     'Qwen2.5-14B-Instruct_Qwen2.5-14B-Instruct_Qwen2.5-14B-Instruct',
    #     'glm-4-9b-chat_Qwen2.5-14B-Instruct_Qwen2.5-14B-Instruct',
    #     'Llama3.1-8B-Chinese-Chat_Qwen2.5-14B-Instruct_Qwen2.5-14B-Instruct'
    # ]
    
    # en2de, en2fr
    join_evaluation_list = [
        'Qwen2.5-14B-Instruct_Qwen2.5-14B-Instruct_Qwen2.5-14B-Instruct',
        'glm-4-9b-chat_Qwen2.5-14B-Instruct_Qwen2.5-14B-Instruct',
        'Meta-Llama-3.1-8B-Instruct_Qwen2.5-14B-Instruct_Qwen2.5-14B-Instruct'
    ]
    
    dirname = osp.dirname(osp.abspath(__file__))
    config_path = osp.join(dirname, '..', 'config.yaml')
    with open(config_path, 'r', encoding='utf-8') as file:
        config = yaml.safe_load(file)
    sft_model = config['sft_model']
    trpe_model = config['trpe_model']
    tr_model = config['tr_model']
    threshold_limit = config['threshold_limit']
    model_path = config['model_path']
    step = config['step']
    lang = config['lang']
    src_lang_str = lang_dict[lang.split('2')[0]]
    lang_str = lang_dict[lang.split('2')[1]]
    evaluate_num = config['evaluate_num']
    evaluate_models = [model.strip() for model in config['evaluate_models'].split(',')]
    evaluate_dimensions = [dimension.strip() for dimension in config['evaluate_dimensions'].split(',')]
    
    source_dir = osp.join(dirname, '..', 'Data', lang, 'source(test)')
    data_dir = osp.join(dirname, '..', 'Data', lang,  'test')
    info_dir = osp.join(dirname, 'info', lang)
    play_names = list(filter(lambda file: file != '.DS_Store', sorted(os.listdir(source_dir))))
    # reference_eval_path = osp.join(info_dir, 'inference', f'{"|".join(play_names)},{"|".join(evaluate_models)},{"|".join(evaluate_dimensions)},{evaluate_num}.json')
    reference_eval_path = osp.join(info_dir, 'inference', f'{lang}.json')
    translation_eval_path = osp.join(info_dir, 'inference', f'test_{sft_model}_{tr_model}_{trpe_model}', 'eval.json')
    
    print('Ass file to csv...')
    if osp.exists(data_dir):
        shutil.rmtree(data_dir)
    os.makedirs(data_dir)

    meta = json.load(open(osp.join(info_dir,'meta(test).json'), 'r', encoding='utf-8'))   
    for play_name in play_names:
        source_path = osp.join(source_dir, play_name)
        target_path = osp.join(data_dir, play_name)
        os.makedirs(target_path)
        ass2csv(source_path, target_path, meta[play_name], src_lang_str, lang_str)
    print('Ass file to csv done.')
    
    print('Map source to target lang...')
    if osp.exists(osp.join(info_dir, 'map_results(evaluation).json')):
        os.remove(osp.join(info_dir, 'map_results(evaluation).json'))
    map_results = {}
    for play_name in play_names:
        target_path = osp.join(data_dir, play_name)
        map_result = statistic_interval(target_path, meta[play_name], src_lang_str, lang_str, threshold_limit=threshold_limit)
        map_results[play_name] = map_result
    json.dump(map_results, open(osp.join(info_dir, 'map_results(evaluation).json'), 'w', encoding='utf-8'),
            ensure_ascii=False, indent=4)
    print('Map source to target lang done.')
    
    print('Extract dialogue fragment...')
    episode_results_dir = osp.join(info_dir, 'episode_results(evaluation)')
    if osp.exists(episode_results_dir):
        shutil.rmtree(episode_results_dir)       
    os.makedirs(episode_results_dir)
    candidate_list = []
    for play_name in play_names:
        target_path = osp.join(data_dir, play_name)
        episode_result = extract_dialogue_translation(target_path, meta[play_name], map_results[play_name], src_lang_str, lang_str, context_len=0, step=step)
        for episode, episode_data in episode_result.items():
            for candidate in episode_data:
                one_evaluate_data = {}
                one_evaluate_data['source'] = candidate['chinese']
                one_evaluate_data['gold reference'] = candidate['target']
                one_evaluate_data['play name'] = play_name
                one_evaluate_data['episode'] = episode
                one_evaluate_data['original line'] = candidate['chinese original line']
                candidate_list.append(one_evaluate_data)
        json.dump(episode_result,
                    open(osp.join(episode_results_dir, f'{play_name}.json'), 'w', encoding='utf-8'),
                    ensure_ascii=False, indent=4)
    print('Extract dialogue fragment done.')

    random.seed(1234)
    random.shuffle(candidate_list)
    
    if osp.exists(reference_eval_path):
        evaluete_reference = False
        reference_eval_results = json.load(open(reference_eval_path, 'r', encoding='utf-8'))
    else:
        evaluete_reference = True
        reference_eval_results = []
    translation_eval_results = []
    total_eval_num = 0
    for i, candidate in enumerate(candidate_list):
        source = candidate['source']
        gold_reference = candidate['gold reference']
        play_name = candidate['play name']
        episode = candidate['episode']
        original_line = candidate['original line']
        begin_index = min(original_line)
        end_index = max(original_line)
        
        if len(join_evaluation_list) > 0:
            dfs = []
            for join_evaluation in join_evaluation_list:
                csv_path = osp.join(info_dir, 'inference', f'test_{join_evaluation}', 'csv', play_name, f'{play_name} {episode}_{lang_str}.csv')
                dfs.append(pd.read_csv(csv_path))
            skip = False
            for df in dfs:
                check_translation = df['译文'].iloc[begin_index - 1:end_index].tolist()
                if pd.Series(check_translation).isnull().any():
                    skip = True
                    break
            if skip:
                continue

        csv_path = osp.join(info_dir, 'inference', f'test_{sft_model}_{tr_model}_{trpe_model}', 'csv', play_name, f'{play_name} {episode}_{lang_str}.csv')
        df = pd.read_csv(csv_path)
        translation = df['译文'].iloc[begin_index - 1:end_index].tolist()
        
        if pd.Series(translation).isnull().any():
            continue
        
        if evaluete_reference:
            src = '\n'.join(source)
            ref = '\n'.join(gold_reference)
            refer_eval_result = {'src': src, 'ref': ref,  'scores':{}}
            ref_tasks = []
            for dimension in evaluate_dimensions:
                refer_eval_result['scores'][dimension] = {}
                for model in evaluate_models:
                    ref_tasks.append([model, lang, src, ref, dimension])
            
            with concurrent.futures.ThreadPoolExecutor(max_workers=len(ref_tasks)) as executor:
                futures = [executor.submit(evaluate, *para) for para in ref_tasks]
                concurrent.futures.wait(futures) 
                for future in futures:
                    score, para = future.result()
                    refer_eval_result['scores'][para['dimension']][para['model']] = score
                    
            reference_eval_results.append(refer_eval_result)
        else:
            refer_eval_result = reference_eval_results[total_eval_num]
            
        src = '\n'.join(source)
        tgt = '\n'.join(translation)
        translation_eval_result = {'src': src, 'ref': refer_eval_result['ref'], 'tgt': tgt, 'ref scores': refer_eval_result['scores'], 'tgt scores':{}}
        tgt_tasks = []
        for dimension in evaluate_dimensions:
            translation_eval_result['tgt scores'][dimension] = {}
            for model in evaluate_models:
                tgt_tasks.append([model, lang, src, tgt, dimension])
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=len(tgt_tasks)) as executor:
            futures = [executor.submit(evaluate, *para) for para in tgt_tasks]
            concurrent.futures.wait(futures) 
            for future in futures:
                score, para = future.result()
                translation_eval_result['tgt scores'][para['dimension']][para['model']] = score        
        
        translation_eval_results.append(translation_eval_result)
        
        total_eval_num += 1
        print(f'Evaluating {total_eval_num}/{evaluate_num} translations done.')
        if total_eval_num == evaluate_num:
            break
    
    eval = {'total eval num': total_eval_num, 'ref': {}, 'tgt': {}, 'evaluation': translation_eval_results}
    for dimension in evaluate_dimensions:
        eval['tgt'][dimension] = {}
        eval['ref'][dimension] = {}
        for model in evaluate_models:
            all_translation_scores = []
            all_reference_scores = []
            for translation_eval_result in translation_eval_results:
                all_translation_scores.append(translation_eval_result['tgt scores'][dimension][model])
                all_reference_scores.append(translation_eval_result['ref scores'][dimension][model])
            avg_translation_score = sum(all_translation_scores) / len(all_translation_scores)
            avg_reference_score = sum(all_reference_scores) / len(all_reference_scores)
            eval['tgt'][dimension][model] = avg_translation_score
            eval['ref'][dimension][model] = avg_reference_score
        
    if 'acc' in evaluate_dimensions:
        ref_data = []
        tgt_data = []
        for translation_eval_result in translation_eval_results:
            src = translation_eval_result['src']
            ref = translation_eval_result['ref']
            tgt = translation_eval_result['tgt']
            for i in range(len(src.split("\n"))):
                ref_data.append({"src": src.split("\n")[i], "mt": ref.split("\n")[i]})
                tgt_data.append({"src": src.split("\n")[i], "mt": tgt.split("\n")[i]})
        
        model_path = download_model("Unbabel/XCOMET-XXL")
        model = load_from_checkpoint(model_path)
        
        ref_model_output = model.predict(ref_data, batch_size=8, gpus=1)
        ref_xcomet_score = ref_model_output.system_score * 100
        tgt_model_output = model.predict(tgt_data, batch_size=8, gpus=1)
        tgt_xcomet_score = tgt_model_output.system_score * 100
        
        eval['ref']['acc']['xcomet'] = ref_xcomet_score
        eval['tgt']['acc']['xcomet'] = tgt_xcomet_score
        
    for dimension in evaluate_dimensions:
        if dimension == 'acc':
            all_model_ref_scores = [eval['ref']['acc']['xcomet']]
            all_model_tgt_scores = [eval['tgt']['acc']['xcomet']]
        else:
            all_model_ref_scores = []
            all_model_tgt_scores = []
        for model in evaluate_models:
            all_model_ref_scores.append(eval['ref'][dimension][model])
            all_model_tgt_scores.append(eval['tgt'][dimension][model])
        eval['tgt'][dimension]['avg'] = sum(all_model_tgt_scores) / len(all_model_tgt_scores)
        eval['ref'][dimension]['avg'] = sum(all_model_ref_scores) / len(all_model_ref_scores)
    
    json.dump(eval, open(translation_eval_path, 'w', encoding='utf-8'), ensure_ascii=False, indent=4)
    json.dump(reference_eval_results, open(reference_eval_path, 'w', encoding='utf-8'), ensure_ascii=False, indent=4)