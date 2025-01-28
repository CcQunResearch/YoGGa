import difflib
def check_res(text):
    if text.endswith("Judgment results="):
        text = text.replace("Judgment results=", "").strip()
    if '开始判断，遵守上述任务要求和格式' in text:
        text = text.split('开始判断，遵守上述任务要求和格式')[1].strip().strip('\n').strip('»»»»')
    else:
        print("no prompt found")
    res = []
    for line in text.split(">"):
        if "<" in line:
            res.append(line.strip())
    return res

def split_into_batches(lst, batch_size):
    if batch_size <= 0:
        raise ValueError("批量大小必须大于0")
    return [lst[i:i + batch_size] for i in range(0, len(lst), batch_size)]

def is_similar(a, b, threshold=0.8):
    similarity = difflib.SequenceMatcher(None, a, b).ratio()
    return similarity >= threshold

def update_dataframe(df, prob_record):
    eff = []
    if 'pe_prob_test' in df.columns:
        del df['pe_prob_test']
    if 'pe_prob' in df.columns:
        del df['pe_prob']
    if 'prob' in df.columns:
        del df['prob']
    for i, row in df.iterrows():
        matched = False
        for (start_index, end_index),text, prob in prob_record:
            src_text = row['zh_text'].strip() if 'zh_text' in df.columns else row['text'].strip()
            if is_similar(src_text,text.strip()) and start_index-1 <= i <= end_index+1:
                df.loc[i, 'pe_prob'] = str(prob)
                eff.append(i)
                matched = True
                break
        if not matched:
            df.loc[i, 'pe_prob'] = None
    return df

def split_list(lst, n):
    length = len(lst)
    segment_length = length // n

    remainder = length % n
    segments = []
    start = 0
    for i in range(n):
        end = start + segment_length + (1 if i < remainder else 0)
        segments.append(lst[start:end])
        start = end
    return segments