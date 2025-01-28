# 【训练】

# 0.【设置配置文件】
# python3 set_config.py

# 1.从a100上下载声纹embbedding
# bash oss.sh #（已有，不用开）

# 2.构建高置信数据
# python3 construct_dataset_pseudo.py

# 3.训练分类模型
python3 emb_classification_train.py
