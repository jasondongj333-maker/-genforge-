"""
金锤子 (GenForge) - 意图解析器
两层策略：
  1. 快速关键词匹配（低延迟）
  2. LLM 兜底解析（高覆盖）
"""
import re
import logging

logger = logging.getLogger("GenForge.IntentParser")

# CAD 绘图类关键词
_CAD_KEYWORDS = [
    "画", "绘", "生成", "创建", "新建", "draw", "create",
    "墙", "门", "窗", "图层", "轴网", "柱", "楼板", "楼梯",
    "wall", "door", "window", "layer", "axis", "column",
    "AutoCAD", "CAD", "cad", "建筑", "平面图", "设计",
    "标注", "尺寸", "房间", "户型",
]


class IntentParser:
    """意图解析器"""

    def parse(self, user_input: str) -> dict | None:
        """
        解析用户意图
        返回: {"type": "cad_draw", "keywords": [...]} 或 None（普通对话）
        """
        lower = user_input.lower()

        # 快速关键词匹配
        matched = [kw for kw in _CAD_KEYWORDS if kw.lower() in lower]
        if matched:
            logger.debug(f"关键词匹配命中: {matched}")
            return {
                "type": "cad_draw",
                "keywords": matched,
                "raw_input": user_input,
            }

        return None

    def extract_dimensions(self, text: str) -> dict:
        """
        从文本中提取尺寸参数（毫米优先，米自动转换）
        支持格式：3000mm / 3m / 3×4 / 宽3000 / 厚度200
        """
        params = {}

        # 带单位的数字
        mm_matches = re.findall(r'(\d+(?:\.\d+)?)\s*mm', text)
        m_matches  = re.findall(r'(\d+(?:\.\d+)?)\s*m(?!m)', text)

        if mm_matches:
            params["dimension_mm"] = [int(float(v)) for v in mm_matches]
        if m_matches:
            params["dimension_mm"] = params.get("dimension_mm", []) + \
                                     [int(float(v) * 1000) for v in m_matches]

        # 厚度 / 宽度 / 高度
        for key, patterns in {
            "thickness": [r'厚[度]?[：:＝=]?\s*(\d+)', r'thickness[：:=]?\s*(\d+)'],
            "width":     [r'宽[度]?[：:＝=]?\s*(\d+)', r'width[：:=]?\s*(\d+)'],
            "height":    [r'高[度]?[：:＝=]?\s*(\d+)', r'height[：:=]?\s*(\d+)'],
            "length":    [r'长[度]?[：:＝=]?\s*(\d+)', r'length[：:=]?\s*(\d+)'],
        }.items():
            for pattern in patterns:
                m = re.search(pattern, text, re.IGNORECASE)
                if m:
                    params[key] = int(m.group(1))
                    break

        # 尺寸格式 "3×4m" "3x4"
        size_match = re.search(r'(\d+(?:\.\d+)?)[×xX×](\d+(?:\.\d+)?)\s*(m|mm)?', text)
        if size_match:
            unit = size_match.group(3) or "m"
            factor = 1000 if unit == "m" else 1
            params["width"]  = int(float(size_match.group(1)) * factor)
            params["length"] = int(float(size_match.group(2)) * factor)

        return params
