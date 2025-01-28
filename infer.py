import yaml
import os.path as osp

command = """# Step 0: 指定使用的环境并定义模型与语言变量
source /data/jovyan/work/yezang/torch_ppu/bin/activate
sft_model="{}"
tr_model="{}"
trpe_model="{}"
lang="{}"
gpus="{}"
port="{}"

# Step 1: 测试集术语推理数据集构建
cd ConstructDataset
# python \[5-1\]extract_test_data.py

# # Step 2: 测试集术语识别
# cd ../LLaMA-Factory
# CUDA_VISIBLE_DEVICES=$gpus llamafactory-cli train TermRecognition/test/$tr_model_$trpe_model/$lang/predict.yaml
# nohup env CUDA_VISIBLE_DEVICES=$gpus API_PORT=$port llamafactory-cli api TermRecognition/test/$tr_model_$trpe_model/$lang/api.yaml > tr_infer.out &
# sleep 1m

# cd ../ConstructDataset
# python \[5-2\]extract_test_data.py
# ps -def | grep $tr_model_$trpe_model | grep -v grep | awk '{{print $2}}' | xargs kill -9

# # Step 3: 测试集构建
# cd ../ConstructDataset
# python \[5-3\]extract_test_data.py

# # Step 4: 测试集推理
# cd ../LLaMA-Factory
# CUDA_VISIBLE_DEVICES=$gpus llamafactory-cli train YoukuTranslationSFT/predict_$sft_model_$tr_model_$trpe_model_$lang.yaml
# nohup env CUDA_VISIBLE_DEVICES=$gpus API_PORT=$port llamafactory-cli api YoukuTranslationSFT/api_$sft_model_$tr_model_$trpe_model_$lang.yaml > sft_infer.out &
# sleep 1m

# cd ../ConstructDataset
# python \[5-4\]extract_test_data.py
# ps -def | grep api_$sft_model_$tr_model_$trpe_model_$lang.yaml | grep -v grep | awk '{{print $2}}' | xargs kill -9

# # Step 5: 生成内容处理
# cd ../ConstructDataset
# python \[6\]prediction_2_subtitle.py

# Step 6: 翻译质量评估
cd ../ConstructDataset
python \[7\]evaluate.py"""

# command_a = """# Step 0: 指定使用的环境并定义模型与语言变量
# source /data/jovyan/work/yezang/torch_ppu/bin/activate
# sft_model="{}"
# tr_model="{}"
# trpe_model="{}"
# lang="{}"
# gpus="{}"
# port="{}"

# # Step 1: 测试集术语推理数据集构建
# cd ConstructDataset
# python \[5-1\]extract_test_data.py"""

# command_b1 = """# Step 2: 测试集术语识别
# cd ../LLaMA-Factory
# nohup env CUDA_VISIBLE_DEVICES=$gpus API_PORT=$port llamafactory-cli api TermRecognition/test/$tr_model_$trpe_model/$lang/api.yaml > tr_infer.out &
# sleep 1m

# cd ../ConstructDataset
# python \[5-2\]extract_test_data.py
# ps -def | grep TermRecognition/test/$tr_model_$trpe_model/$lang/api.yaml | grep -v grep | awk '{{print $2}}' | xargs kill -9"""

# command_b2 = """# Step 2: 测试集术语识别
# cd ../LLaMA-Factory
# CUDA_VISIBLE_DEVICES=$gpus llamafactory-cli train TermRecognition/test/$tr_model_$trpe_model/$lang/predict.yaml"""

# command_c = """# Step 3: 测试集构建
# cd ../ConstructDataset
# python \[5-3\]extract_test_data.py"""

# command_d1 = """# Step 4: 测试集推理
# cd ../LLaMA-Factory
# nohup env CUDA_VISIBLE_DEVICES=$gpus API_PORT=$port llamafactory-cli api YoukuTranslationSFT/api_$sft_model_$tr_model_$trpe_model_$lang.yaml > sft_infer.out &
# sleep 1m

# cd ../ConstructDataset
# python \[5-4\]extract_test_data.py
# ps -def | grep YoukuTranslationSFT/api_$sft_model_$tr_model_$trpe_model_$lang.yaml | grep -v grep | awk '{{print $2}}' | xargs kill -9"""

# command_d2 = """# Step 4: 测试集推理
# cd ../LLaMA-Factory
# CUDA_VISIBLE_DEVICES=$gpus llamafactory-cli train YoukuTranslationSFT/predict_$sft_model_$tr_model_$trpe_model_$lang.yaml"""

# command_e = """# Step 5: 生成内容处理
# cd ../ConstructDataset
# python \[6\]prediction_2_subtitle.py"""

if __name__ == "__main__":
    dirname = osp.dirname(osp.abspath(__file__))
    config_path = osp.join(dirname, 'config.yaml')
    with open(config_path, 'r', encoding='utf-8') as file:
        config = yaml.safe_load(file)
    sft_model = config['sft_model']
    tr_model = config['tr_model']
    trpe_model = config['trpe_model']
    lang = config['lang']
    gpus = config['gpus']
    port = config['port']
    # infer_mode = config['infer_mode']
    
    # if infer_mode == 'online':
    #     command = "\n\n".join([command_a, command_b1, command_c,command_d1, command_e])
    # else:
    #     command = "\n\n".join([command_a, command_b2, command_c,command_d2, command_e])
    
    run_command = command.format(sft_model, tr_model, trpe_model, lang, gpus, port)
    run_command = run_command.replace('$sft_model','${sft_model}')
    run_command = run_command.replace('$tr_model','${tr_model}')
    run_command = run_command.replace('$trpe_model','${trpe_model}')
    run_command = run_command.replace('$lang','${lang}')
    run_command = run_command.replace('$gpus','${gpus}')
    run_command = run_command.replace('$port','${port}')
    with open(osp.join(dirname, 'infer_command.sh'), 'w', encoding='utf-8') as file:
        file.write(run_command)