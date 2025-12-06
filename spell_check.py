
import os
import re
from spellchecker import SpellChecker
import ast

def find_files(directory, extensions):
    for root, _, files in os.walk(directory):
        # Exclude hidden directories and files, as well as node_modules
        if any(part.startswith('.') for part in root.split(os.sep)) or 'node_modules' in root:
            continue
        for file in files:
            if file.endswith(extensions):
                yield os.path.join(root, file)

def extract_text_from_md(filepath):
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    # Remove code blocks
    content = re.sub(r'```.*?```', '', content, flags=re.DOTALL)
    return content

def extract_text_from_py(filepath):
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()

    # Extract docstrings
    try:
        tree = ast.parse(content)
        docstrings = []
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.ClassDef, ast.Module)):
                docstring = ast.get_docstring(node)
                if docstring:
                    docstrings.append(docstring)
    except (SyntaxError, ValueError) as e:
        print(f"Could not parse {filepath}: {e}")
        docstrings = []

    # Extract comments
    comments = re.findall(r'#.*', content)

    return ' '.join(docstrings) + ' '.join(comments)

def spell_check():
    spell = SpellChecker()

    # Custom dictionary of technical terms
    custom_dictionary = {
        'adafactor', 'adalkiran', 'adamw', 'aotautograd', 'api', 'arange', 'args', 'argsort',
        'argumentparser', 'argv', 'arxiv', 'assertionerror', 'auth', 'autoprocessor',
        'autoregressive', 'autotokenizer', 'backend', 'backends', 'backpropagation',
        'basecausallm', 'bigquery', 'bool', 'broadcastable', 'broadcastarguments', 'bsd',
        'bsz', 'bwd', 'causalmask', 'cdot', 'celeba', 'checkpointed', 'checkpointing',
        'chunked', 'ckpt', 'cli', 'cls', 'cnn', 'codegen', 'compilable', 'compuation',
        'conda', 'config', 'configs', 'convnext', 'cpu', 'cuda', 'dataclasses',
        'datacollatorwithpadding', 'dataloader', 'dataloading', 'dataparallel', 'dataset',
        'datasetdict', 'datasets', 'datetime', 'dcn', 'dcp', 'debounce', 'deekseek',
        'deepseek', 'def', 'deps', 'dequantization', 'dequantized', 'dev', 'dict',
        'dictconfig', 'didn', 'dimentsions', 'dirs', 'dist', 'distcp', 'div', 'divied',
        'docstring', 'docstrings', 'doesn', 'dpkg', 'dpo', 'dtensors', 'dtype', 'einsum',
        'eleutherai', 'env', 'eps', 'etc', 'exaple', 'exp', 'experiements', 'fairscale',
        'fakemesh', 'faq', 'ffn', 'filename', 'filenames', 'filenotfounderror', 'filesystem',
        'finetuning', 'floattensor', 'foo', 'foward', 'frac', 'freqcis', 'fsdp', 'fsspec',
        'fullmask', 'fwd', 'gcloud', 'gcp', 'gcr', 'gcs', 'gcsfuse', 'gemm', 'getenv',
        'github', 'gitignore', 'gke', 'gmm', 'googlers', 'googlesql', 'gpt', 'gpu',
        'gpus', 'gqa', 'gspmd', 'gsutil', 'hardcoded', 'hardwares', 'hermeticity', 'hlo',
        'homogeneoussequential', 'homogenoussequential', 'html', 'http', 'https',
        'huggingface', 'hybridmesh', 'hypercomputer', 'hyperparameter', 'hyperparameters',
        'ici', 'idx', 'ilankelman', 'img', 'imtermediate', 'init', 'insujang', 'int',
        'interoperate', 'intro', 'ipynb', 'isn', 'isolatedparallel', 'itelsf', 'jax',
        'jialei', 'jit', 'jobset', 'jpg', 'json', 'jsonl', 'karpathy', 'keyerror',
        'kubectl', 'kwargs', 'lbcp', 'ldots', 'learnable', 'lhs', 'libtpu', 'linearities',
        'llm', 'llms', 'llamadecoderlayer', 'llamaforcausallm', 'llavarmsnorm', 'llava', 'llavaforconditionalgeneration',
        'localmask', 'logits', 'longtensor', 'lookup', 'markshardingfunction', 'matmul',
        'matplotlib', 'maxtext', 'megascale', 'metadata', 'meth', 'mfu', 'minibatch',
        'misc', 'mistralattention', 'mistralmodel', 'mixtral', 'mixtraldecoderlayer',
        'mixtralrmsnorm', 'mla', 'mllamavisionmodel', 'mlp', 'modelargs', 'modeloutput',
        'modulelist', 'mps', 'mscale', 'multi', 'multiheadmask', 'multimodal', 'multipod',
        'multislice', 'mymodel', 'namedsharding', 'nanotron', 'natively', 'nccl', 'neox',
        'newlines', 'nhead', 'noqa', 'norope', 'notimplementederror', 'ntk', 'num',
        'numerics', 'numpy', 'nvidia', 'nvme', 'nwhat', 'offsetted', 'omegaconf', 'oom',
        'optimise', 'org', 'orignal', 'parallelembedding', 'param', 'params',
        'partitioners', 'pathspec', 'pdb', 'pdf', 'peft', 'perceptron', 'perf',
        'performant', 'pil', 'pinterest', 'png', 'postinstall', 'pre', 'precomputes',
        'prefetching', 'prefill', 'prefixtuning', 'preprocesses', 'pretrained',
        'pretrainedconfig', 'pretraining', 'profiler', 'proto', 'protobuf', 'puremodule',
        'pylint', 'pyproject', 'pytest', 'pytorch', 'pytree', 'randint', 'readme',
        'realtime', 'refactor', 'reimplement', 'releated', 'remat', 'rematerialization',
        'rematerialize', 'repo', 'res', 'reshard', 'resharding', 'resnet', 'rgb',
        'rmsnorm', 'runtime', 'runtimes', 'rxstatmetadata', 'safetensor', 'safetensors',
        'scalebyadamstate', 'screenshot', 'sdpa', 'seq', 'seqlen', 'sequnence',
        'setuptools', 'sft', 'sfttrainer', 'shardable', 'sharded', 'shardedmodule',
        'sharder', 'sharding', 'shardings', 'shardingspec', 'shortn', 'shutil',
        'simplelinear', 'softmax', 'soooo', 'splashattentionconfig', 'spmd', 'sqrt',
        'src', 'stablehlo', 'stdout', 'stopsigns', 'str', 'submodule', 'submodules',
        'sudo', 'suppor', 'svg', 'swiglu', 'swin', 'sys', 'tensorboard', 'tensorfloat',
        'tensorflow', 'tflops', 'timestamp', 'tmp', 'todo', 'tokenization', 'tokenize',
        'tokenized', 'tokenizer', 'tokenizers', 'tokenizes', 'toml', 'topk', 'torchax',
        'torcheval', 'torchprime', 'torchrun', 'torchtitan', 'tpu', 'tpus',
        'transformerblock', 'transformerencoderlayer', 'triu', 'tuple', 'tuples', 'txt',
        'ultrascale', 'uncomment', 'unet', 'unked', 'unpermuate', 'unpermute',
        'unsqueeze', 'uri', 'url', 'usr', 'utc', 'utf', 'utils', 'uuid', 'validator',
        'valueerror', 'viz', 'vllm', 'vmap', 'vms', 'vocabparallelembedding', 'vscode',
        'wavelen', 'wich', 'wikitext', 'wildcards', 'workaround', 'workflow',
        'workflows', 'wraper', 'wrt', 'www', 'xad', 'xbb', 'xeventj', 'xeventmetadata',
        'xla', 'xlatensor', 'xpk', 'xplane', 'xrefs', 'xstat', 'xstatb', 'xstatmetadata',
        'yaml', 'yml', 'zpcore'
    }
    spell.word_frequency.load_words(custom_dictionary)

    errors = {}

    for filepath in find_files('.', ('.md', '.py')):
        if filepath.startswith('./.git') or filepath.startswith('./local_dist'):
            continue
        if filepath.endswith('.md'):
            text = extract_text_from_md(filepath)
        elif filepath.endswith('.py'):
            text = extract_text_from_py(filepath)
        else:
            continue

        words = re.findall(r'\b[a-zA-Z]+\b', text)

        misspelled = spell.unknown(words)

        for word in misspelled:
            # Ignore all-caps words (likely acronyms) and words with digits
            if not word.isupper() and not any(char.isdigit() for char in word):
                if word.lower() not in errors:
                    errors[word.lower()] = []
                if filepath not in errors[word.lower()]:
                    errors[word.lower()].append(filepath)

    with open('spelling_errors.md', 'w') as f:
        f.write("# Spelling Errors Report\n\n")
        if not errors:
            f.write("No spelling errors found.\n")
        else:
            for word, files in sorted(errors.items()):
                f.write(f"## {word}\n")
                for file in files:
                    f.write(f"- {file}\n")
                f.write("\n")

if __name__ == "__main__":
    spell_check()
