from ai_agents.resume_tailor.tool import tailor_resume

def test_tailoring():
    resume = "Skilled data analyst with Python and SQL experience."
    jd = "Seeking a data analyst with strong Python, Tableau, and data visualization skills."
    result = tailor_resume(resume, jd)
    print(result)
