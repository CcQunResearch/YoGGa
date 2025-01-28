import yaml
import os
import pandas as pd
import json
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score
# 一些参数
with open('config.yaml', 'r') as file:
    config = yaml.safe_load(file)
w = config['weighted_fusion']['w']
low_threshold = config['construct_dataset_pseudo']['low_threshold']
high_threshold = config['construct_dataset_pseudo']['high_threshold']
prefix = '/prefix_path'

test_col = 'prob' # lg_pred, pe_prob, prob
def get_metric():
    gd = []
    pred = []
    pred_prob = []
    for drama in os.listdir(prefix):
        paths = os.listdir(os.path.join(prefix, drama, 'csv'))
        for epi in paths:
            if epi.endswith('.csv'):
                file_path = os.path.join(prefix, drama, 'csv', epi)
                df = pd.read_csv(file_path)
                if test_col not in df.columns:
                    continue
                count0 = 0
                count1 = 0
                for i in range(1, len(df)):
                    row1 = df.iloc[i - 1]
                    row2 = df.iloc[i]
                    same_speaker = -1
                    if 'spk' in row1:
                        same_speaker = int(row1['spk'] == row2['spk'])  
                    elif '角色' in row1:
                        same_speaker = int(row1['角色'] == row2['角色'])
                    elif 'spk_name' in row1:
                        same_speaker = int(row1['spk_name'] == row2['spk_name'])
                    elif '说话人' in row1:
                        same_speaker = int(row1['说话人'] == row2['说话人'])
                    if same_speaker!= -1 and str(row2[test_col]) != 'None':
                        gd.append(same_speaker)
                        pred.append(int(row2[test_col] > 0.5))
                        pred_prob.append(float(row2[test_col]) if not pd.isna(row2[test_col]) else 0.0)
                print(f"【{test_col}】---{drama}---{epi}---count0:{count0},count1:{count1}")
    accuracy = accuracy_score(gd, pred)
    precision = precision_score(gd, pred)
    roc_auc = roc_auc_score(gd, pred_prob)
    recall = recall_score(gd, pred)
    f1 = f1_score(gd, pred)
    print(f"【{test_col}】---prediction Result:")
    print(f"Accuracy: {accuracy:.4f}")
    print(f"ROC AUC: {roc_auc:.4f}")
    print(f"Precision: {precision:.4f}")
    print(f"Recall: {recall:.4f}")
    print(f"F1 Score: {f1:.4f}")

get_metric()