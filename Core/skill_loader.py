"""
金锤子 (GenForge) - Skill 热加载器
参照 JZXZBOT：Markdown 文件即技能，无需编译，运行时动态加载
"""
import logging
from pathlib import Path

logger = logging.getLogger("GenForge.SkillLoader")

# Skills 目录（Settings/Skills/）
_SKILLS_DIR = Path(__file__).parent.parent / "Settings" / "Skills"


class SkillLoader:
    """
    Skill 热加载器
    
    目录结构（参照 JZXZBOT）：
    Settings/Skills/
    ├── Architect/
    │   └── SKILL.md
    ├── CADDeveloper/
    │   └── SKILL.md
    └── ResidentialCadGenerator/
        ├── SKILL.md
        └── references/
            ├── layer-axis.md
            └── layer-wall.md
    """

    def load_all(self) -> dict:
        """
        扫描 Settings/Skills/ 下所有子目录的 SKILL.md
        返回 {技能名: system_prompt_str} 字典
        """
        skills = {}

        if not _SKILLS_DIR.exists():
            logger.warning(f"⚠️  Skills 目录不存在: {_SKILLS_DIR}，使用空技能")
            return skills

        for skill_dir in sorted(_SKILLS_DIR.iterdir()):
            if not skill_dir.is_dir():
                continue

            skill_md = skill_dir / "SKILL.md"
            if not skill_md.exists():
                continue

            skill_name = skill_dir.name
            content = self._load_skill_with_references(skill_dir, skill_md)
            skills[skill_name] = content
            logger.info(f"📖 已加载技能: {skill_name} ({len(content)} 字符)")

        return skills

    def _load_skill_with_references(self, skill_dir: Path, skill_md: Path) -> str:
        """加载 SKILL.md 及其 references/ 目录下的所有文档，合并为完整 system prompt"""
        parts = []

        # 主 SKILL.md
        try:
            parts.append(skill_md.read_text(encoding="utf-8"))
        except Exception as e:
            logger.error(f"读取 {skill_md} 失败: {e}")

        # references/ 子文档
        refs_dir = skill_dir / "references"
        if refs_dir.exists():
            for ref_file in sorted(refs_dir.glob("*.md")):
                try:
                    ref_content = ref_file.read_text(encoding="utf-8")
                    parts.append(f"\n\n---\n## 参考文档: {ref_file.name}\n{ref_content}")
                    logger.debug(f"  + 参考文档: {ref_file.name}")
                except Exception as e:
                    logger.error(f"读取参考文档 {ref_file} 失败: {e}")

        return "\n".join(parts)

    def reload(self) -> dict:
        """热重载所有技能（无需重启程序）"""
        logger.info("🔄 重新加载所有技能...")
        return self.load_all()
