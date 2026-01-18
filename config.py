"""
简化的配置管理
"""

import os
import json
from typing import Dict, Any

class AnalysisConfig:
    """分析配置类"""

    def __init__(self):
        # 默认配置
        self.analysis_mode = "rule_based"  # rule_based, ai_enhanced, hybrid
        self.ai_config = {'enabled': False}

        # 评分权重配置
        self.rule_weight = 0.7
        self.ai_weight = 0.3

        # 质量阈值
        self.min_score_threshold = 5.0
        self.duration_range = (120, 180)  # 2-3分钟

        # 加载保存的配置
        self._load_config()

    def set_ai_mode(self, ai_config: Dict[str, Any]):
        """设置AI分析模式"""
        if ai_config.get('enabled'):
            self.analysis_mode = "ai_enhanced"
            self.ai_config = ai_config
            self._save_config()
            return True
        return False

    def set_hybrid_mode(self, ai_config: Dict[str, Any], rule_weight: float = 0.7):
        """设置混合分析模式"""
        if ai_config.get('enabled'):
            self.analysis_mode = "hybrid"
            self.ai_config = ai_config
            self.rule_weight = rule_weight
            self.ai_weight = 1.0 - rule_weight
            self._save_config()
            return True
        return False

    def is_ai_enabled(self) -> bool:
        """检查是否启用AI"""
        return self.ai_config.get('enabled', False)

    def get_ai_config(self) -> Dict[str, Any]:
        """获取AI配置"""
        return self.ai_config

    def _save_config(self):
        """保存配置到文件"""
        try:
            config_data = {
                'analysis_mode': self.analysis_mode,
                'ai_config': self.ai_config,
                'rule_weight': self.rule_weight,
                'ai_weight': self.ai_weight
            }

            with open('.config.json', 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"⚠ 保存配置失败: {e}")

    def _load_config(self):
        """从文件加载配置"""
        try:
            if os.path.exists('.config.json'):
                with open('.config.json', 'r', encoding='utf-8') as f:
                    config_data = json.load(f)

                self.analysis_mode = config_data.get('analysis_mode', 'rule_based')
                self.ai_config = config_data.get('ai_config', {'enabled': False})
                self.rule_weight = config_data.get('rule_weight', 0.7)
                self.ai_weight = config_data.get('ai_weight', 0.3)
        except Exception as e:
            print(f"⚠ 加载配置失败: {e}")

    def get_prompt_template(self) -> str:
        """获取AI分析提示词模板"""
        return """
你是专业的电视剧剪辑师，专注于法律悬疑剧的精彩片段识别。

请评估以下对话片段：
"{text}"

评估维度：
1. 主线剧情推进度（法案调查、证据揭露、法庭辩论）
2. 戏剧冲突强度（情感爆发、观点对立、真相反转）  
3. 角色关系发展（父女情、法律职业操守、正义追求）
4. 信息密度（关键线索、重要证词、案件突破）
5. 观众吸引力（悬念制造、情感共鸣、剧情张力）

请给出0-10分的综合评分，只返回数字：
"""

# 全局配置实例
config = AnalysisConfig()