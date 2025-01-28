import requests
import json
import re
from openai import OpenAI

# qwen2.5-72b-instruct, qwen-max-0428
def chat_qwen(text, model, logprobs=False):
    headers = {'Authorization': 'api_key',
               'Content-Type': 'application/json'}

    q = {"messages": [{"content": text, "role": "user"}], "model": model, "stream": False, "logprobs": logprobs}
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

# deepseek v3
def chat_ds3(text, logprobs=False):
    client = OpenAI(api_key="api_key", base_url="api_url")
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

def extract_json_from_string(long_string):
    json_pattern = r'\{.*?\}'
    
    match = re.search(json_pattern, long_string)
    if match:
        json_data = match.group()
        try:
            return json.loads(json_data)
        except json.JSONDecodeError:
            print(f"提取的字符串不是有效的JSON格式:{long_string}")
    return None


output_format_zh = '{"Score": 评分}'
output_format_en = '{"Score": evaluation score}'

# 中文模型准确性评估
acc_prompt_zh = lambda src2tgt, src_lang, tgt_lang, src, tgt: f'''【{src2tgt}台词翻译准确性评估】

请对以下{src2tgt}台词翻译的准确性打分，打分采用0到100的整数评分。台词翻译准确性评分标准包括评估{tgt_lang}翻译是否准确传达了{src_lang}原台词的原始意义。另外，需要关注{src_lang}原台词中的术语（例如人名、地名、机构、物品等专有名词）是否在{tgt_lang}译文中得到准确翻译。
评分标准（准确性）：
100：翻译完全准确，涵盖了所有信息，并提供了连贯的译文，且专有名词翻译准确。
50：翻译大部分准确，只有轻微的遗漏或上下文不清，专有名词翻译部分不准确，但整体仍然可理解。
0：翻译严重扭曲，误解了原文的主要意思，且专有名词翻译效果不佳。

{src_lang}原文：
{src}

{tgt_lang}翻译：
{tgt}

注意：你需要以json格式输出评分：{output_format_zh}
评分（只需输出评分即可，无需过多解释）：'''

# 中文模型自然度评估
nat_prompt_zh = lambda src2tgt, src_lang, tgt_lang, src, tgt: f'''【{src2tgt}台词翻译自然度评估】

请对以下{src2tgt}台词翻译的自然度打分，打分采用0到100的整数评分。台词翻译自然度评分标准考虑的是译文是否充分考虑了语境因素，包括文化背景、语境等，是否保证语言表达自然流畅，符合{tgt_lang}的语法结构和用词习惯，使译文易于理解，贴近{tgt_lang}受众的文化和表达习惯。
评分标准（自然度）：
100：译文充分考虑了语境和文化背景，语言流畅自然，符合{tgt_lang}的习惯用法，没有语法和单词错误。
50：译文考虑了语境，表达基本流畅，但个别表达略微生硬或不自然，可能有轻微的语法错误。
0：译文没有有效地考虑语境或文化，表达不流畅，语法错误多，翻译生硬，难以理解。

{src_lang}原文：
{src}

{tgt_lang}翻译：
{tgt}

注意：你需要以json格式输出评分：{output_format_zh}
评分（只需输出评分即可，无需过多解释）：'''

# 中文模型生动性评估
vivi_prompt_zh = lambda src2tgt, src_lang, tgt_lang, src, tgt: f'''【{src2tgt}台词翻译生动性评估】

请对以下{src2tgt}台词翻译的生动性打分，打分采用0到100的整数评分。台词翻译生动性评分标准不考虑译文的翻译准确性，仅评估译文是否具有表现力，情感是否丰富，是否更容易打动观众。
评分标准（生动性）：
100：翻译极具表现力和感染力，情感丰富，能够强烈打动观众。
50：翻译具有一定表现力，情感表达较为平淡，但仍能传递部分情感。
0：翻译缺乏表现力和情感，无法引起观众的任何情感共鸣。

{src_lang}原文：
{src}

{tgt_lang}翻译：
{tgt}

注意：你需要以json格式输出评分：{output_format_zh}
评分（只需输出评分即可，无需过多解释）：'''

