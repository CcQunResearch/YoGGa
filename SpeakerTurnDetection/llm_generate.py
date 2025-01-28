from transformers import AutoTokenizer, AutoModelForCausalLM
import torch
import torch.nn.functional as F
class textGenerator:
    def __init__(self, model_id: str):
        self.model_id = model_id
        self.model = AutoModelForCausalLM.from_pretrained(model_id, torch_dtype="auto", device_map="auto", low_cpu_mem_usage=True, trust_remote_code=True)
        self.tokenizer = AutoTokenizer.from_pretrained(model_id, padding_side='left', trust_remote_code=True)

    def generate_with_probs(self, prompt: str, max_gen_tokens=512):
        # 对输入进行编码
        encoded_input = self.tokenizer(prompt, return_tensors="pt", padding=True, truncation=True)
        input_ids = encoded_input.input_ids.cuda()
        attention_mask = encoded_input.attention_mask.cuda()

        generated_ids = input_ids
        target_token_probs = []
    
        with torch.no_grad():
            # token_sp_id = self.tokenizer.convert_tokens_to_ids("<")
            vocab = self.tokenizer.get_vocab()
            target_char = "<"  
            char_ids = [token_id for token, token_id in vocab.items() if target_char in token]

            # print(f"All IDs containing '{target_char}': {char_ids}")
            token_none_id = self.tokenizer.convert_tokens_to_ids("None")
            token_0_id = self.tokenizer.convert_tokens_to_ids("0")
            token_1_id = self.tokenizer.convert_tokens_to_ids("1")
            flag = False
    
            for i in range(max_gen_tokens):
                outputs = self.model(input_ids=generated_ids, attention_mask=attention_mask)
                logits = outputs.logits

                next_token_logits = logits[:, -1, :]
                probs = F.softmax(next_token_logits, dim=-1)

                # 采样下一个 token
                next_token_id = torch.multinomial(probs, num_samples=1)
                if probs[0, token_0_id].item() + probs[0, token_1_id].item() + probs[0, token_none_id].item() > 0.3 and flag:
                    token_0_prob = probs[0, token_0_id].item()
                    token_1_prob = probs[0, token_1_id].item()

                    target_token_probs.append((token_0_prob, token_1_prob))
                    flag = False
                
                if next_token_id.item() in char_ids or str(self.tokenizer.decode([next_token_id.item()])) == target_char:
                    flag = True

                generated_ids = torch.cat([generated_ids, next_token_id.cuda()], dim=-1)
                new_attention = torch.ones((attention_mask.shape[0], 1), device=attention_mask.device)
                attention_mask = torch.cat([attention_mask, new_attention], dim=1)
    
                if next_token_id.item() == self.tokenizer.eos_token_id:
                    break
    
        # 解码生成的文本
        decoded_output = self.tokenizer.decode(generated_ids[0], skip_special_tokens=True)
    
        # 释放CUDA内存
        del input_ids, attention_mask, generated_ids
        torch.cuda.empty_cache()

        return decoded_output, target_token_probs
    def generate_with_probs_batch(self, prompts: list, max_gen_tokens=512,prompt_flag='01'):
        # 对输入进行批量编码
        print(f"Generating {len(prompts)} sequences...")
        encoded_input = self.tokenizer(prompts, return_tensors="pt", padding=True, truncation=True)
        input_ids = encoded_input.input_ids.cuda()
        attention_mask = encoded_input.attention_mask.cuda()

        batch_size = input_ids.shape[0]
        generated_ids = input_ids.clone()
        target_token_probs = [[] for _ in range(batch_size)]

        with torch.no_grad():
            vocab = self.tokenizer.get_vocab()
            target_char = "<"
            char_ids = [token_id for token, token_id in vocab.items() if target_char in token]

            token_none_id = self.tokenizer.convert_tokens_to_ids("None")
            #  change
            if prompt_flag == '01':
                token_0_id = self.tokenizer.convert_tokens_to_ids("0")
                token_1_id = self.tokenizer.convert_tokens_to_ids("1")
            else:
                token_0_id = self.tokenizer.convert_tokens_to_ids("A")
                token_1_id = self.tokenizer.convert_tokens_to_ids("B")

            flags = [False] * batch_size

            for i in range(max_gen_tokens):
                outputs = self.model(input_ids=generated_ids, attention_mask=attention_mask)
                logits = outputs.logits[:, -1, :]
                probs = F.softmax(logits, dim=-1)
                if torch.any(torch.isnan(probs)) or torch.any(torch.isinf(probs)):
                    print("警告: probs 中存在 NaN 或 Inf 值！")
                    probs = torch.nan_to_num(probs, nan=0.0, posinf=1.0, neginf=0.0)
                next_token_ids = torch.multinomial(probs, num_samples=1)
                

                for idx in range(batch_size):
                    if (probs[idx, token_0_id].item() + probs[idx, token_1_id].item() + probs[idx, token_none_id].item() > 0.3 and flags[idx]):
                        token_0_prob = probs[idx, token_0_id].item()
                        token_1_prob = probs[idx, token_1_id].item()
                        target_token_probs[idx].append((token_0_prob, token_1_prob))
                        flags[idx] = False

                    if next_token_ids[idx].item() in char_ids or str(self.tokenizer.decode([next_token_ids[idx].item()])) == target_char:
                        flags[idx] = True

                generated_ids = torch.cat([generated_ids, next_token_ids.cuda()], dim=1)
                new_attention = torch.ones((attention_mask.shape[0], 1), device=attention_mask.device)
                attention_mask = torch.cat([attention_mask, new_attention], dim=1)

                if all(next_token_id.item() == self.tokenizer.eos_token_id for next_token_id in next_token_ids):
                    break

        decoded_output = [self.tokenizer.decode(generated_ids[i], skip_special_tokens=True) for i in range(batch_size)]

        del input_ids, attention_mask, generated_ids
        torch.cuda.empty_cache()

        return decoded_output, target_token_probs

    def generate(self, prompt: str, n=1, temperature=0.6, top_p=0.9, max_gen_tokens=64):
        encoded_input = self.tokenizer(prompt, return_tensors="pt", padding=True,truncation=False)
        input_ids = encoded_input.input_ids.cuda()
        attention_mask = encoded_input.attention_mask.cuda()
        pad_token_id = self.tokenizer.pad_token_id or self.tokenizer.eos_token_id

        # Generate text
        with torch.no_grad():
            generated_ids = self.model.generate(
                input_ids,
                attention_mask=attention_mask,
                num_beams=3,
                max_new_tokens=max_gen_tokens,
                num_return_sequences=n,
                do_sample=True,
                temperature=temperature,
                top_p=top_p,
                pad_token_id=pad_token_id,
            )

        outputs = self.tokenizer.batch_decode(generated_ids, skip_special_tokens=True)

        # Clear CUDA cache
        del input_ids
        del attention_mask
        del generated_ids
        torch.cuda.empty_cache()

        return outputs
    def generate_batch(self, prompts: list, n=1, temperature=0.95, top_p=0.95, top_k=30, max_gen_tokens=96):
        # 使用 tokenizer 进行批量编码
        encoded_input = self.tokenizer(prompts, return_tensors="pt", padding=True, truncation=True)
        input_ids = encoded_input.input_ids.cuda()
        attention_mask = encoded_input.attention_mask.cuda()
        pad_token_id = self.tokenizer.pad_token_id or self.tokenizer.eos_token_id
        
        
        # 从概率分布中生成文本
        generated_ids = self.model.generate(
            input_ids,
            attention_mask=attention_mask,
            num_beams=n,
            max_new_tokens=max_gen_tokens,
            num_return_sequences=n,
            do_sample=True,
            temperature=temperature,
            top_p=top_p,
            top_k=top_k,
            pad_token_id=pad_token_id,
        )

        outputs = self.tokenizer.batch_decode(generated_ids, skip_special_tokens=True)
        
        # 释放CUDA内存
        del input_ids
        del attention_mask
        del generated_ids
        torch.cuda.empty_cache()
        return outputs  



