import yaml
import os.path as osp

command_a = """# Step 0: 指定使用的环境并定义模型与语言变量
source /data/jovyan/work/yezang/torch_ppu/bin/activate
sft_model="{}"
tr_model="{}"
trpe_model="{}"
lang="{}"
gpus="{}"
model_path="{}"

# Step 1: 数据预处理
cd ConstructDataset
python \[1\]preprocess.py
python \[2-1\]identify_proper_noun.py"""

command_b1 = """# Step 2: PE术语识别
# python \[2-2\]identify_proper_noun.py"""

command_b2 = """# Step 2: PE术语识别
cd ../LLaMA-Factory
# CUDA_VISIBLE_DEVICES=$gpus llamafactory-cli train TermRecognition/train/$trpe_model/$lang/predict.yaml"""

command_c = """# Step 3: SFT与术语识别数据集构建
cd ../ConstructDataset
python \[2-3\]identify_proper_noun.py
python \[3\]construct_dataset.py
python \[4\]construct_tr_dataset.py

# Step 4: 训练SFT模型与术语识别模型
cd ../LLaMA-Factory
CUDA_VISIBLE_DEVICES=$gpus llamafactory-cli train YoukuTranslationSFT/sft_$sft_model_$trpe_model_$lang.yaml
# CUDA_VISIBLE_DEVICES=$gpus llamafactory-cli train YoukuTranslationSFT/tr_$tr_model_$trpe_model_$lang.yaml
rm -r $model_path/llamafactory/$sft_model_$trpe_model/$lang/sft_default/checkpoint*
# rm -r $model_path/llamafactory/$tr_model_$trpe_model/$lang/tr_default/checkpoint*
"""

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
    trpe_mode = config['trpe_mode']
    model_path = config['model_path']
    
    if trpe_mode == 'online':
        command = "\n\n".join([command_a, command_b1, command_c])
    else:
        command = "\n\n".join([command_a, command_b2, command_c])
    
    run_command = command.format(sft_model, tr_model, trpe_model, lang, gpus, model_path)
    run_command = run_command.replace('$sft_model','${sft_model}')
    run_command = run_command.replace('$tr_model','${tr_model}')
    run_command = run_command.replace('$trpe_model','${trpe_model}')
    run_command = run_command.replace('$lang','${lang}')
    run_command = run_command.replace('$gpus','${gpus}')
    run_command = run_command.replace('$model_path','${model_path}')
    with open(osp.join(dirname, 'train_command.sh'), 'w', encoding='utf-8') as file:
        file.write(run_command)