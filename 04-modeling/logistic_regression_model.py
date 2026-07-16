from __future__ import annotations
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from preprocessing import transformer

def build_model() -> Pipeline:
    return Pipeline([("preprocess", transformer(True)), ("model", LogisticRegression(class_weight="balanced", max_iter=1000, C=.35, random_state=42))])

# So what? Class weighting makes rare fraud consequential during training, while logistic regression provides an interpretable benchmark.
