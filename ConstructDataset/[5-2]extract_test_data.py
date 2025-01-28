import requests
import json
import yaml
import time
import random
import os.path as osp
from tqdm import tqdm


def get_response_stream(query, port, temperature=0.05, repetition_penalty=1.0, seed=2024):
    q = {
        'model': 'infer', 
        'messages': [
            {"role": "user", "content": query}
        ],
        'temperature': temperature,
        'repetition_penalty': repetition_penalty,
        'seed': seed,
        'stream': True
    }
    
    text = ''
    response = requests.post(
        f'http://0.0.0.0:{port}/v1/chat/completions',
        json=q,
        timeout=600,
        stream=True
    )
    
    for c in response.iter_lines():
        if c:
            c = c.decode()[6:]
            try:
                c = json.loads(c)
                text += c['choices'][0]['delta']['content']
            except Exception as e:
                pass
    return text

model_mapping = {
    "Qwen2.5-72B-Instruct": "qwen2.5-72b-instruct",
    "Qwen2.5-14B-Instruct": "Qwen2.5-14B-Instruct-AWQ"
}

if __name__ == '__main__':
    dirname = osp.dirname(osp.abspath(__file__))
    config_path = osp.join(dirname, '..', 'config.yaml')
    with open(config_path, 'r', encoding='utf-8') as file:
        config = yaml.safe_load(file)
    tr_model = config['tr_model']
    trpe_model = config['trpe_model']
    port = config['port']
    lang = config['lang']
    dataset_path = osp.join(dirname, '..', 'LLaMA-Factory', 'data', f'term_recognition_test_{tr_model}_{trpe_model}_{lang}.json')
    output_dir = osp.join(dirname, '..', 'LLaMA-Factory', 'TermRecognition', 'test', f'{tr_model}_{trpe_model}', lang)
    
    print('Request local service to identify terms...')
    begin_time = time.time()

    generated_predictions = []
    with open(osp.join(output_dir, 'generated_predictions.jsonl'), 'r', encoding='utf-8') as f:
        for line in f:
            generated_predictions.append(json.loads(line))
    
    exception_indexes = []
    for i, prediction in enumerate(generated_predictions):
        response = prediction["predict"]
        if len(response) > 2000:
            exception_indexes.append(i)
    
    final_exception_indexes = []
    if len(exception_indexes) > 0:
        for i in exception_indexes:
            prompt = generated_predictions[i]["prompt"]
            success_tag = False
            fail_count = 0
            retry_num = 5
            print(f'Processing exception index {i}...')
            while not success_tag and fail_count < retry_num:
                try:
                    response = get_response_stream(prompt, port, temperature=random.uniform(0, 0.3))            
                except Exception:
                    fail_count += 1
                    if fail_count == retry_num:
                        final_exception_indexes.append(i)
                else:
                    if len(response) > 2000:
                        fail_count += 1
                        if fail_count == retry_num:
                            final_exception_indexes.append(i)
                    else:
                        success_tag = True
                        generated_predictions[i]["predict"] = response
            if not success_tag:
                print(f'Failed to generate response for exception index {i}.')
            else:
                print(f'Successfully generated response for exception index {i}.')
                
    final_exception_indexes_json = osp.join(output_dir, 'final_exception_indexes.jsonl')
    json.dump(final_exception_indexes, open(final_exception_indexes_json, 'w', encoding='utf-8'), ensure_ascii=False, indent=4)
              
    with open(osp.join(output_dir, 'generated_predictions.jsonl'), 'w', encoding='utf-8') as f:
        for item in generated_predictions:
            f.write(json.dumps(item, ensure_ascii=False) + '\n')
    end_time = time.time()
    print(f'Finished in {end_time - begin_time} seconds.')
    print('Request local service to identify terms.')