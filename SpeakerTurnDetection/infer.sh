#前置条件：待推理数据集的声纹embedding已经提取好
# 0.【设置配置文件】
# python3 set_config.py

# 1.【推理-声纹分类模型】
# 1.1 用分类模型给csv测试集打标
# python3 emb_classification_infer.py

# 2.【推理-pe】
# 2.1 多线程用pe给数据集打标
# python3 llm_pe_main.py

# 3.【融合】
# 3.1 加权融合概率
python3 weighted_fusion.py
# 3.2 计算融合后的总准确率（若是测试集则打开此项，训练集打标无需打开此项）
python3 get_testcsv_metric.py