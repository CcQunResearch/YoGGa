import requests
import json
import re
import os
import csv
import random
import pandas as pd
import os.path as osp
from prompt_template import get_replace_dict, proper_noun_slot_dict
from datetime import timedelta


lang_dict = {
    "zh": "简体中文",
    "en": "英语",
    "th": "泰国语",
    "vi": "越南语",
    "id": "印尼语",
    "ms": "马来语",
    "es": "西班牙语",
    "pt": "葡萄牙语",
    "ar": "阿拉伯语",
    "ja": "日语",
    "ko": "韩语",
    "de": "德语",
    "fr": "法语",
}

# 跟这些词相同就丢弃
filter_nouns = ["爸", "妈", "爷爷", "奶奶", "外公", "外婆", "哥哥", "姐姐", "哥", "姐", "弟弟", "妹妹", "儿子", "女儿",
                "丈夫", "妻子", "朋友", "同学", "老师", "人", "床", "父母", "爸爸", "妈妈", "爹", "娘", "上",
                "下", "左", "右", "爷", "高", "走", "滚", "等", "收", "打", "我女儿", "我儿子",
                "大脑", "真相", "生日", "谢谢", "美国", "中国", "日本", "韩国", "印度", "俄罗斯", "英国", "法国",
                "德国", "意大利", "西班牙", "葡萄牙", "希腊", "土耳其", "以色列", "埃及", "南非", "澳大利亚", "新西兰",
                "加拿大", "墨西哥", "巴西", "阿根廷", "哥伦比亚", "智利", "秘鲁", "委内瑞拉", "女大学生", "花", "药",
                "好", "坏", "高", "矮", "胖", "瘦", "大", "小", "多", "少", "长", "短", "宽", "窄", "高", "矮", "胖",
                "明天", "后天", "今天", "昨天", "前天", "店", "地址", "对不起", "谁", "一个"]

# 包含这些词就丢弃
reversed_filter_nouns = ["我", "你", "他", "她", "它", "咱", "您", "这", "那", "男朋友", "女朋友"]

def contains_chinese(text):
    pattern = re.compile(r'[\u4e00-\u9fff]')
    return bool(pattern.search(text))


def time2timestamp(time_str):
    hours, minutes, seconds = map(float, time_str.split(':'))
    time_delta = timedelta(hours=hours, minutes=minutes, seconds=seconds)
    timestamp = time_delta.total_seconds()
    return timestamp

def extract_meta_info(source_path, src_lang_str, lang_str):
    file_names = sorted(os.listdir(source_path))
    episodes = []
    target_play_name = ''
    for file_name in file_names:
        split_res = file_name.split('_')
        file_name_postfix = split_res[-2][-2:] + '_' + split_res[-1]
        src_pattern = f'\d+.*_{src_lang_str}.ass'
        pattern = f'\d+.*_{lang_str}.ass'
        if not re.match(src_pattern, file_name_postfix) and not re.match(pattern, file_name_postfix):
            continue
        else:
            if target_play_name == '':
                target_play_name = file_name[:-len(file_name_postfix)]
            episodes.append(file_name_postfix.split('_')[0])

    episodes = list(set(episodes))
    return {'target name': target_play_name, 'episodes': episodes}

