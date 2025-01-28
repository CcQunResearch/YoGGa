def extract_zh_from_prompt(src_prompt):
    if '原文：' in src_prompt:
        start = src_prompt.find('原文：')
        res = src_prompt[start+3:].lstrip()
        end = res.find('翻译结果：')
        return [elem for elem in res[:end].strip().split('\n') if elem.strip()!='']
    else:
        print('No translation found')
        return ''
    
def extract_tr_from_prompt(src_prompt):
    if '专有名词翻译：' in src_prompt:
        start = src_prompt.find('专有名词翻译：')
        res = src_prompt[start+7:].lstrip()
        end = res.find('\n\n')
        return [elem for elem in res[:end].strip().split('\n') if elem.strip()!='']
    else:
        print('No translation found')
        return []
    
def extract_tar(texts):
    res = []
    for text in texts.split('\n'):
        start = text.find('(')
        end = text.find(')')
        if start!=-1 and end!=-1:
            res.append(text[start+1:end].strip())
    return res

def extract_zh(texts):
    res = []
    for text in texts.split('\n'):
        start = text.find('(')
        if start!=-1:
            res.append(text[:start].strip())
    return res

def check_quality(prompt,pred):
    # return True
    prompt_zhs = extract_zh_from_prompt(prompt)
    trs = extract_tr_from_prompt(prompt)
    pred_zh = extract_zh(pred)
    pred_tars = extract_tar(pred)
    #1、中文和prompt对齐
    if len(prompt_zhs)!=len(pred_zh):
        print(f"中文和prompt行数不一致--{len(prompt_zhs)}!={len(pred_zh)}")
        return False
    for i in range(len(prompt_zhs)):
        if prompt_zhs[i]!=pred_zh[i]:
            print(f"中文和prompt对齐失败--{prompt_zhs[i]}!={pred_zh[i]}")
            # return False
    #2、译文不重复
    if len(set(pred_tars))<len(pred_tars)-10:
        print(f"译文有重复")
        return False
    #3、检查术语
    error_tr = 0
    for tr_elem in trs:
        if '-' in tr_elem:
            tr_zh = tr_elem.split('-')[0].strip()
            tr_es = tr_elem.split('-')[1].strip()
            for i,zh_elem in enumerate(pred_zh):
                if tr_zh in zh_elem:
                    # print(f"错误句子: {src_zh[i]}-----{src_es[i]}----{pred_es[i]}")
                    # print(f"正确术语: {tr_zh}-----{tr_es}")
                    thold = 5
                    flag = False
                    start = i-thold if i-thold>=0 else 0
                    end = i+thold if i+thold<len(pred_tars) else len(pred_tars)
                    for j in range(start,end):
                        if tr_es.lower() in pred_tars[j].lower():
                            flag = True
                            break
                    if not flag:
                        error_tr+=1
    if error_tr>3:
        print(f"单个prompt错误术语数: {error_tr}")
        return False
    return True