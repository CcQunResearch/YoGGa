import os
import re
from pydub import AudioSegment
from moviepy.editor import *
import pandas as pd
import subprocess
from modelscope.pipelines import pipeline
from tqdm import tqdm
import librosa
from datetime import datetime
import pysrt

sv_pipeline = pipeline(
    task='speaker-verification',
    model='iic/speech_eres2netv2_sv_zh-cn_16k-common',
    model_revision='v1.0.2'
)


def extract_audio(video_file, vocal_path):
    audio_file = video_file.replace('mp4', 'wav')
    video_clip = VideoFileClip(video_file)
    audio_clip = video_clip.audio
    audio_clip.write_audiofile(audio_file)
    audio_clip.close()
    video_clip.close()

    command = ['demucs', '-o', vocal_path, '--two-stems=vocals', audio_file]
    subprocess.run(command)

    return audio_file


def slice_wavs(zimu_file, wav_file, slice_path):
    df = pd.read_csv(zimu_file)
    audio = AudioSegment.from_wav(wav_file)
    output_files = []
    os.makedirs(slice_path, exist_ok=True)
    for i in range(len(df)):
        start = df['start_time'].iloc[i]
        end = df['end_time'].iloc[i]
        slice = audio[start:end]
        output_file = os.path.join(slice_path, str(i).zfill(4) + '.wav')
        output_files.append(output_file)
        slice.export(output_file, format="wav")
    df['files'] = output_files
    df.to_csv(zimu_file, index=False, encoding='utf-8-sig')


def cal_similarity(input, output):
    df = pd.read_csv(input)
    pred = ['']
    for i in tqdm(range(len(df) - 1)):
        now_file = df['files'].iloc[i]
        next_file = df['files'].iloc[i + 1]
        data1, sr = librosa.load(now_file, sr=16000)
        data2, sr = librosa.load(next_file, sr=16000)
        result = sv_pipeline([data1, data2])
        pred.append(result['text'])

    df['pred'] = pred
    df.to_csv(output, encoding='utf-8-sig', index=False)


def zimu_analysis(assfile, csvfile):
    if assfile.endswith('ass'):
        ass_result = []
        with open(assfile, 'r') as f:
            lines = f.readlines()
            original_line_num = 1
            for line in lines:
                if line.startswith('Dialogue'):
                    fields = line.split(',')
                    text = ','.join(fields[9:]).strip()  # 英文台词中会出现逗号，故做此处理
                    text = text.replace("\u200f", "")
                    if len(text) == 0:
                        original_line_num += 1
                        continue
                    
                    if 'Episode' in text or '[' in text or '♪' in text or '♫' in text:
                        original_line_num += 1
                        continue
                    
                    if r'{\an8}' in text:
                        original_line_num += 1
                        continue
                        
                    # [Th]删除泰语字幕中的注释行，以及台词中开头出现的注释
                    if text[0] == '=' and text[-1] == '=':
                        original_line_num += 1
                        continue
                    text = re.sub(r'=.*?=\\N', '', text)

                    # 删除注释
                    text = re.sub(r'\(\*.*?\)', '', text)
                    text = text.replace('*', '')

                    # 删除括号
                    text = re.sub(r'\((.*?)\)', r'\1', text)
                    
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
                        
                    start_time_str = datetime.strptime(fields[1], '%H:%M:%S.%f')
                    start_milliseconds = (start_time_str.hour * 3600 + start_time_str.minute * 60 + start_time_str.second) * 1000 + int(start_time_str.microsecond / 1000)
                    end_time_str = datetime.strptime(fields[2], '%H:%M:%S.%f')
                    end_milliseconds = (end_time_str.hour * 3600 + end_time_str.minute * 60 + end_time_str.second) * 1000 + int(end_time_str.microsecond / 1000)
                    ass_result.append((start_milliseconds, end_milliseconds, text, original_line_num))
                    original_line_num += 1
                              
        res = pd.DataFrame(columns=['start_time', 'end_time', 'text', 'original_line_num'])
        res['start_time'], res['end_time'], res['text'], res['original_line_num'] = zip(*ass_result)
        res.to_csv(csvfile, index=False, encoding="utf-8-sig")
