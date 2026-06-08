from __future__ import annotations
import pandas as pd
import re
#Nebula数据容器 统一接口
class NebulaData:
    '''NebulaData类:Nebula的数据类'''
    def __init__(
        self,
        features: pd.DataFrame,
        annotations: pd.DataFrame,
        metadata: pd.DataFrame
    ):
        self.features = features#代谢特征定量矩阵
        self.annotations = annotations#代谢特征注释信息
        self.metadata = metadata#样本元数据

