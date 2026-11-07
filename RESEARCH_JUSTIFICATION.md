# Research References & Technical Justification

This document compiles peer-reviewed literature, official specifications, and benchmark citations supporting the architectural decisions of the **AI-Assisted Information Verification System**.

---

## 1. Sentence-BERT (Semantic Similarity)

* **Title**: *Sentence-BERT: Sentence Embeddings using Siamese BERT-Networks*
* **Authors**: Nils Reimers and Iryna Gurevych
* **Publication Year**: 2019
* **Venue / Publisher**: Proceedings of the 2019 Conference on Empirical Methods in Natural Language Processing (EMNLP 2019)
* **Official Link**: [https://aclanthology.org/D19-1410/](https://aclanthology.org/D19-1410/)
* **Main Contribution**: Introduced Siamese and triplet network architectures on top of BERT/RoBERTa to generate semantically meaningful sentence embeddings that can be compared using cosine similarity with $O(1)$ vector dot products, reducing search latency from hours to milliseconds compared to cross-encoders.
* **Relation to Project**: Used in `sbert_ranker.py` (`sentence-transformers/all-MiniLM-L6-v2`) to rank Google Fact Check records by semantic similarity against the user's claim.
* **What it Justifies**: Justifies using bi-encoders for high-throughput initial semantic matching across large pools of short claim statements.
* **What it Does NOT Justify**: SBERT bi-encoders cannot reliably distinguish logical entailment from logical contradiction because contradictory sentences (e.g., *"Drug X cures illness Y"* vs. *"Drug X does not cure illness Y"*) share near-identical token vocabularies and produce high cosine similarity. SBERT is appropriate for candidate retrieval, but inappropriate for final veracity determination.

---

## 2. MedCPT (Biomedical Information Retrieval)

* **Title**: *MedCPT: Contrastive Pre-trained Transformers with Large-scale PubMed Search Logs for Zero-shot Biomedical Information Retrieval*
* **Authors**: Qiao Jin, Won Kim, Qingyu Chen, Donald C. Comeau, Wilbur J. Lu, and Zhiyong Lu
* **Publication Year**: 2023
* **Venue / Publisher**: *Bioinformatics*, Volume 39, Issue 11, Oxford University Press
* **Official Link**: [https://doi.org/10.1093/bioinformatics/btad651](https://doi.org/10.1093/bioinformatics/btad651) / [PubMed Central PMC10638515](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC10638515/)
* **Main Contribution**: Pre-trained contrastive biomedical transformers on 255 million real-world user search query–click pairs from PubMed search logs. Specifically developed `ncbi/MedCPT-Cross-Encoder` to rerank (query, title + abstract) pairs with specialized biomedical vocabulary understanding.
* **Relation to Project**: Implemented in `scripts/medcpt_rank.py` and invoked by `run_both_rankers.py` to rank candidate PubMed articles.
* **What it Justifies**: Demonstrates that MedCPT outperforms general-purpose semantic models (such as MiniLM or standard BM25) on biomedical search benchmarks (TREC-COVID, NFCorpus, BioASQ). Justifies using domain-specific cross-attention for ranking scientific literature.
* **What it Does NOT Justify**: MedCPT measures *topical query relevance*, not truthfulness or veracity. A paper directly refuting a claim is highly relevant to that claim according to MedCPT. MedCPT is a ranking model, not a fact-checking decision engine.

---

## 3. SciFact (Scientific Claim Verification Benchmark)

* **Title**: *Fact or Fiction: Verifying Scientific Claims*
* **Authors**: David Wadden, Shanchuan Lin, Kyle Lo, Lauren Fratamico, Richard Hahnloser, Edouard Bugnion, and Arman Cohan
* **Publication Year**: 2020
* **Venue / Publisher**: Proceedings of the 2020 Conference on Empirical Methods in Natural Language Processing (EMNLP 2020)
* **Official Link**: [https://aclanthology.org/2020.emnlp-main.609/](https://aclanthology.org/2020.emnlp-main.609/) / [GitHub Repository](https://github.com/allenai/scifact)
* **Main Contribution**: Built an expert-annotated benchmark for verifying biomedical and scientific claims against PubMed research abstracts, annotating claim-evidence relationships as `SUPPORT`, `CONTRADICT`, or `NOT_ENOUGH_INFO` with rationale sentence citations.
* **Relation to Project**: Provided reference claims and ground-truth validation pairs for the project's expanded evaluation dataset (`evaluation_dataset_expanded.csv`).
* **What it Justifies**: Justifies formulating scientific claim verification as an evidence retrieval and Natural Language Inference (NLI) classification task over PubMed abstracts.
* **What it Does NOT Justify**: SciFact uses isolated biomedical abstracts; it does not evaluate multi-source aggregation combining general public fact-checks with PubMed scientific literature.

---

## 4. FEVER (Fact Extraction and VERification)

* **Title**: *FEVER: a Large-scale Dataset for Fact Extraction and VERification*
* **Authors**: James Thorne, Andreas Vlachos, Christos Christodoulopoulos, and Arpit Mittal
* **Publication Year**: 2018
* **Venue / Publisher**: Proceedings of the 2018 Conference of the North American Chapter of the Association for Computational Linguistics (NAACL-HLT 2018)
* **Official Link**: [https://aclanthology.org/N18-1074/](https://aclanthology.org/N18-1074/)
* **Main Contribution**: Formulated the standard automated fact-checking paradigm: document retrieval $\rightarrow$ evidence sentence selection $\rightarrow$ 3-way NLI classification (`SUPPORTS`, `REFUTES`, `NOT ENOUGH INFO`).
* **Relation to Project**: Establishes the foundational theoretical framework adopted by this verification system (retrieval $\rightarrow$ ranking $\rightarrow$ NLI $\rightarrow$ decision engine).
* **What it Justifies**: Justifies evaluating evidence-claim relationships using 3-way classification and measuring pipeline performance through standard classification metrics.
* **What it Does NOT Justify**: FEVER is based on Wikipedia and general knowledge, lacking complex biomedical and clinical trial nuances.

---

## 5. DeBERTa / DeBERTaV3 (Natural Language Inference)

* **Title**: *DeBERTaV3: Improving DeBERTa using ELECTRA-Style Pre-Training with Gradient-Disentangled Embedding Sharing*
* **Authors**: Pengcheng He, Jianwei Gao, and Weizhu Chen
* **Publication Year**: 2023
* **Venue / Publisher**: Proceedings of the 11th International Conference on Learning Representations (ICLR 2023)
* **Official Link**: [https://openreview.net/forum?id=sE7-XhLxHA](https://openreview.net/forum?id=sE7-XhLxHA)
* **Main Contribution**: Introduced disentangled attention (representing token content and relative position in separate vectors) and replaced MLM with replaced token detection, significantly improving NLI benchmark performance on MNLI, SNLI, and ANLI.
* **Relation to Project**: Implemented in `nli_classifier.py` using `cross-encoder/nli-deberta-v3-base` to classify whether evidence entails, contradicts, or is neutral toward the health claim.
* **What it Justifies**: Justifies cross-encoder token interaction for nuanced directional reasoning (premise vs. hypothesis).
* **What it Does NOT Justify**: The model is pre-trained on general NLI datasets (MNLI, SNLI); it can struggle with complex pharmacological dosages or biostatistical sub-analyses unless given clear, uncontaminated evidence context.

---

## 6. Information Retrieval Evaluation Metrics (TREC Standards)

* **Title**: *TREC: Experiment and Evaluation in Information Retrieval*
* **Authors**: Ellen M. Voorhees and Donna K. Harman (Editors)
* **Publication Year**: 2005
* **Publisher**: MIT Press (Digital Open Access)
* **Official Link**: [https://mitpress.mit.edu/9780262220736/](https://mitpress.mit.edu/9780262220736/)
* **Main Contribution**: Standardized evaluation protocols for search and ranking systems, establishing Precision@K, Recall@K, Mean Reciprocal Rank (MRR), and Discounted Cumulative Gain (NDCG) as formal metrics to evaluate ranking quality independently of downstream classification.
* **Relation to Project**: Implemented in `evaluate_ranking.py` to evaluate the retrieval and ranking models separately from the final claim verdict classification.
* **What it Justifies**: Justifies evaluating document rankers (SBERT, MedCPT) using position-aware metrics rather than classification accuracy.
* **What it Does NOT Justify**: Ranking metrics cannot evaluate whether a final claim assessment is correct; they only measure whether relevant documents appear near the top of the retrieved list.
