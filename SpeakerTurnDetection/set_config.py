import yaml
out_files = '../config.yaml'
in_files = 'config.yaml'
with open(out_files, 'r') as file:
    out_config = yaml.safe_load(file)

with open(in_files, 'r') as file:
    in_config = yaml.safe_load(file)

in_config['construct_dataset_pseudo']['high_threshold'] = out_config['tau_t']
in_config['construct_dataset_pseudo']['low_threshold'] = out_config['tau_b']
in_config['weighted_fusion']['w'] = out_config['w']
in_config['pe_infer']['std_pe_model'] = out_config['std_pe_model']

with open(in_files, 'w') as file:
    yaml.safe_dump(in_config, file)