def process_assfile_2_csvfile(source_path, target_path, file_name, audio_csv_path=None, merge_audio_path=False):
    file_path = osp.join(source_path, file_name)
    target_file_path = osp.join(target_path, file_name.replace('.ass', '.csv'))
    csv_writer = csv.writer(open(target_file_path, 'w', encoding='utf-8'), delimiter='\t')

    file_content = open(file_path, 'r', encoding='utf-8').read()
    file_content = file_content[file_content.find('[Events]') + 8:].strip()
    
    mapping = osp.exists(audio_csv_path) if merge_audio_path else False
    if mapping:
        audio_csv = pd.read_csv(audio_csv_path)
        line_2_audiopath = dict(zip(audio_csv['original_line_num'], audio_csv['files']))

    for i, line in enumerate(file_content.split('\n')):
        fields = line.split(',')
        text = ','.join(fields[9:]).strip()  # 英文台词中会出现逗号，故做此处理
        text = text.replace("\u200f", "")
        if len(text) == 0:
            continue
        
        if 'Episode' in text or '[' in text or '♪' in text or '♫' in text:
            continue
        
        if r'{\an8}' in text:
            continue
        
        # [Th]删除泰语字幕中的注释行，以及台词中开头出现的注释
        if text[0] == '=' and text[-1] == '=':
            continue
        text = re.sub(r'=.*?=\\N', '', text)

        # 删除注释
        text = re.sub(r'\(\*.*?\)', '', text)
        text = text.replace('*', '')

        # 删除括号
        text = re.sub(r'\((.*?)\)', r'\1', text)
        
        if "日语" in file_name:
            text = re.sub(r'（(.*?)）', '', text)
        
        if r'{\fad(120,120)}' in text:
            text = text.replace('{\fad(120,120)}', '')
        if r'{\c&Hffe5e5&}' in text:
            text = text.replace('{\c&Hffe5e5&}', '')

        if r'\N-' in text:
            text = text.replace(r'\N-', ' ')
            if text[0] == '-':
                text = text[1:]
        elif r'\N' in text:
            text = text.replace(r'\N', ' ')
            
        if not text or len(text) == 0:
            continue

        fields = fields[:9] + [text]
        assert len(fields) == 10, 'wrong field num.'
        fields = [field.strip() for field in fields]
        if 'Format: Layer' in line:
            fields = ['Original Line'] + fields
            if merge_audio_path:
                fields = fields + ['Audio Path']
        else:
            fields = [i] + fields
            if merge_audio_path:
                if mapping:
                    if i in line_2_audiopath:
                        fields = fields + [line_2_audiopath[i]]
                    else:
                        fields = fields + ['Not Found']
                else:
                    fields = fields + ['Not Found']
        csv_writer.writerow(fields)
        
def statistic_interval(target_path, meta_info, src_lang_str, lang_str, threshold_limit=0.7):
    map_result = {}
    target_play_name = meta_info['target name']
    for episode in meta_info['episodes']:
        # print(target_path, episode)
        source_file_path = osp.join(target_path, f'{target_play_name}{episode}_{src_lang_str}.csv')
        target_file_path = osp.join(target_path, f'{target_play_name}{episode}_{lang_str}.csv')
        source_csv_reader = pd.read_csv(open(source_file_path, 'r', encoding='utf-8'), sep='\t')
        target_csv_reader = pd.read_csv(open(target_file_path, 'r', encoding='utf-8'), sep='\t')

        source_duration = source_csv_reader['Start'].tolist()
        target_duration = target_csv_reader['Start'].tolist()
        source_duration = [time2timestamp(duration) for duration in source_duration]
        target_duration = [time2timestamp(duration) for duration in target_duration]

        statistic = {}
        step = abs(len(target_duration) - len(source_duration)) + 10
        min_intervals = []
        for i in range(len(source_duration)):
            compares = target_duration[max(0, i - step):min(i + step, len(target_duration))]
            intervals = [round(abs(source_duration[i] - compare), 2) for compare in compares]
            min_interval = min(intervals)
            min_intervals.append(min_interval)
            statistic[i] = (target_duration.index(compares[intervals.index(min_interval)]), min_interval)
        cleaned_min_intervals = [min_interval for min_interval in min_intervals if min_interval <= threshold_limit]
        threshold = min(threshold_limit, max(cleaned_min_intervals))
        s2c_map = {}
        for index, res in statistic.items():
            if res[1] <= threshold:
                s2c_map[index] = res[0]

        map_result[episode] = s2c_map

        miss_lines = []
        for i in range(len(source_duration)):
            if i not in s2c_map.keys():
                miss_lines.append(i)

        map_result[episode] = {'s2c map': s2c_map, 'miss lines': miss_lines}
    return map_result

