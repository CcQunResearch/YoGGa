import os
import os.path as osp
import json
import torch
import numpy as np
from torch.utils.data import Dataset
from template import *
from utils import *


class SFTDataset(Dataset):
    def __init__(self, file_path, template="default"):
        assert template in ["default", "qwen", "glm4", "llama3"], "template must be in ['default', 'qwen', 'glm4', 'llama3]"
        self.file_path = file_path
        self.template = template

        self.load_data()

    def load_data(self):
        temp = default_template
        if self.template == "qwen":
            temp = qwen_template
        elif self.template == "glm4":
            temp = glm4_template
        elif self.template == "llama3":
            temp = llama3_template

        self.all_data = json.load(open(self.file_path, "r", encoding="utf-8"))
        self.all_data = [{"instruction": temp.format(data["instruction"]), "output": data["output"]} for data in
                         self.all_data]

    def __len__(self):
        return len(self.all_data)

    def __getitem__(self, index):
        return self.all_data[index]


class DPODataset(Dataset):
    def __init__(self, file_path, add_kl_penalty=True, template="default"):
        assert template in ["default", "qwen", "glm4", "llama3"], "template must be in ['default', 'qwen', 'glm4', 'llama3]"
        self.file_path = file_path
        self.template = template
        self.add_kl_penalty = add_kl_penalty

        self.load_data()

    def load_data(self):
        temp = default_template
        if self.template == "qwen":
            temp = qwen_template
        elif self.template == "glm4":
            temp = glm4_template
        elif self.template == "llama3":
            temp = llama3_template

        self.raw_data = json.load(open(self.file_path, "r", encoding="utf-8"))
        self.all_data = []
        for data in self.raw_data:
            src_prompt = data["src_prompt"]
            for sample in data["sampling_records"]:
                if sample["same_flag"] is not True:
                    one_data = {"instruction": temp.format(src_prompt) + sample["temp_prompt"] + sample["src"] + "(",
                                "chosen": sample["chosen"], "rejected": sample["rejected"]}
                    if self.add_kl_penalty:
                        one_data["complete"] = data["single"]["accept"]
                    self.all_data.append(one_data)

    def __len__(self):
        return len(self.all_data)

    def __getitem__(self, index):
        return self.all_data[index]


class PPODataset(Dataset):
    def __init__(self, file_path, args):
        assert args.template in ["default", "qwen", "glm4", "llama3"], "template must be in ['default', 'qwen', 'glm4', 'llama3]"
        assert args.measure in ["consis", "shorter"], "measure must be in ['consis', 'shorter']"
        self.file_path = file_path
        self.template = args.template
        self.measure_type = args.measure
        self.w1 = args.w1
        self.w2 = args.w2
        self.normalize_advantage = args.normalize_advantage
        self.clip_advantage = args.clip_advantage

        self.load_data()

    def load_data(self):
        temp = default_template
        if self.template == "qwen":
            temp = qwen_template
        elif self.template == "glm4":
            temp = glm4_template
        elif self.template == "llama3":
            temp = llama3_template

        self.raw_data = json.load(open(self.file_path, "r", encoding="utf-8"))
        self.all_data = []
        all_advantages = []
        for data in self.raw_data:
            measures = []
            for sample in data["sampling_records"]:
                src_duration = sample["src_duration"]
                tar_durations = sample["tar_duration"]
                if self.measure_type == "consis":
                    measure = [-penalty(src_duration, tar, w1=self.w1, w2=self.w2) for tar in tar_durations]
                else:
                    measure = [-tar for tar in tar_durations]
                measures.append(measure)
            mean_measures = [np.mean(measure) for measure in measures]

            train_measures = []
            index_2_type_id = {}
            token_type_id = 0
            texts = [temp.format(data["src_prompt"])]
            for i, duration in enumerate(data["train"]["duration"]):
                if self.measure_type == "consis":
                    train_measures.append(
                        -penalty(duration["src_duration"], duration["tar_duration"], w1=self.w1, w2=self.w2))
                elif self.measure_type == "shorter":
                    train_measures.append(-duration["tar_duration"])

                if i == 0:
                    texts += [duration["src"] + "("]
                else:
                    texts += [")" + duration["src"] + "("]

                texts += [duration["tar"]]
                token_type_id += 2
                index_2_type_id[i] = token_type_id

                if i == len(data["train"]["duration"]) - 1:
                    texts += [")"]
            advantage = [train_measures[i] - mean_measures[i] for i in range(len(train_measures))]

            if self.clip_advantage > 0:
                advantage = np.clip(advantage, -self.clip_advantage, self.clip_advantage).tolist()

            if len(data["sampling_records"]) != len(advantage):
                continue

            for i, sample in enumerate(data["sampling_records"]):
                if sample["same_flag"]:
                    advantage[i] = 0

            if self.normalize_advantage:
                all_advantages += advantage

            self.all_data.append({"texts": texts, "type_id_map": index_2_type_id, "advantage": advantage})

        if self.normalize_advantage:
            all_advantages = [abs(val) for val in all_advantages]
            scale_factor = max(all_advantages)
            for i in range(len(self.all_data)):
                self.all_data[i]["advantage"] = [val / scale_factor for val in self.all_data[i]["advantage"]]

    def __len__(self):
        return len(self.all_data)

    def __getitem__(self, index):
        return self.all_data[index]


