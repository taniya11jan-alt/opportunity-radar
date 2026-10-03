def calculate_match_score(student_skills: str, opportunity_skills: str) -> float:
    # Convert comma-separated strings into clean sets of lowercase skills
    student_set = set(skill.strip().lower() for skill in student_skills.split(","))
    opportunity_set = set(skill.strip().lower() for skill in opportunity_skills.split(","))

    if not opportunity_set:
        return 0.0

    # Count how many opportunity skills the student actually has
    overlap = student_set.intersection(opportunity_set)

    # Score = fraction of the opportunity's required skills that the student has
    score = len(overlap) / len(opportunity_set)
    return round(score, 2)