def extract_dialogue_translation(target_path, meta_info, map_result, src_lang_str, lang_str, context_len=5, step=25, merge_audio_path=False):
    episode_result = {}
    target_play_name = meta_info['target name']
    for episode in meta_info['episodes']:
        source_file_path = osp.join(target_path, f'{target_play_name}{episode}_{src_lang_str}.csv')
        target_file_path = osp.join(target_path, f'{target_play_name}{episode}_{lang_str}.csv')
        source_csv_reader = pd.read_csv(open(source_file_path, 'r', encoding='utf-8'), sep='\t')
        target_csv_reader = pd.read_csv(open(target_file_path, 'r', encoding='utf-8'), sep='\t')
        source_dialogue = source_csv_reader['Text'].tolist()
        target_dialogue = target_csv_reader['Text'].tolist()
        source_start_timestamp = source_csv_reader['Start'].tolist()
        source_end_timestamp = source_csv_reader['End'].tolist()
        source_original_line = source_csv_reader['Original Line'].tolist()
        source_audio_path = source_csv_reader['Audio Path'].tolist() if merge_audio_path else ['Not Found'] * len(source_dialogue)

        results = []
        s2c_map = map_result[episode]['s2c map']
        miss_lines = map_result[episode]['miss lines'] + [len(source_dialogue)]
        end = -1
        for miss_line in miss_lines:
            begin = end + 1
            end = miss_line
            dialogue_fragment = [str(source_dialogue[index]) for index in range(begin, end)]
            translation_fragment = [str(target_dialogue[s2c_map[index]]) for index in range(begin, end)]
            source_original_line_fragment = [source_original_line[index] for index in range(begin, end)]
            source_start_timestamp_fragment = [source_start_timestamp[index] for index in range(begin, end)]
            source_end_timestamp_fragment = [source_end_timestamp[index] for index in range(begin, end)]
            source_audio_path_fragment = [source_audio_path[index] for index in range(begin, end)] if merge_audio_path else ['Not Found'] * len(dialogue_fragment)

            head_index = 0
            tail_index = len(dialogue_fragment) + 100000
            if begin == 0 and end - begin - context_len > step:
                head_index = -context_len
                tail_index = step + context_len
            elif begin != 0 and end - begin - 2 * context_len > step:
                head_index = 0
                tail_index = step + 2 * context_len
            else:
                if len(dialogue_fragment) >= 15:
                    res = {
                        'chinese': dialogue_fragment,
                        'target': translation_fragment,
                        'chinese original line': source_original_line_fragment
                    }
                    cs_timestamp = source_start_timestamp_fragment
                    ce_timestamp = source_end_timestamp_fragment
                    source_duration = [round(time2timestamp(a) - time2timestamp(b), 3) for a, b in
                                        zip(ce_timestamp, cs_timestamp)]
                    res['chinese duration'] = source_duration
                    res['start timestamp'] = cs_timestamp
                    res['end timestamp'] = ce_timestamp
                    
                    if merge_audio_path:
                        res['chinese audio path'] = source_audio_path_fragment
                        res['audio complete'] = 'Not Found' not in res['chinese audio path']
                    
                    results.append(res)
            while tail_index <= len(dialogue_fragment):
                res = {
                    'chinese': dialogue_fragment[max(0, head_index):tail_index],
                    'target': translation_fragment[max(0, head_index):tail_index],
                    'chinese original line': source_original_line_fragment[max(0, head_index):tail_index]
                }
                cs_timestamp = source_start_timestamp_fragment[max(0, head_index):tail_index]
                ce_timestamp = source_end_timestamp_fragment[max(0, head_index):tail_index]
                source_duration = [round(time2timestamp(a) - time2timestamp(b), 3) for a, b in
                                    zip(ce_timestamp, cs_timestamp)]
                res['chinese duration'] = source_duration
                res['start timestamp'] = cs_timestamp
                res['end timestamp'] = ce_timestamp
                
                if merge_audio_path:
                    res['chinese audio path'] = source_audio_path_fragment[max(0, head_index):tail_index]
                    res['audio complete'] = 'Not Found' not in res['chinese audio path']
                
                results.append(res)
                head_index += step
                tail_index += step
            if tail_index < 100000 and len(dialogue_fragment) - head_index - 2 * context_len > 10:
                res = {
                    'chinese': dialogue_fragment[head_index:],
                    'target': translation_fragment[head_index:],
                    'chinese original line': source_original_line_fragment[head_index:]
                }
                cs_timestamp = source_start_timestamp_fragment[head_index:]
                ce_timestamp = source_end_timestamp_fragment[head_index:]
                source_duration = [round(time2timestamp(a) - time2timestamp(b), 3) for a, b in
                                    zip(ce_timestamp, cs_timestamp)]
                res['chinese duration'] = source_duration
                res['start timestamp'] = cs_timestamp
                res['end timestamp'] = ce_timestamp
                
                if merge_audio_path:
                    res['chinese audio path'] = source_audio_path_fragment[head_index:]
                    res['audio complete'] = 'Not Found' not in res['chinese audio path']
                
                results.append(res)
        episode_result[episode] = results
    return episode_result

