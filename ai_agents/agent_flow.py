from ai_agents.resume_tailor.tool import tailor_resume
from ai_agents.jd_matcher.tool import match_resume_to_jd
from ai_agents.q_generator.tool import generate_interview_questions
from ai_agents.feedback_agent.tool import evaluate_answer
from ai_agents.resume_parser.tool import parse_resume

class CareerAgentFlow:

    @staticmethod
    def full_pipeline(resume: str, jd: str):
        return {
            "tailored_resume": tailor_resume(resume, jd),
            "match_report": match_resume_to_jd(resume, jd),
            "questions": generate_interview_questions(resume, jd),
        }

    @staticmethod
    def evaluate_answer_flow(answer: str, jd: str):
        return evaluate_answer(answer, jd)

    @staticmethod
    def extract_from_resume(resume: str):
        return parse_resume(resume)
