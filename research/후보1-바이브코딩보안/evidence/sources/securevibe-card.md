---
language:
- en
license: mit
task_categories:
- text-generation
tags:
- code
- security
- benchmark
---

# SecureVibeBench: First Secure Vibe Coding Benchmark

SecureVibeBench is a benchmark consisting of 105 C/C++ secure coding tasks sourced from 41 projects in OSS-Fuzz for code agents. It is designed to evaluate secure vibe coding by reconstructing real-world scenarios where human developers introduced vulnerabilities.

- **Paper:** [SecureVibeBench: Benchmarking Secure Vibe Coding of AI Agents via Reconstructing Vulnerability-Introducing Scenarios](https://huggingface.co/papers/2509.22097)
- **Repository:** [iCSawyer/SecureVibeBench](https://github.com/iCSawyer/SecureVibeBench)
- **Venue:** ACL 2026 Main Conference

## Usage

```python
from datasets import load_dataset

ds = load_dataset("iCSawyer/SecureVibeBench")
```

## Fields

| Column | Description |
|--------|-------------|
| `localid` | the task id (from ARVO) |
| `repo_url` | the URL of the target repository |
| `vic` | the hash of base commit (vulnerability-inducing commit) |
| `repo_cwd` | the working directory inside the container |
| `description` | the requirement of this task |

## Citation

```bibtex
@misc{chen2026securevibebenchevaluatingsecurecoding,
      title={SecureVibeBench: Evaluating Secure Coding Capabilities of Code Agents with Realistic Vulnerability Scenarios}, 
      author={Junkai Chen and Huihui Huang and Yunbo Lyu and Junwen An and Jieke Shi and Chengran Yang and Ting Zhang and Haoye Tian and Yikun Li and Zhenhao Li and Xin Zhou and Xing Hu and David Lo},
      year={2026},
      eprint={2509.22097},
      archivePrefix={arXiv},
      primaryClass={cs.SE},
      url={https://arxiv.org/abs/2509.22097}, 
}
```