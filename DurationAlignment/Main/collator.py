import torch
from utils import *


class SFTCollator:
    def __init__(self, tokenizer, padding=True, truncation=False, return_token_type_ids=True):
        self.tokenizer = tokenizer
        self.padding = padding
        self.truncation = truncation
        self.return_token_type_ids = return_token_type_ids

    def __call__(self, batch):
        text_batch = []
        for instance in batch:
            text_batch.append([instance["instruction"], instance["output"]])

        encodings = self.tokenizer(text_batch,
                                   padding=self.padding,
                                   truncation=self.truncation,
                                   return_token_type_ids=self.return_token_type_ids,
                                   return_tensors="pt")
        encodings['input_ids'] = encodings['input_ids'].to(torch.int32)
        encodings['attention_mask'] = encodings['attention_mask'].to(torch.int8)
        encodings['token_type_ids'] = encodings['token_type_ids'].to(torch.int8)

        labels = encodings["input_ids"].clone()
        labels[encodings["token_type_ids"] == 0] = -100
        result = {
            "input_ids": encodings["input_ids"],
            "attention_mask": encodings["attention_mask"],
            "labels": labels.to(torch.int64)
        }
        return result


class DPOCollator:
    def __init__(self, tokenizer, padding=True, truncation=False, return_token_type_ids=True, add_kl_penalty=True):
        self.tokenizer = tokenizer
        self.padding = padding
        self.truncation = truncation
        self.return_token_type_ids = return_token_type_ids
        self.add_kl_penalty = add_kl_penalty

    def __call__(self, batch):
        chosen_text_batch = []
        rejected_text_batch = []
        complete_text_batch = []
        # exist_complete = []
        for instance in batch:
            chosen_text_batch.append([instance["instruction"], instance["chosen"]])
            rejected_text_batch.append([instance["instruction"], instance["rejected"]])
            if self.add_kl_penalty:
                # if instance["complete"] in exist_complete:
                #     continue
                # exist_complete.append(instance["complete"])
                complete_text_batch.append([instance["instruction"], instance["complete"]])
        text_batch = chosen_text_batch + rejected_text_batch

        encodings = self.tokenizer(text_batch,
                                   padding=self.padding,
                                   truncation=self.truncation,
                                   return_token_type_ids=self.return_token_type_ids,
                                   return_tensors="pt")
        encodings['input_ids'] = encodings['input_ids'].to(torch.int32)
        encodings['attention_mask'] = encodings['attention_mask'].to(torch.int8)
        encodings['token_type_ids'] = encodings['token_type_ids'].to(torch.int8)
        labels = encodings["input_ids"].clone()
        labels[encodings["token_type_ids"] == 0] = -100
        result = {
            "input_ids": encodings["input_ids"],
            "attention_mask": encodings["attention_mask"],
            "labels": labels
        }

        if self.add_kl_penalty:
            complete_encodings = self.tokenizer(complete_text_batch,
                                                padding=self.padding,
                                                truncation=self.truncation,
                                                return_token_type_ids=self.return_token_type_ids,
                                                return_tensors="pt")
            complete_encodings['input_ids'] = complete_encodings['input_ids'].to(torch.int32)
            complete_encodings['attention_mask'] = complete_encodings['attention_mask'].to(torch.int8)
            complete_encodings['token_type_ids'] = complete_encodings['token_type_ids'].to(torch.int8)
            complete_labels = complete_encodings["input_ids"].clone()
            complete_labels[complete_encodings["token_type_ids"] == 0] = -100
            result["complete_input_ids"] = complete_encodings["input_ids"]
            result["complete_attention_mask"] = complete_encodings["attention_mask"]
            result["complete_labels"] = complete_labels

        return result


class PPOCollator:
    def __init__(self, tokenizer, padding=True, truncation=False, return_token_type_ids=True):
        self.tokenizer = tokenizer
        self.padding = padding
        self.truncation = truncation
        self.return_token_type_ids = return_token_type_ids

    def __call__(self, batch):
        text_batch = []
        type_id_map_batch = []
        advantage_batch = []
        for instance in batch:
            text_batch.append(instance["texts"])
            type_id_map_batch.append(instance["type_id_map"])
            advantage_batch.append(instance["advantage"])

        input_ids_list = []
        attention_mask_list = []
        token_type_ids_list = []
        for i, texts in enumerate(text_batch):
            encodings = self.tokenizer(texts, add_special_tokens=True)
            encodings['token_type_ids'] = [[type_id] * len(ids) for type_id, ids in enumerate(encodings['input_ids'])]

            input_ids_list.append(sum(encodings['input_ids'], []))
            attention_mask_list.append(sum(encodings['attention_mask'], []))
            token_type_ids_list.append(sum(encodings['token_type_ids'], []))

        result = {
            "input_ids": pad_list(input_ids_list, padding_value=self.tokenizer.pad_token_id).to(torch.int32),
            "attention_mask": pad_list(attention_mask_list, padding_value=0).to(torch.int8),
            "token_type_ids": pad_list(token_type_ids_list, padding_value=0).to(torch.int8),
            "type_id_maps": type_id_map_batch,
            "advantages": advantage_batch
        }
        return result


class DPCollator:
    def __init__(self, tokenizer, padding=True, truncation=False):
        self.tokenizer = tokenizer
        self.padding = padding
        self.truncation = truncation

    def __call__(self, batch):
        text_batch = []
        targets = []
        for instance in batch:
            text_batch.append(instance["input"])
            targets.append(instance["output"])

        encodings = self.tokenizer(text_batch,
                                   padding=self.padding,
                                   truncation=self.truncation,
                                   return_tensors="pt")
        result = {
            "input_ids": encodings["input_ids"].to(torch.int32),
            "attention_mask": encodings["attention_mask"].to(torch.int8),
            "targets": torch.FloatTensor(targets).half()
        }
        return result