def extract_dialogue_translation_nogt(target_path, meta_info, src_lang_str, context_len=5, step=25):
    episode_result = {}
    target_play_name = meta_info['target name']
    for episode in meta_info['episodes']:
        chinese_file_path = osp.join(target_path, f'{target_play_name}{episode}_{src_lang_str}.csv')
        chinese_csv_reader = pd.read_csv(open(chinese_file_path, 'r', encoding='utf-8'), sep='\t')
        chinese_dialogue = chinese_csv_reader['Text'].tolist()
        chinese_start_timestamp = chinese_csv_reader['Start'].tolist()
        chinese_end_timestamp = chinese_csv_reader['End'].tolist()
        chinese_original_line = chinese_csv_reader['Original Line'].tolist()
        
        results = []
        begin = 0
        end = step
        while begin < len(chinese_dialogue):
            dialogue_fragment = chinese_dialogue[max(begin - context_len, 0):end + context_len]
            chinese_original_line_fragment = chinese_original_line[max(begin - context_len, 0):end + context_len]
            cs_timestamp = chinese_start_timestamp[max(begin - context_len, 0):end + context_len]
            ce_timestamp = chinese_end_timestamp[max(begin - context_len, 0):end + context_len]
            chinese_duration = [round(time2timestamp(a) - time2timestamp(b), 3) for a, b in zip(ce_timestamp, cs_timestamp)]
            res = {
                'chinese': dialogue_fragment,
                'chinese original line': chinese_original_line_fragment,
                'chinese duration': chinese_duration,
                'start timestamp': cs_timestamp,
                'end timestamp': ce_timestamp
            }
            results.append(res)
            begin += step
            end += step
        episode_result[episode] = results
    return episode_result

def extract_proper_noun(generation_results):
    result = {}
    for tmp_result in generation_results:
        predict = tmp_result['predict']
        for res in predict.split('\n'):
            # pattern = re.compile(r'([\u4e00-\u9fa5]+)（([\u4e00-\u9fa5]+)）\s?-\s?(.+)')
            pattern = re.compile(r'(.+?)（(.+?)）\s?-\s?(.+)')
            matches = pattern.findall(res)
            if len(matches) > 0:
                match = matches[0]
            else:
                continue

            word = match[0].strip()
            type = match[1].strip()
            translation = match[2].strip()

            if word in result.keys():
                types = type.split('/')
                for t in types:
                    if t not in result[word]['type'].keys():
                        result[word]['type'][t] = 1
                    else:
                        result[word]['type'][t] += 1
                if translation not in result[word]['translation'].keys():
                    result[word]['translation'][translation] = 1
                else:
                    result[word]['translation'][translation] += 1
                result[word]['count'] += 1
            else:
                result[word] = {
                    'type': {},
                    'translation': {translation: 1},
                    'count': 1
                }
                type = type.replace('+', '/')
                types = type.split('/')
                for t in types:
                    result[word]['type'][t] = 1

    return result


def find_contained_words(words):
    contained_words = set()
    
    # 遍历列表中的每一个词
    for word in words:
        for other_word in words:
            # 确保不比较同一个词，同时判断包含关系
            if word != other_word and word in other_word:
                contained_words.add((other_word, word))
                break
    
    return list(contained_words)


def filter_translation(translation):
    all_trans = list(translation.items())
    sorted_all_trans = sorted(all_trans, key=lambda x: x[1], reverse=True)
    return sorted_all_trans[0][0]


def filter_proper_noun_result(proper_noun_result, threshold=3):
    filter_result = {}
    proper_terms = []
    for term in proper_noun_result.keys():
        # 只有一个字
        if len(term) == 1:
            continue
        
        # # 中文太长
        # if len(term) >= 8:
        #     print(term)
        #     continue

        # 直接过滤
        if term in filter_nouns:
            # print(term)
            continue
        reversed_pass = False
        for rf in reversed_filter_nouns:
            if rf in term:
                reversed_pass = True
                break
        if reversed_pass:
            continue

        # 全剧只出现少次
        if proper_noun_result[term]['count'] <= 2:
            continue

        # 出现多次，且类型为地名、机构、人名等类型，则一致认为属于专有名词
        types = proper_noun_result[term]['type'].keys()
        if '地名' in types or '机构' in types or '人名' in types:
            trans = filter_translation(proper_noun_result[term]['translation'])
            typee = filter_translation(proper_noun_result[term]['type'])
            # if contains_chinese(trans):
            #     continue
            proper_terms.append([term, typee, trans])
            continue

        # 剩下的通过阈值来判断是否作为专有名词
        if proper_noun_result[term]['count'] > threshold:
            trans = filter_translation(proper_noun_result[term]['translation'])
            typee = filter_translation(proper_noun_result[term]['type'])
            # if contains_chinese(trans):
            #     continue
            proper_terms.append([term, typee, trans])
            continue

    for proper_term in proper_terms:
        filter_result[proper_term[0]] = {"translation": proper_term[2], "type": proper_term[1]}
    return filter_result


