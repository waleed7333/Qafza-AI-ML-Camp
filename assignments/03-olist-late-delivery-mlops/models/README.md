# Models

Production inference does **not** load a model from this directory.

The selected fitted model is registered in MLflow. The API resolves the configured registered-model alias (default: `champion`) and loads the model from the MLflow Model Registry / artifact store.

This directory is reserved for local export/debug material only and remains outside the production loading path.
