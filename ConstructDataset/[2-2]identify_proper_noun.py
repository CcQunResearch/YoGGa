import requests
import json
import yaml
import time
import os.path as osp
from tqdm import tqdm


def chat(txt, model):
    headers = {'Authorization': 'api_key',
               'Content-Type': 'application/json'}

    q = {"messages": [{"content": txt, "role": "user"}], "model": model}
    q["stream"] = True
    r = requests.post(
        'https://soku-model.alibaba-inc.com/v1/chat/completions',
        json=q,
        headers=headers,
        timeout=600,
        stream=True
    )
    resp_text = ''
    for c in r.iter_lines():
        if c:
            c = c.decode()[6:]
            try:
                c = json.loads(c)
                resp_text += c['choices'][0]['delta']['content']
            except:
                pass
    return resp_text.strip()

model_mapping = {
    "Qwen2.5-72B-Instruct": "qwen2.5-72b-instruct",
    "Qwen2.5-14B-Instruct": "Qwen2.5-14B-Instruct-AWQ"
}

if __name__ == '__main__':
    dirname = osp.dirname(osp.abspath(__file__))
    config_path = osp.join(dirname, '..', 'config.yaml')
    with open(config_path, 'r', encoding='utf-8') as file:
        config = yaml.safe_load(file)
    trpe_model = config['trpe_model']
    lang = config['lang']
    dataset_path = osp.join(dirname, '..', 'LLaMA-Factory', 'data', f'proper_noun_queries_train_{lang}.json')
    output_dir = osp.join(dirname, '..', 'LLaMA-Factory', 'TermRecognition', 'train', trpe_model, lang)
    
    print('Request online service to identify terms...')
    begin_time = time.time()
    generated_predictions = []
    queries = json.load(open(dataset_path, 'r', encoding='utf-8'))
    exception_indexes = []
    for i, query in enumerate(tqdm(queries)):
        prompt = query["instruction"]
        try:
            response = chat(prompt, model_mapping[trpe_model])
        except Exception:  
            exception_indexes.append(i)
            prediction = {"prompt": prompt, "label": "", "predict": "无专有名词"}
        else:
            prediction = {"prompt": prompt, "label": "", "predict": response}
        finally:
            generated_predictions.append(prediction)
    
    final_exception_indexes = []
    if len(exception_indexes) > 0:
        for i in exception_indexes:
            prompt = queries[i]["instruction"]
            try:
                response = chat(prompt, model_mapping[trpe_model])
            except Exception:
                final_exception_indexes.append(i)
            else:
                generated_predictions[i]["predict"] = response
                
    final_exception_indexes_json = osp.join(output_dir, 'final_exception_indexes.jsonl')
    json.dump(final_exception_indexes,  open(final_exception_indexes_json, 'w', encoding='utf-8'), ensure_ascii=False, indent=4)
              
    with open(osp.join(output_dir, 'generated_predictions.jsonl'), 'w', encoding='utf-8') as f:
        for item in generated_predictions:
            f.write(json.dumps(item, ensure_ascii=False) + '\n')
    end_time = time.time()
    print(f'Finished in {end_time - begin_time} seconds.')
    print('Request online service to identify terms.')
    
    
