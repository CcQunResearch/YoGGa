import yaml
import json
import os.path as osp

template_dict = {
    'Qwen2.5-7B-Instruct': 'qwen',
    'Qwen2.5-14B-Instruct': 'qwen',
    'Qwen2.5-32B-Instruct': 'qwen',
    'Qwen2.5-72B-Instruct': 'qwen',
    'glm-4-9b-chat': 'glm4',
    'Llama3.1-8B-Chinese-Chat': 'llama3',
    'Meta-Llama-3.1-8B-Instruct': 'llama3',
}

def save_pn_pe_config(model_path, trpe_model, lang):
    dataset_info_file = open(osp.join('..','LLaMA-Factory','data','dataset_info.json'), 'r', encoding='utf-8')
    dataset_info = json.load(dataset_info_file)
    
    dataset_name = f'proper_noun_queries_train_{lang}'
    if dataset_name not in dataset_info:
        dataset_info[dataset_name] = {
            "file_name": f"{dataset_name}.json",
            "columns": {
            "prompt": "instruction",
            "query": "input",
            "response": "output",
            "system": None,
            "history": None
            }
        }
    
    config = {
        'model_name_or_path': osp.join(model_path, 'vanilla', trpe_model),
        'stage': 'sft',
        'do_predict': True,
        'finetuning_type': 'full',
        'eval_dataset': dataset_name,
        'template': template_dict[trpe_model],
        'cutoff_len': 4096,
        'overwrite_cache': True,
        'preprocessing_num_workers': 16,
        'output_dir': f'TermRecognition/train/{trpe_model}/{lang}',
        'overwrite_output_dir': True,
        'per_device_eval_batch_size': 5,
        'predict_with_generate': True
    }
    
    api_config = {
        'model_name_or_path': osp.join(model_path, 'vanilla', trpe_model),
        'template': template_dict[trpe_model]
    }
    
    with open(osp.join('..','LLaMA-Factory','TermRecognition','train',trpe_model,lang,'predict.yaml'), 'w') as file:
        yaml.dump(config, file, default_flow_style=False, allow_unicode=True)
    
    with open(osp.join('..','LLaMA-Factory','TermRecognition','train',trpe_model,lang,'api.yaml'), 'w') as file:
        yaml.dump(api_config, file, default_flow_style=False, allow_unicode=True)
        
    dataset_info_file = open(osp.join('..','LLaMA-Factory','data','dataset_info.json'), 'w', encoding='utf-8')
    json.dump(dataset_info, dataset_info_file, ensure_ascii=False, indent=4)
    
def save_pn_infer_config(model_path, tr_model, trpe_model,lang):
    dataset_info_file = open(osp.join('..','LLaMA-Factory','data','dataset_info.json'), 'r', encoding='utf-8')
    dataset_info = json.load(dataset_info_file)
    
    dataset_name = f'term_recognition_test_{tr_model}_{trpe_model}_{lang}'
    if dataset_name not in dataset_info:
        dataset_info[dataset_name] = {
            "file_name": f"{dataset_name}.json",
            "columns": {
            "prompt": "instruction",
            "query": "input",
            "response": "output",
            "system": None,
            "history": None
            }
        }
    
    config = {
        'model_name_or_path': osp.join(model_path, 'llamafactory', f'{tr_model}_{trpe_model}', lang, 'tr_default'),
        'stage': 'sft',
        'do_predict': True,
        'finetuning_type': 'full',
        'eval_dataset': dataset_name,
        'template': template_dict[tr_model],
        'cutoff_len': 4096,
        'overwrite_cache': True,
        'preprocessing_num_workers': 16,
        'output_dir': f'TermRecognition/test/{tr_model}_{trpe_model}/{lang}',
        'overwrite_output_dir': True,
        'per_device_eval_batch_size': 5,
        'predict_with_generate': True
    }
    
    api_config = {
        'model_name_or_path': osp.join(model_path, 'llamafactory', f'{tr_model}_{trpe_model}', lang, 'tr_default'),
        'template': template_dict[tr_model]
    }
    
    with open(osp.join('..','LLaMA-Factory','TermRecognition','test', f'{tr_model}_{trpe_model}', lang, 'predict.yaml'), 'w') as file:
        yaml.dump(config, file, default_flow_style=False, allow_unicode=True)

    with open(osp.join('..','LLaMA-Factory','TermRecognition','test', f'{tr_model}_{trpe_model}', lang, 'api.yaml'), 'w') as file:
        yaml.dump(api_config, file, default_flow_style=False, allow_unicode=True)  
        
    dataset_info_file = open(osp.join('..','LLaMA-Factory','data','dataset_info.json'), 'w', encoding='utf-8')
    json.dump(dataset_info, dataset_info_file, ensure_ascii=False, indent=4)
    