# class PPODataset(Dataset):
#     def __init__(self, file_path, measure_type="consis", w1=0.8, w2=1.0, template="default"):
#         assert template in ["default", "qwen"], "template must be in ['default', 'qwen']"
#         assert measure_type in ["consis", "shorter"], "measure must be in ['consis', 'shorter']"
#         self.file_path = file_path
#         self.template = template
#         self.measure_type = measure_type
#         self.w1 = w1
#         self.w2 = w2
#
#         self.load_data()
#
#     def load_data(self):
#         temp = default_template
#         if self.template == "qwen":
#             temp = qwen_template
#
#         self.raw_data = json.load(open(self.file_path, "r", encoding="utf-8"))
#         self.all_data = []
#         for data in self.raw_data:
#             measures = [[] for _ in range(len(data["sampling_records"][0]["duration"]))]
#             for sample in data["sampling_records"]:
#                 for i, duration in enumerate(sample["duration"]):
#                     if self.measure_type == "consis":
#                         measures[i].append(
#                             penalty(duration["src_duration"], duration["tar_duration"], w1=self.w1, w2=self.w2))
#                     elif self.measure_type == "shorter":
#                         measures[i].append(-duration["tar_duration"])
#                     measures[i] = list(set(measures[i]))
#
#             mean_measures = [np.mean(measure) for measure in measures]
#             train_measures = []
#             index_2_type_id = {}
#             token_type_id = 0
#             texts = [temp.format(data["src_prompt"])]
#             for i, duration in enumerate(data["train"]["duration"]):
#                 if self.measure_type == "consis":
#                     train_measures.append(
#                         penalty(duration["src_duration"], duration["tar_duration"], w1=self.w1, w2=self.w2))
#                 elif self.measure_type == "shorter":
#                     train_measures.append(-duration["tar_duration"])
#
#                 if i == 0:
#                     texts += [duration["src"] + "("]
#                 else:
#                     texts += [")" + duration["src"] + "("]
#
#                 texts += [duration["tar"]]
#                 token_type_id += 2
#                 index_2_type_id[i] = token_type_id
#
#                 if i == len(data["train"]["duration"]) - 1:
#                     texts += [")"]
#             # print(train_measures)
#             # print(mean_measures)
#             # print()
#             advantage = [train_measures[i] - mean_measures[i] for i in range(len(train_measures))]
#             same_flags = data['same_flag']
#             for i, flag in enumerate(same_flags):
#                 if flag:
#                     advantage[i] = 0
#             self.all_data.append({"texts": texts, "type_id_map": index_2_type_id, "advantage": advantage})
#
#     def __len__(self):
#         return len(self.all_data)
#
#     def __getitem__(self, index):
#         return self.all_data[index]


class DPDataset(Dataset):
    def __init__(self, file_path):
        self.file_path = file_path

        self.load_data()

    def load_data(self):
        self.all_data = json.load(open(self.file_path, "r", encoding="utf-8"))

    def __len__(self):
        return len(self.all_data)

    def __getitem__(self, index):
        return self.all_data[index]
