
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
旁白生成配置
"""

# 旁白模板配置
NARRATION_TEMPLATES = {
    'legal': {
        'intro': "法庭激辩即将开始",
        'explanation': "关键法律争议焦点",
        'highlight': "真相即将大白",
        'tip': "精彩辩论不容错过"
    },
    'crime': {
        'intro': "案件调查关键时刻", 
        'explanation': "重要线索即将揭露",
        'highlight': "真相呼之欲出",
        'tip': "破案关键就在眼前"
    },
    'romance': {
        'intro': "情感高潮即将上演",
        'explanation': "感人至深的情感表达", 
        'highlight': "最动人的时刻",
        'tip': "爱情的力量感动人心"
    },
    'family': {
        'intro': "温馨家庭时光",
        'explanation': "亲情的温暖力量",
        'highlight': "最感人的亲情时刻", 
        'tip': "家的温暖触动心灵"
    },
    'general': {
        'intro': "精彩剧情即将上演",
        'explanation': "重要情节发展",
        'highlight': "不容错过的精彩",
        'tip': "剧情高潮值得期待"
    }
}

# 字幕样式配置
SUBTITLE_STYLES = {
    'title': {
        'fontsize': 28,
        'fontcolor': 'white',
        'position': 'top',  # top, middle, bottom
        'duration': 3,
        'box_color': 'black@0.8',
        'border_width': 4
    },
    'explanation': {
        'fontsize': 20,
        'fontcolor': 'yellow', 
        'position': 'bottom',
        'duration': 5,
        'box_color': 'black@0.7',
        'border_width': 3
    },
    'highlight': {
        'fontsize': 18,
        'fontcolor': 'lightblue',
        'position': 'bottom',
        'duration': 3,
        'box_color': 'black@0.6', 
        'border_width': 3
    },
    'tip': {
        'fontsize': 16,
        'fontcolor': 'red',
        'position': 'top_left',
        'duration': 3,
        'box_color': 'black@0.6',
        'border_width': 2
    }
}

# 时间配置
TIMING_CONFIG = {
    'title_start': 0,
    'title_duration': 3,
    'explanation_start': 3,
    'explanation_duration': 5,
    'highlight_start_from_end': 3,  # 从结尾倒数3秒开始
    'tip_start': 1,
    'tip_duration': 3
}

# 关键词匹配规则
KEYWORD_MAPPING = {
    'legal_keywords': ['法官', '检察官', '律师', '法庭', '审判', '证据', '案件', '起诉', '辩护', '判决', '申诉', '听证会'],
    'crime_keywords': ['警察', '犯罪', '嫌疑人', '调查', '破案', '线索', '凶手', '案发', '侦探', '刑侦', '追踪', '逮捕'],
    'romance_keywords': ['爱情', '喜欢', '心动', '表白', '约会', '分手', '复合', '结婚', '情侣', '恋人', '暗恋', '初恋'],
    'family_keywords': ['家庭', '父母', '孩子', '兄弟', '姐妹', '亲情', '家人', '团聚', '离别', '成长', '教育', '代沟']
}