def easy_filter_proper_noun_result(proper_noun_result):
    filter_result = {}
    proper_terms = []
    for term in proper_noun_result.keys():
        # 只有一个字
        if len(term) == 1:
            continue
        
        # # 中文太长
        # if len(term) >= 8:
        #     continue

        # 直接过滤
        if term in filter_nouns:
            continue
        reversed_pass = False
        for rf in reversed_filter_nouns:
            if rf in term:
                reversed_pass = True
                break
        if reversed_pass:
            continue

        trans = filter_translation(proper_noun_result[term]['translation'])
        typee = filter_translation(proper_noun_result[term]['type'])
        # if contains_chinese(trans):
        #     continue
        proper_terms.append([term, typee, trans])

    for proper_term in proper_terms:
        filter_result[proper_term[0]] = {"translation": proper_term[2], "type": proper_term[1]}
    return filter_result

def extract_training_queries_and_responses(play_name, episode_result, proper_noun_dict, template, src_lang_str, lang_str, pn_identify_dict=None, pn_consis=False, evaluation_mode=True, merge_audio_path=False):
    play_data = []
    pn_fewshot = []

    # 构建词典树
    trie = Trie()
    for word in set(proper_noun_dict.keys()):
        trie.insert(word)

    for episode, dialogue in episode_result.items():
        for ce_pair_dict in dialogue:      
            ptypes = []
            if evaluation_mode:
                ce_pair_list = list(zip(ce_pair_dict["chinese"], ce_pair_dict["target"]))
                for i in range(len(ce_pair_list)):
                    if not ce_pair_list[i][0]:
                        ce_pair_list[i][0] = ""
                    if not ce_pair_list[i][1]:
                        ce_pair_list[i][1] = ""
            else:
                ce_pair_list = list(zip(ce_pair_dict["chinese"], [""] * len(ce_pair_dict["chinese"])))
                for i in range(len(ce_pair_list)):
                    if not ce_pair_list[i][0]:
                        ce_pair_list[i][0] = ""

            dialogue_content = '\n'.join([ce_pair[0] for ce_pair in ce_pair_list])

            proper_noun_list = proper_noun_retrieve(dialogue_content, trie)
            proper_noun_list = sorted(proper_noun_list, key=lambda x: dialogue_content.index(x))
            if not pn_consis:
                proper_noun_pairs = [(p, proper_noun_dict[p]['type'], proper_noun_dict[p]['translation']) for p in
                                    proper_noun_list]
            else:
                target_dialogue_content = '\n'.join([ce_pair[1] for ce_pair in ce_pair_list])
                proper_noun_pairs = []
                for p in proper_noun_list:
                    trans_of_p = list(pn_identify_dict[p]['translation'].keys())
                    trans_of_p = nested_sort(trans_of_p)
                    chosen_trans = proper_noun_dict[p]['translation']
                    for trans in trans_of_p:
                        if trans in target_dialogue_content:
                            chosen_trans = trans
                            break
                    proper_noun_pairs.append((p, proper_noun_dict[p]['type'], chosen_trans))
                
            ptypes = list(set([pair[1] for pair in proper_noun_pairs]))
            proper_noun_content = '\n'.join(
                [f'{pair[0]} - {pair[2]}' for pair in proper_noun_pairs]) if proper_noun_pairs else '无'
            full_proper_noun_content = '\n'.join(
                [f'{pair[0]}（{pair[1]}） - {pair[2]}' for pair in proper_noun_pairs]) if proper_noun_pairs else '无专有名词'

            replace_dict = get_replace_dict()
            template = template.replace("<<1>>", random.choice(replace_dict["<<1>>"]))
            template = template.replace("<<2>>", random.choice(replace_dict["<<2>>"]))
            template = template.replace("<<3>>", random.choice(replace_dict["<<3>>"]))
            template = template.replace("<<4>>", random.choice(replace_dict["<<4>>"]))
            template = template.replace("<<5>>", random.choice(replace_dict["<<5>>"]))
            template = template.replace("<<6>>", random.choice(replace_dict["<<6>>"]))
            replace_src_lang_str = src_lang_str
            if src_lang_str == "简体中文":
                replace_src_lang_str = "中文"
            replace_lang_str = lang_str
            if lang_str == "简体中文":
                replace_lang_str = "中文"
            template = template.replace("<src_lang_str>", replace_src_lang_str)
            template = template.replace("<lang_str>", replace_lang_str)
            prompt = template.format(proper_noun_content, dialogue_content)
            
            response = '\n'.join([f'{ce_pair[0]}({ce_pair[1]})' for ce_pair in ce_pair_list]) if evaluation_mode else None
            
            res = {'instruction': prompt, 'input': None, 'output': response, 'chinese duration': ce_pair_dict['chinese duration'], 
                   'start timestamp': ce_pair_dict['start timestamp'], 'end timestamp': ce_pair_dict['end timestamp'], 'play name': play_name, 
                   'episode': episode, 'chinese original line': ce_pair_dict['chinese original line']}

            if merge_audio_path:
                res["chinese audio path"] = ce_pair_dict["chinese audio path"]
                res["audio complete"] = ce_pair_dict["audio complete"]
                
            play_data.append(res)
            
            if len(proper_noun_list) > 8 and len(ptypes) > 3:
                pn_fewshot.append({"dialogue": dialogue_content, "term": full_proper_noun_content})
    return play_data, pn_fewshot