# 英文模型准确性评估
acc_prompt_en = lambda src2tgt, src_lang, tgt_lang, src, tgt: f'''[{src2tgt} Dialogue Translation Accuracy Evaluation]

Please rate the accuracy of the following {src2tgt} dialogue translation, using integer scores from 0 to 100. The translation accuracy rating criteria include evaluating whether the {tgt_lang} translation accurately conveys the original meaning of the {src_lang} dialogue. Additionally, pay attention to whether the terminology (e.g., names of people, places, organizations, items, etc.) in the {src_lang} original dialogue is accurately translated in the {tgt_lang} translation.
Scoring Criteria (Accuracy):
100: The translation is completely accurate, covers all information, provides a coherent translation, and the proper nouns are accurately translated.
50: The translation is mostly accurate, with only minor omissions or unclear context, and proper nouns are partially inaccurately translated, but the overall meaning is still understandable.
0: The translation is severely distorted, misinterprets the main meaning of the original text, and the translation of proper nouns is poor.

Original {src_lang} Text:
{src}

{tgt_lang} Translation:
{tgt}

Note: You need to output the score in JSON format: {output_format_en}
Score (only output the score, no further explanation required):'''

# 英文模型自然度评估
nat_prompt_en = lambda src2tgt, src_lang, tgt_lang, src, tgt: f'''[{src2tgt} Dialogue Translation Naturalness Evaluation]

Please rate the naturalness of the following {src2tgt} dialogue translation using an integer score from 0 to 100. The naturalness score of the dialogue translation should consider whether the translated text adequately takes into account contextual factors, including cultural background and context, and whether it ensures natural and fluent language expression that conforms to {tgt_lang} grammatical structures and word usage habits. It should be easy to understand and close to the culture and expression habits of the {tgt_lang} audience.
Scoring Criteria (Naturalness):
100: The translation fully considers context and cultural background, with smooth and natural language that aligns with {tgt_lang} usage habits, and contains no grammatical or lexical errors.
50: The translation considers the context and is basically fluent, but some expressions may be slightly awkward or unnatural, with potential minor grammatical errors.
0: The translation does not effectively consider the context or culture, is not fluent, has many grammatical errors, is rigid, and difficult to understand.

Original {src_lang} Text:
{src}

{tgt_lang} Translation:
{tgt}

Note: You need to output the score in JSON format: {output_format_en}
Score (only output the score, no further explanation required):'''

# 英文模型生动性评估
vivi_prompt_en = lambda src2tgt, src_lang, tgt_lang, src, tgt: f'''[{src2tgt} Dialogue Translation Vividness Evaluation]

Please rate the vividness of the {src2tgt} dialogue translation below, using an integer score from 0 to 100. The score for translation vividness does not take into account the accuracy of the translation; it only evaluates whether the translation is expressive, emotionally rich, and more capable of engaging the audience.
Scoring Criteria (Vividness):
100: The translation is highly expressive and impactful, with rich emotions, capable of strongly moving the audience.
50: The translation has some expressiveness, and the emotional expression is relatively flat but still conveys some emotion.
0: The translation lacks expressiveness and emotion, failing to evoke any emotional resonance from the audience.

Original {src_lang} Text:
{src}

{tgt_lang} Translation:
{tgt}

Note: You need to output the score in JSON format: {output_format_en}
Score (only output the score, no further explanation required):'''

lang_2_zh = {
    'zh2en': '中译英',
    'zh2es': '中译西',
    'zh2pt': '中译葡',
    'zh2ms': '中译马',
    'zh2id': '中译印',
    'zh2vi': '中译越',
    'zh2th': '中译泰',
    'ko2zh': '韩译中',
    'ja2zh': '日译中',
    'en2zh': '英译中',
    'en2es': '英译西',
    'en2de': '英译德',
    'en2fr': '英译法',
}

