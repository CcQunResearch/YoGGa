import requests
import json
import re
from openai import OpenAI
from concurrent.futures import ThreadPoolExecutor
import yaml
# 一些参数
with open('config.yaml', 'r') as file:
    config = yaml.safe_load(file)
prompt_flag = str(config['pe_infer']['infer_prompt_flag'])
model_name = config['pe_infer']['std_pe_model']
if prompt_flag != 'ab':
    label_pool = ['0', '1']
else:
    label_pool = ['A', 'B']

# deepseek v3
def chat_ds3(text, logprobs=False):
    client = OpenAI(api_key="api_key", base_url="base_url")
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": "You are a helpful assistant"},
            {"role": "user", "content": text},
        ],
        stream=False,
        logprobs=logprobs
    )
    
    resp_json = response.to_dict()
    resp_text = resp_json['choices'][0]['message']['content']
    if logprobs:
        probs = resp_json['choices'][0]['logprobs']['content']
        return resp_text, probs
    else:
        return resp_text, None

# qwen2.5-72b-instruct, qwen-max-0428
def chat_qwen(text, model, logprobs=False):
    headers = {'Authorization': 'api_key',
               'Content-Type': 'application/json'}

    q = {"messages": [{"content": text, "role": "user"}], "model": model, "stream": False, "logprobs": logprobs}
    r = requests.post(
        'api_url', # 弹外
        json=q,
        headers=headers,
        timeout=600
    )
    
    resp_json = r.json()
    resp_text = resp_json['choices'][0]['message']['content']
    if logprobs:
        probs = resp_json['choices'][0]['logprobs']['content']
        return resp_text, probs
    else:
        return resp_text, None

# gpt3.5, gpt4o, claude35sonnet
def chat_gpt(text, model, logprobs=False):
    headers = {'Authorization': 'api_key',
               'Content-Type': 'application/json'}

    q = {"messages": [{"content": text, "role": "user"}], "model": model, "stream": False, "logprobs": False}
    r = requests.post(
        'api_url', 
        json=q,
        headers=headers,
        timeout=600
    )
    
    resp_json = r.json()
    resp_text = resp_json['choices'][0]['message']['content']
    if logprobs:
        probs = resp_json['choices'][0]['logprobs']['content']
        return resp_text, probs
    else:
        return resp_text, None

if model_name == 'deepseek-v3':
    chat_func = chat_ds3
elif model_name == 'qwen2.5-72b-instruct':
    chat_func = lambda text, logprobs=False: chat_qwen(text, 'qwen2.5-72b-instruct', logprobs)
elif model_name == 'qwen-max-0428':
    chat_func = lambda text, logprobs=False: chat_qwen(text, 'qwen-max-0428', logprobs)
else:
    chat_func = lambda text, logprobs=False: chat_gpt(text, 'gpt3.5', logprobs)

# 提取 logprobs 中的概率
def extract_probabilities(logprobs):
    probabilities = []
    for index,token_info in enumerate(logprobs):
        if token_info['token'] in label_pool and '<' in logprobs[index-1]['token'] and '>' in logprobs[index+1]['token']:
            probabilities.append({
                'label': token_info['token'],
                'probability': round(10 ** token_info['logprob'], 4)
            })
    return probabilities

# 获取台词标签及概率
def get_label_prob_single(prompt):
    iter_num = 0
    while True:
        iter_num += 1
        if iter_num > 3:
            print("Error: 超过最大迭代次数")
            return []
        result = []
        start_index = prompt['start_index']
        end_index = prompt['end_index']
        last_label = None
        prob_index = 0
        try:
            response_text, logprobs = chat_func(prompt['instruction'], logprobs=True)

            lines = response_text.strip().split('\n')
            probabilities = extract_probabilities(logprobs)
            for line in lines:
                if prompt_flag != 'ab':
                    match = re.match(r'(.*)<(\d|None)>$', line)
                else:
                    match = re.match(r'(.*)<(A|B)>$', line)
                if match:
                    sentence = match.group(1).strip()
                    label = match.group(2).strip()
                    if label in label_pool and prob_index < len(probabilities):
                        prob = probabilities[prob_index]['probability']
                        if prompt_flag!='ab':
                            if label == '0':
                                prob = 1 - prob
                        else:
                            if last_label == None:
                                prob = None
                            else:
                                if last_label != label:
                                    prob = 1 - prob
                        result.append(((start_index, end_index),sentence, prob))
                        prob_index += 1
                    last_label = label
        except:
            print("Error: 返回结果解析失败")
        if result != []:
            return result

def muti_processer(prompts):
    futures = []
    output = []
    with ThreadPoolExecutor(max_workers=len(prompts)) as executor:
        for idx, prompt in enumerate(prompts):
            future = executor.submit(get_label_prob_single, prompt)
            futures.append((idx, future))
    for idx, future in futures:
        output.extend(future.result())

    print(f'muti-{len(output)} sentences have been labeled.')
    return output