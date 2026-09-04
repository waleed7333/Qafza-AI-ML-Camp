# Model results

Validation average precision selected logistic regression (`C=1.0`, `class_weight=None`). Threshold `0.1570` maximized validation F1.

| Evaluation | Accuracy | Precision | Recall | F1 | ROC-AUC | PR-AUC |
|---|---:|---:|---:|---:|---:|---:|
| Dummy validation | 0.9569 | 0.0000 | 0.0000 | 0.0000 | 0.5000 | 0.0431 |
| Final validation | 0.8913 | 0.1628 | 0.3670 | 0.2255 | 0.7740 | 0.1374 |
| Dummy test | 0.9572 | 0.0000 | 0.0000 | 0.0000 | 0.5000 | 0.0428 |
| Final test | 0.7988 | 0.0646 | 0.2742 | 0.1046 | 0.6514 | 0.0784 |

Test was evaluated once after all choices were frozen.