def save_sft_infer_config(model_path, sft_model, tr_model, trpe_model, lang):
    dataset_info_file = open(osp.join('..','LLaMA-Factory','data','dataset_info.json'), 'r', encoding='utf-8')
    dataset_info = json.load(dataset_info_file)
    
    dataset_name = f'translation_test_{tr_model}_{trpe_model}_{lang}'
    if dataset_name not in dataset_info:
        dataset_info[dataset_name] = {
            "file_name": f"{dataset_name}.json",
            "columns": {
            "prompt": "instruction",
            "query": "input",
            "response": "output",
            "system": None,
            "history": None
            }
        }
    
    config = {
        'model_name_or_path': osp.join(model_path, 'llamafactory', f'{sft_model}_{trpe_model}', lang, 'sft_default'),
        'stage': 'sft',
        'do_predict': True,
        'finetuning_type': 'full',
        'eval_dataset': dataset_name,
        'template': template_dict[sft_model],
        'cutoff_len': 4096,
        'overwrite_cache': True,
        'preprocessing_num_workers': 16,
        'output_dir': f'../ConstructDataset/info/{lang}/inference/test_{sft_model}_{tr_model}_{trpe_model}',
        'overwrite_output_dir': True,
        'per_device_eval_batch_size': 5,
        'predict_with_generate': True
    }
    
    api_config = {
        'model_name_or_path': osp.join(model_path, 'llamafactory', f'{sft_model}_{trpe_model}', lang, 'sft_default'),
        'template': template_dict[sft_model]
    }
    
    with open(osp.join('..','LLaMA-Factory', 'YoukuTranslationSFT', f'predict_{sft_model}_{tr_model}_{trpe_model}_{lang}.yaml'), 'w') as file:
        yaml.dump(config, file, default_flow_style=False, allow_unicode=True)
    
    with open(osp.join('..','LLaMA-Factory', 'YoukuTranslationSFT', f'api_{sft_model}_{tr_model}_{trpe_model}_{lang}.yaml'), 'w') as file:
        yaml.dump(api_config, file, default_flow_style=False, allow_unicode=True)
        
    dataset_info_file = open(osp.join('..','LLaMA-Factory','data','dataset_info.json'), 'w', encoding='utf-8')
    json.dump(dataset_info, dataset_info_file, ensure_ascii=False, indent=4)
    
# def save_sft_pd_infer_config(model_path, sft_model, tr_model, trpe_model, lang):
#     dataset_info_file = open(osp.join('..','LLaMA-Factory','data','dataset_info.json'), 'r', encoding='utf-8')
#     dataset_info = json.load(dataset_info_file)
    
#     dataset_name = f'translation_production_{tr_model}_{trpe_model}_{lang}'
#     if dataset_name not in dataset_info:
#         dataset_info[dataset_name] = {
#             "file_name": f"{dataset_name}.json",
#             "columns": {
#             "prompt": "instruction",
#             "query": "input",
#             "response": "output",
#             "system": None,
#             "history": None
#             }
#         }
    
#     config = {
#         'model_name_or_path': osp.join(model_path, 'llamafactory', sft_model, lang, 'sft_default'),
#         'stage': 'sft',
#         'do_predict': True,
#         'finetuning_type': 'full',
#         'eval_dataset': dataset_name,
#         'template': template_dict[sft_model],
#         'cutoff_len': 4096,
#         'overwrite_cache': True,
#         'preprocessing_num_workers': 16,
#         'output_dir': f'../ConstructDataset/info/{lang}/inference/production_{sft_model}_{tr_model}_{trpe_model}',
#         'overwrite_output_dir': True,
#         'per_device_eval_batch_size': 5,
#         'predict_with_generate': True
#     }
    
#     with open(osp.join('..','LLaMA-Factory', 'YoukuTranslationSFT', f'predict_{sft_model}_{tr_model}_{trpe_model}_{lang}_production.yaml'), 'w') as file:
#         yaml.dump(config, file, default_flow_style=False, allow_unicode=True)
        
#     dataset_info_file = open(osp.join('..','LLaMA-Factory','data','dataset_info.json'), 'w', encoding='utf-8')
#     json.dump(dataset_info, dataset_info_file, ensure_ascii=False, indent=4)
    
# def save_pn_pd_infer_config(model_path, tr_model, trpe_model, lang):
#     dataset_info_file = open(osp.join('..','LLaMA-Factory','data','dataset_info.json'), 'r', encoding='utf-8')
#     dataset_info = json.load(dataset_info_file)
    
#     dataset_name = f'term_recognition_production_{tr_model}_{trpe_model}_{lang}'
#     if dataset_name not in dataset_info:
#         dataset_info[dataset_name] = {
#             "file_name": f"{dataset_name}.json",
#             "columns": {
#             "prompt": "instruction",
#             "query": "input",
#             "response": "output",
#             "system": None,
#             "history": None
#             }
#         }
    
#     config = {
#         'model_name_or_path': osp.join(model_path, 'llamafactory', tr_model, lang, 'tr_default'),
#         'stage': 'sft',
#         'do_predict': True,
#         'finetuning_type': 'full',
#         'eval_dataset': dataset_name,
#         'template': template_dict[tr_model],
#         'cutoff_len': 4096,
#         'overwrite_cache': True,
#         'preprocessing_num_workers': 16,
#         'output_dir': f'TermRecognition/production/{tr_model}_{trpe_model}/{lang}',
#         'overwrite_output_dir': True,
#         'per_device_eval_batch_size': 5,
#         'predict_with_generate': True
#     }
    