lang_2_en = {
    'zh2en': 'Chinese to English',
    'zh2es': 'Chinese to Spanish',
    'zh2pt': 'Chinese to Portuguese',
    'zh2ms': 'Chinese to Malay',
    'zh2id': 'Chinese to Indonesian',
    'zh2vi': 'Chinese to Vietnamese',
    'zh2th': 'Chinese to Thai',
    'ko2zh': 'Korean to Chinese',
    'ja2zh': 'Japanese to Chinese',
    'en2zh': 'English to Chinese',
    'en2es': 'English to Spanish',
    'en2de': 'English to German',
    'en2fr': 'English to French',
}

lang_dict_zh = {
    'zh': '中文',
    'en': '英语',
    'es': '西班牙语',
    'pt': '葡萄牙语',
    'ms': '马来西亚语',
    'id': '印度尼西亚语',
    'vi': '越南语',
    'th': '泰语',
    'ko': '韩语',
    'ja': '日语',
    'de': '德语',
    'fr': '法语',
}

lang_dict_en = {
    'zh': 'Chinese',
    'en': 'English',
    'es': 'Spanish',
    'pt': 'Portuguese',
    'ms': 'Malay',
    'id': 'Indonesian',
    'vi': 'Vietnamese',
    'th': 'Thai',
    'ko': 'Korean',
    'ja': 'Japanese',
    'de': 'German',
    'fr': 'French',
}

gpt_model_dict = {
    "gpt3.5": "idealab-soku-gpt-3.5-16K",
    "gpt4o": "idealab-soku-gpt-4o-0806-global",
    "claude35sonnet": "idealab-soku-claude35_sonnet"
}

def evaluate(model, lang, src, tgt, dimension):
    para = {'model': model, 'lang': lang,'src': src, 'tgt': tgt, 'dimension': dimension}
    if model in ['qwen2.5-72b-instruct', 'qwen-max-0428', 'deepseek-v3']:
        src2tgt = lang_2_zh[lang]
        src_lang = lang_dict_zh[lang.split('2')[0]]
        tgt_lang = lang_dict_zh[lang.split('2')[1]]
        if dimension == 'acc':
            prompt = acc_prompt_zh(src2tgt, src_lang, tgt_lang, src, tgt)
        elif dimension == 'vivi':
            prompt = vivi_prompt_zh(src2tgt, src_lang, tgt_lang, src, tgt)
        elif dimension == 'nat':
            prompt = nat_prompt_zh(src2tgt, src_lang, tgt_lang, src, tgt)
        else:
            raise ValueError(f'Unsupported dimension: {dimension}')
        
        iter = 0
        while True:
            try:
                if model != 'deepseek-v3':
                    result, _ = chat_qwen(prompt, model)
                else:
                    result, _  = chat_ds3(prompt)
                res =  extract_json_from_string(result)
            except Exception as e:
                print(f"{model}发生异常：{e}")
                res = None
            finally:
                if res:
                    if 'Score' in res:
                        return int(res['Score']), para
                    elif 'score' in res:
                        return int(res['score']), para
                iter += 1 
                if iter > 5:
                    return None, para
        
    elif model in ['gpt3.5', 'gpt4o', 'claude35sonnet']:
        src2tgt = lang_2_en[lang]
        src_lang = lang_dict_en[lang.split('2')[0]]
        tgt_lang = lang_dict_en[lang.split('2')[1]]
        if dimension == 'acc':
            prompt = acc_prompt_en(src2tgt, src_lang, tgt_lang, src, tgt)
        elif dimension == 'vivi':
            prompt = vivi_prompt_en(src2tgt, src_lang, tgt_lang, src, tgt)
        elif dimension == 'nat':
            prompt = nat_prompt_en(src2tgt, src_lang, tgt_lang, src, tgt)
        else:
            raise ValueError(f'Unsupported dimension: {dimension}')
        
        iter = 0
        while True:
            try:
                result, _ = chat_gpt(prompt, gpt_model_dict[model])
                res =  extract_json_from_string(result)
            except Exception as e:
                print(f"{model}发生异常：{e}")
                res = None
            finally:
                if res:
                    if 'Score' in res:
                        return int(res['Score']), para
                    elif 'score' in res:
                        return int(res['score']), para
                iter += 1 
                if iter > 5:
                    return None, para
    else:
        raise ValueError(f'Unsupported model: {model}')

        


