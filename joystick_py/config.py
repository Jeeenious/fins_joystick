# -*- coding: utf-8 -*-
"""从 config/config.yaml 加载手柄参数"""
import os
import yaml

_cfg_path = os.path.join(os.path.dirname(__file__), "../config/config.yaml")
with open(_cfg_path, "r") as f:
    _cfg = yaml.safe_load(f)

FPS = _cfg["control"]["fps"]