class TrieNode:
    def __init__(self):
        self.children = {}
        self.is_word = False


class Trie:
    def __init__(self):
        self.root = TrieNode()

    def insert(self, word):
        node = self.root
        for char in word:
            if char not in node.children:
                node.children[char] = TrieNode()
            node = node.children[char]
        node.is_word = True

    def search(self, word):
        node = self.root
        for char in word:
            if char not in node.children:
                return False
            node = node.children[char]
        return node.is_word

def remove_subwords(word_list):
    result = []
    for i, word in enumerate(word_list):
        is_substring = False
        for j, other_word in enumerate(word_list):
            if i != j and word in other_word:
                is_substring = True
                break
        if not is_substring:
            result.append(word)
    return result

def proper_noun_retrieve(text, trie):
    result = []

    # 在文本中搜索每个词
    for i in range(len(text)):
        node = trie.root
        for j in range(i, len(text)):
            if text[j] not in node.children:
                break
            node = node.children[text[j]]
            if node.is_word:
                result.append(text[i:j + 1])

    result = list(set(result))
    result = remove_subwords(result)
    return result

def nested_sort(words):
    # 对列表进行排序，按长度降序
    words.sort(key=len, reverse=True)
    
    result = []
    
    while words:
        word = words.pop(0)
        # 将当前词加入结果列表
        result.append(word)
        # 去掉被当前词包含的词
        words = [w for w in words if word not in w]
    
    return result

def get_sft_prompt(src_lang_str, lang_str, template, proper_noun_content, dialogue_content):
    replace_dict = get_replace_dict()
    template = template.replace("<<1>>", random.choice(replace_dict["<<1>>"]))
    template = template.replace("<<2>>", random.choice(replace_dict["<<2>>"]))
    template = template.replace("<<3>>", random.choice(replace_dict["<<3>>"]))
    template = template.replace("<<4>>", random.choice(replace_dict["<<4>>"]))
    template = template.replace("<<5>>", random.choice(replace_dict["<<5>>"]))
    template = template.replace("<<6>>", random.choice(replace_dict["<<6>>"]))
    replace_src_lang_str = src_lang_str
    if src_lang_str == "简体中文":
        replace_src_lang_str = "中文"
    replace_lang_str = lang_str
    if lang_str == "简体中文":
        replace_lang_str = "中文"
    template = template.replace("<src_lang_str>", replace_src_lang_str)
    template = template.replace("<lang_str>", replace_lang_str)
    prompt = template.format(proper_noun_content, dialogue_content)
    return prompt