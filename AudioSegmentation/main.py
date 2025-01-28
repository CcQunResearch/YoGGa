import pandas as pd
import os.path as osp
import os
import shutil
import yaml
from utils import zimu_analysis,extract_audio,slice_wavs
import concurrent.futures

def audio_segmentation(input_zimu, output_zimu_csv, input_video, vocal_path, slice_path):
    # stage1 解析字幕文件
    zimu_analysis(input_zimu, output_zimu_csv)
    # stage2 提取人声
    audio_file = extract_audio(input_video, vocal_path)
    # stage3 切分音频
    base_name = os.path.splitext(os.path.basename(audio_file))[0]
    vocal_file = osp.join(vocal_path, 'htdemucs', base_name, 'vocals.wav')
    slice_wavs(output_zimu_csv,vocal_file,slice_path)
    shutil.rmtree(osp.join(vocal_path, 'htdemucs', base_name))
    
    if os.path.exists(audio_file):
        os.remove(audio_file)

if __name__ == '__main__':
    dirname = osp.dirname(osp.abspath(__file__))
    config_path = osp.join(dirname, '..', 'config.yaml')
    with open(config_path, 'r', encoding='utf-8') as file:
        config = yaml.safe_load(file)
    as_data_path = config['as_data_path']
    
    mapping_path = osp.join(as_data_path, 'mapping.xlsx')
    zimu_path =  osp.join(as_data_path, 'zh', 'source(train)')
    videos_path = osp.join(as_data_path, 'videos')
    separate_path = osp.join(as_data_path, 'separate')
    # test_show_name = ['吉祥不高兴', '契约新娘', '护心', '请叫我总监']

    if osp.exists(separate_path):
        shutil.rmtree(separate_path)
    os.makedirs(separate_path)

    for video_name in os.listdir(videos_path):
        os.rename(osp.join(videos_path, video_name), osp.join(videos_path, video_name.split('_')[-1].strip()))

    mapping_sheet = pd.read_excel(mapping_path, sheet_name='Sheet1')

    show_name_list = mapping_sheet['show_name'].to_list()
    episode_list = mapping_sheet['episode'].to_list()
    vdo_id_list = mapping_sheet['vdo_id'].to_list()

    mapping = {}
    for i, show_name in enumerate(show_name_list):
        if show_name not in mapping.keys():
            mapping[show_name] = {}
        mapping[show_name][episode_list[i]] = vdo_id_list[i]
        
    # print(mapping)

    tasks = []
    tmp_paths = []
    for show_name in mapping.keys():
        show_mapping = mapping[show_name]
        # if show_name in test_show_name:
        #     zimu_split_path = 'source(test)'
        #     output_split_path = 'test'
        # else:
        #     zimu_split_path = 'source(train)'
        #     output_split_path = 'train'
        # output_path = osp.join(separate_path, output_split_path, show_name)
        output_path = osp.join(separate_path, show_name)
        show_csv_path = osp.join(output_path, 'csv')
        show_vocal_path = osp.join(output_path, 'vocal')
        show_slice_path = osp.join(output_path, 'slice')
        
        os.makedirs(show_csv_path)
        os.makedirs(show_slice_path)
        os.makedirs(show_vocal_path)
        tmp_paths.append(show_vocal_path)
        for episode in show_mapping.keys():
            vdo_id = show_mapping[episode]
            # input_zimu = osp.join(zimu_path, zimu_split_path, show_name,f'{episode}.ass')
            input_zimu = osp.join(zimu_path, show_name,f'{episode}.ass')
            output_zimu_csv = osp.join(show_csv_path, f'{episode}.csv')
            tmp_path = osp.join(videos_path, show_name, str(vdo_id))
            if not osp.exists(input_zimu) or not osp.exists(tmp_path):
                print(f'{input_zimu} or {tmp_path} not exists')
                print(osp.exists(input_zimu))
                print(osp.exists(tmp_path))
                print()
                continue
            mp4_file_name = next(f for f in os.listdir(tmp_path) if f.endswith('.mp4'))
            input_video = osp.join(tmp_path, mp4_file_name)
            slice_path = osp.join(show_slice_path, f'{episode:02}')
            
            tasks.append((input_zimu, output_zimu_csv, input_video, show_vocal_path, slice_path))

    # print(tasks)
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=12) as executor:
        futures = [executor.submit(audio_segmentation, *para) for para in tasks]
        concurrent.futures.wait(futures)

    for tmp_path in tmp_paths:
        shutil.rmtree(tmp_path)