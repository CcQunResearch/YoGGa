
import json
import os
import torch
import torch.nn as nn
import numpy as np
import os
import numpy as np
import pandas as pd
import lightgbm as lgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report, roc_auc_score
from sklearn.metrics import precision_score, recall_score, f1_score
from itertools import combinations
from tqdm import tqdm
from torch.nn import CosineSimilarity
import torch
from scipy.spatial.distance import euclidean, cityblock
from sklearn.preprocessing import StandardScaler
import yaml
import random
random.seed(42)
# 一些参数
with open('config.yaml', 'r') as file:
    config = yaml.safe_load(file)
have_test_data = config['emb_classification_train']['have_test_data']
low_threshold = config['construct_dataset_pseudo']['low_threshold']
high_threshold = config['construct_dataset_pseudo']['high_threshold']
train_data_percentage = config['emb_classification_train']['train_data_percentage']

model_path = f'model_ckpt/emb_classification_train_{low_threshold}_{high_threshold}.pkl'
train_data_path = f'emb_train_data/emb_classification_train_{low_threshold}_{high_threshold}.json'

with open(train_data_path, "r") as f:
    train_data = json.load(f)

x_train = []
y_train = []
for elem in train_data:
    embedding1 = np.load(elem['emb1'])
    embedding2 = np.load(elem['emb2'])
    similarity = elem['similarity']
    combined_embedding = np.concatenate([[similarity],embedding1, embedding2])
    pseudo_label = int(elem['label'])
    x_train.append(combined_embedding)
    y_train.append(pseudo_label)

# 确定抽取数量
if train_data_percentage < 1:
    sample_size = int(len(y_train) * train_data_percentage)
    sample_indices = random.sample(range(len(y_train)), sample_size)
    x_sample = [x_train[i] for i in sample_indices]
    y_sample = [y_train[i] for i in sample_indices]
    x_train = x_sample
    y_train = y_sample

x_train = np.array(x_train)
y_train = np.array(y_train)
print(f"训练集大小: X_train: {x_train.shape}, y_train: {y_train.shape}")
assert len(x_train) == len(y_train), "训练集特征和标签样本数量不一致"



print(f'-----开始训练')

# 定义LGBM模型参数
param_grid = {
    'n_estimators': 2000,
    'learning_rate': 0.05,
    'num_leaves': 64,
    'max_depth': 32,
    'min_child_samples': 12,
    'subsample': 0.8,
    'colsample_bytree': 0.8,
    'objective': 'binary',
    'metric': 'binary_logloss',
    'boosting_type': 'gbdt'
}

model = lgb.LGBMClassifier(**param_grid)
print('开始训练')
model.fit(x_train, y_train)

with open(model_path, 'wb') as f:
    torch.save(model, f)



if have_test_data:
    for drama in ['郎君不如意','101次抢婚','遇见你的那天','治愈系恋人','少年歌行']:
        test_data_path = f'emb_train_data/emb_classification_test.json'
        x_val = []
        y_val = []
        with open(test_data_path, "r") as f:
            test_data = json.load(f)
        for elem in test_data:
            if drama not in elem['position']:
                continue
            embedding1 = np.load(elem['emb1'])
            embedding2 = np.load(elem['emb2'])
            similarity = elem['similarity']
            combined_embedding = np.concatenate([[similarity],embedding1, embedding2])
            pseudo_label = int(elem['label'])
            x_val.append(combined_embedding)
            y_val.append(pseudo_label)
        x_test = np.array(x_val)
        y_test = np.array(y_val)
        print(f"测试集大小: X_test: {x_test.shape}, y_test: {y_test.shape}")
        assert len(x_test) == len(y_test), "测试集特征和标签样本数量不一致"
        with open(model_path, 'rb') as f:
            model = torch.load(f)
        y_pred_proba = model.predict_proba(x_test)[:, 1]  # 获取正类的概率
        y_pred = (y_pred_proba > 0.5).astype(int)
        accuracy = accuracy_score(y_test, y_pred)
        roc_auc = roc_auc_score(y_test, y_pred_proba)
        precision = precision_score(y_test, y_pred)
        recall = recall_score(y_test, y_pred)
        f1 = f1_score(y_test, y_pred)

        print(f'模型准确率: {accuracy * 100:.2f}%')
        print(f'ROC AUC: {roc_auc:.4f}')
        print(classification_report(y_test, y_pred))