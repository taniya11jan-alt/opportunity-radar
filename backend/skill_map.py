# Maps an internship role phrase to the skills it usually needs.
SKILL_MAP = {
    "software developer": ["python", "java", "sql"],
    "software testing": ["testing", "selenium"],
    "frontend developer": ["html", "css", "javascript"],
    "backend": ["python", "sql", "api"],
    "web development": ["html", "css", "javascript"],
    "app development": ["java", "android"],
    "data analysis": ["python", "sql", "excel"],
    "data science": ["python", "machine learning", "statistics"],
    "machine learning": ["python", "machine learning"],
    "research and development": ["research", "python"],
    "vlsi": ["verilog", "digital design"],
    "autocad": ["autocad", "design"],
    "video editor": ["video editing"],
    "social media": ["social media", "content writing"],
    "business development": ["sales", "communication"],     "data scientist": ["python", "machine learning", "statistics"],
    "digital marketing": ["seo", "social media", "marketing"],
    "marketing": ["marketing", "communication"],
    "ui/ux": ["figma", "ui design", "ux"],
    "design": ["design", "figma"],
    "cad": ["autocad", "cad"],
    "electronics": ["electronics", "embedded systems"],
    "artificial intelligence": ["python", "machine learning", "ai"],
    "generative ai": ["python", "machine learning", "llm"],
    "hr": ["communication", "recruitment"],
    "research": ["research", "excel"],    "python": ["python", "programming"],
    "php": ["php", "mysql", "web development"],
    "react native": ["react native", "javascript", "android"],
    "content creation": ["content writing", "social media"],
    "graphic designer": ["design", "figma", "photoshop"],
}


def expand_skills(role_phrase):
    """Return extra skills for a role phrase, e.g. 'frontend developer' -> html, css, javascript."""
    role = role_phrase.lower()
    extra = []
    for key, skills in SKILL_MAP.items():
        if key in role:
            extra.extend(skills)
    return list(dict.fromkeys(extra))