#     with open(osp.join('..','LLaMA-Factory','TermRecognition','production', f'{tr_model}_{trpe_model}', lang,'predict.yaml'), 'w') as file:
#         yaml.dump(config, file, default_flow_style=False, allow_unicode=True)
        
#     dataset_info_file = open(osp.join('..','LLaMA-Factory','data','dataset_info.json'), 'w', encoding='utf-8')
#     json.dump(dataset_info, dataset_info_file, ensure_ascii=False, indent=4)
    
def save_sft_train_config(model_path, sft_model, trpe_model, lang, gas, lr, num_epochs):
    dataset_info_file = open(osp.join('..','LLaMA-Factory','data','dataset_info.json'), 'r', encoding='utf-8')
    dataset_info = json.load(dataset_info_file)
    
    dataset_name = f'translation_train_{trpe_model}_{lang}'
    if dataset_name not in dataset_info:
        dataset_info[dataset_name] = {
            "file_name": f"{dataset_name}.json",
            "columns": {
            "prompt": "instruction",
            "query": "input",
            "response": "output",
            "system": None,
            "history": None
            }
        }
    
    config = {
        'model_name_or_path': osp.join(model_path, 'vanilla', sft_model),
        'stage': 'sft',
        'do_train': True,
        'finetuning_type': 'full',
        'deepspeed': 'examples/deepspeed/ds_z3_config.json',
        'dataset': dataset_name,
        'template': template_dict[sft_model],
        'cutoff_len': 4096,
        'overwrite_cache': True,
        'preprocessing_num_workers': 16,
        'output_dir': osp.join(model_path, 'llamafactory', f'{sft_model}_{trpe_model}', lang, 'sft_default'),
        'logging_steps': 10,
        'save_steps': 5000000,
        'plot_loss': True,
        'overwrite_output_dir': True,
        'per_device_train_batch_size': 3,
        'gradient_accumulation_steps': gas,
        'learning_rate': lr,
        'num_train_epochs': num_epochs,
        'lr_scheduler_type': 'cosine',
        'warmup_ratio': 0.1,
        'bf16': True,
        'ddp_timeout': 180000000,
        'val_size': 0.01,
        'per_device_eval_batch_size': 4,
        'eval_strategy': 'steps',
        'eval_steps': 200
    }
    
    with open(osp.join('..','LLaMA-Factory', 'YoukuTranslationSFT', f'sft_{sft_model}_{trpe_model}_{lang}.yaml'), 'w') as file:
        yaml.dump(config, file, default_flow_style=False, allow_unicode=True)
        
    dataset_info_file = open(osp.join('..','LLaMA-Factory','data','dataset_info.json'), 'w', encoding='utf-8')
    json.dump(dataset_info, dataset_info_file, ensure_ascii=False, indent=4)
    
    
def save_tr_train_config(model_path, tr_model,trpe_model, lang, gas, lr, num_epochs):
    dataset_info_file = open(osp.join('..','LLaMA-Factory','data','dataset_info.json'), 'r', encoding='utf-8')
    dataset_info = json.load(dataset_info_file)
    
    dataset_name = f'term_recognition_train_{trpe_model}_{lang}'
    if dataset_name not in dataset_info:
        dataset_info[dataset_name] = {
            "file_name": f"{dataset_name}.json",
            "columns": {
            "prompt": "instruction",
            "query": "input",
            "response": "output",
            "system": None,
            "history": None
            }
        }
    
    config = {
        'model_name_or_path': osp.join(model_path, 'vanilla', tr_model),
        'stage': 'sft',
        'do_train': True,
        'finetuning_type': 'full',
        'deepspeed': 'examples/deepspeed/ds_z3_config.json',
        'dataset': dataset_name,
        'template': template_dict[tr_model],
        'cutoff_len': 4096,
        'overwrite_cache': True,
        'preprocessing_num_workers': 16,
        'output_dir': osp.join(model_path, 'llamafactory', f'{tr_model}_{trpe_model}', lang, 'tr_default'),
        'logging_steps': 10,
        'save_steps': 5000000,
        'plot_loss': True,
        'overwrite_output_dir': True,
        'per_device_train_batch_size': 3,
        'gradient_accumulation_steps': gas,
        'learning_rate': lr,
        'num_train_epochs': num_epochs,
        'lr_scheduler_type': 'cosine',
        'warmup_ratio': 0.1,
        'bf16': True,
        'ddp_timeout': 180000000,
        'val_size': 0.01,
        'per_device_eval_batch_size': 4,
        'eval_strategy': 'steps',
        'eval_steps': 200
    }
    
    with open(osp.join('..','LLaMA-Factory', 'YoukuTranslationSFT', f'tr_{tr_model}_{trpe_model}_{lang}.yaml'), 'w') as file:
        yaml.dump(config, file, default_flow_style=False, allow_unicode=True)
        
    dataset_info_file = open(osp.join('..','LLaMA-Factory','data','dataset_info.json'), 'w', encoding='utf-8')
    json.dump(dataset_info, dataset_info_file, ensure_ascii=False, indent=4)