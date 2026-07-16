from __future__ import annotations
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.pipeline import Pipeline
from preprocessing import transformer

def build_model() -> Pipeline:
    return Pipeline([("preprocess", transformer(False)), ("model", HistGradientBoostingClassifier(max_iter=180, learning_rate=.06, max_leaf_nodes=18, l2_regularization=2.0, random_state=42))])

# So what? Boosting can learn nonlinear interactions such as velocity plus risky route without relying on paid or proprietary tooling.
