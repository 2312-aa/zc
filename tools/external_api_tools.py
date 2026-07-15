"""外部心理服务API工具（可选扩展）"""
from langchain_core.tools import tool


@tool
def search_mental_health_resources(query: str, resource_type: str = "all") -> str:
    """搜索心理健康相关的外部资源信息。

    Args:
        query: 搜索关键词
        resource_type: 资源类型 (article/hotline/hospital/app/all)
    """
    # 预置的资源数据库（可替换为真实 API 调用）
    resources_db = {
        "article": [
            {"title": "认识焦虑：症状与应对", "url": "https://example.com/anxiety", "tags": ["焦虑", "认知"]},
            {"title": "抑郁自测与自助指南", "url": "https://example.com/depression", "tags": ["抑郁", "自助"]},
            {"title": "正念冥想入门", "url": "https://example.com/mindfulness", "tags": ["正念", "冥想"]},
            {"title": "CBT认知行为疗法基础", "url": "https://example.com/cbt", "tags": ["CBT", "认知"]},
            {"title": "睡眠卫生指南", "url": "https://example.com/sleep", "tags": ["失眠", "睡眠"]},
        ],
        "hotline": [
            {"name": "全国24小时心理危机干预热线", "phone": "400-161-9995"},
            {"name": "北京心理危机研究与干预中心", "phone": "010-82951332"},
            {"name": "生命热线", "phone": "400-821-1215"},
            {"name": "希望24热线", "phone": "400-161-9995"},
        ],
        "hospital": [
            {"name": "北京安定医院", "city": "北京", "specialty": "精神科"},
            {"name": "上海市精神卫生中心", "city": "上海", "specialty": "精神科"},
            {"name": "华西医院心理卫生中心", "city": "成都", "specialty": "心理科"},
            {"name": "中山大学附属第三医院精神科", "city": "广州", "specialty": "精神科"},
        ],
        "app": [
            {"name": "壹心理", "desc": "专业心理健康平台"},
            {"name": "简单心理", "desc": "在线心理咨询"},
            {"name": "潮汐", "desc": "冥想与白噪音"},
            {"name": "心潮", "desc": "情绪管理与正念"},
        ],
    }

    results = []

    if resource_type in ("all", "article"):
        for a in resources_db["article"]:
            if any(tag in query for tag in a["tags"]) or query in a["title"]:
                results.append(f"[文章] {a['title']} - {a['url']}")

    if resource_type in ("all", "hotline"):
        for h in resources_db["hotline"]:
            results.append(f"[热线] {h['name']}: {h['phone']}")

    if resource_type in ("all", "hospital"):
        for h in resources_db["hospital"]:
            if query in h["city"] or query in h["specialty"] or resource_type == "all":
                results.append(f"[医院] {h['name']}({h['city']}) - {h['specialty']}")

    if resource_type in ("all", "app"):
        for a in resources_db["app"]:
            results.append(f"[App] {a['name']} - {a['desc']}")

    if not results:
        return f"未找到与 '{query}' 相关的资源。建议尝试更具体的关键词。"

    return "\n".join(results)
