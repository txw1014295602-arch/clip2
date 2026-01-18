
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
AI分析测试脚本 - 验证AI功能
"""

from ai_analyzer import ai_analyzer

def test_ai_analysis():
    """测试AI分析功能"""
    print("🧪 测试AI分析功能")
    print("=" * 50)
    
    if not ai_analyzer.enabled:
        print("❌ AI分析未启用，请先配置API")
        print("运行: python quick_ai_setup.py")
        return
    
    # 测试对话片段
    test_dialogues = [
        "我要为四二八案申请重审，这个证据证明当年的判决有误。",
        "张园在学校里被霸凌，这与628旧案有直接关系。",
        "法官，我反对！这个证据是非法获得的。",
        "爸爸，我相信你是清白的，我会为你证明的。"
    ]
    
    print(f"📊 测试 {len(test_dialogues)} 个对话片段:")
    print("-" * 30)
    
    for i, dialogue in enumerate(test_dialogues, 1):
        print(f"\n🎬 测试片段 {i}: {dialogue[:30]}...")
        
        try:
            result = ai_analyzer.analyze_dialogue_segment(dialogue, "法律悬疑剧背景")
            
            print(f"✅ 评分: {result.get('score', 0)}/10")
            print(f"🎭 分析: {result.get('reasoning', 'N/A')[:100]}...")
            
            if 'key_elements' in result:
                print(f"🔑 关键要素: {', '.join(result['key_elements'][:3])}")
            
        except Exception as e:
            print(f"❌ 分析失败: {e}")
    
    print("\n" + "=" * 50)
    print("✅ AI分析测试完成")

if __name__ == "__main__":
    test_ai_analysis()
