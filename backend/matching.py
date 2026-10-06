from datetime import datetime

def calculate_skill_score(student_skills: str, opportunity_skills: str) -> float:
    student_set = set(skill.strip().lower() for skill in student_skills.split(","))
    opportunity_set = set(skill.strip().lower() for skill in opportunity_skills.split(","))

    if not opportunity_set:
        return 0.0

    matched = 0
    for opp_skill in opportunity_set:
        for student_skill in student_set:
            if student_skill in opp_skill or opp_skill in student_skill:
                matched += 1
                break  # count this opportunity skill only once, even if multiple student skills match it

    score = matched / len(opportunity_set)
    return round(score, 2)


def calculate_urgency_score(deadline_str: str) -> float:
    try:
        deadline = datetime.strptime(deadline_str, "%Y-%m-%d")
    except ValueError:
        return 0.0

    days_left = (deadline - datetime.now()).days

    if days_left < 0:
        return 0.0
    if days_left <= 7:
        return 1.0
    if days_left <= 30:
        return 0.6
    return 0.3


def calculate_final_score(student_skills: str, opportunity_skills: str, deadline_str: str) -> dict:
    skill_score = calculate_skill_score(student_skills, opportunity_skills)
    urgency_score = calculate_urgency_score(deadline_str)

    final_score = round((0.7 * skill_score) + (0.3 * urgency_score), 2)

    return {
        "skill_score": skill_score,
        "urgency_score": urgency_score,
        "final_score": final_score
    }