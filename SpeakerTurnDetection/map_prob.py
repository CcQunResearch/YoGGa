import time
import yaml
import os
import pandas as pd

# some config
with open('../config.yaml', 'r') as file:
    config = yaml.safe_load(file)
lang = config['lang']
lang = 'zh2ms'


def map_label(src_prefix,tar_prefix):
    i = 0
    for drama in os.listdir(src_prefix):
        for epi in os.listdir(os.path.join(src_prefix, drama, 'csv')):
            if epi.endswith('.csv'):
                epi_num = epi.split('.')[0]
                src_file_path = os.path.join(src_prefix, drama, 'csv', epi)
                tar_file_path = os.path.join(tar_prefix, drama, f'{drama} {epi_num}_简体中文.csv')
                if os.path.exists(src_file_path) and os.path.exists(tar_file_path):
                    src_df = pd.read_csv(src_file_path,sep=',')
                    tar_df = pd.read_csv(tar_file_path,sep='\t')
                    if len(tar_df.columns)< 3:
                        print('分隔符错误')
                        tar_df = pd.read_csv(tar_file_path,sep=',')
                    if 'original_line_num' in src_df.columns:
                        src_df = src_df.rename(columns={'original_line_num': 'Original Line'})
                    if 'Original Line' not in tar_df.columns:
                        print(f"错误: {tar_file_path} 缺少 'Original Line' 列，跳过此文件")
                        continue
                    if 'Original Line' not in src_df.columns:
                        print(f"错误: {src_file_path} 缺少 'Original Line' 列，跳过此文件")
                        continue

                    if 'prob' in src_df.columns:
                        merge_df = pd.merge(tar_df, src_df[['Original Line', 'prob','lg_pred','pe_prob']], on='Original Line', how='left')
                        # 更新 tar_df 的 label 列
                        tar_df['p_std'] = merge_df['prob']
                        tar_df['p_a'] = merge_df['lg_pred']
                        tar_df['p_t'] = merge_df['pe_prob']
                        tar_df.loc[0,'label'] = 'A'
                        print(tar_df.loc[0,'label'])
                        for i in range(1, len(tar_df)):
                            if pd.isna(tar_df.loc[i, 'p_std']): 
                                tar_df.loc[i, 'label'] = tar_df.loc[i - 1, 'label']
                            elif tar_df.loc[i, 'p_std'] < 0.5:
                                tar_df.loc[i, 'label'] = 'B' if tar_df.loc[i - 1, 'label'] == 'A' else 'A'
                            elif tar_df.loc[i, 'p_std'] >= 0.5:
                                tar_df.loc[i, 'label'] = 'A' if tar_df.loc[i - 1, 'label'] == 'A' else 'B'
                        print(tar_file_path)
                        tar_df.to_csv(tar_file_path, index=False,sep='\t')
                        # print(f"已处理 {drama} 个文件")

src_prefix_train = '/train_path/'
src_prefix_test = '/test_path/'
tar_prefix = f'../Data/{lang}/train/'
if os.path.exists(tar_prefix):
    map_label(src_prefix_train,tar_prefix)
    map_label(src_prefix_test,tar_prefix)