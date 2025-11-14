from typing import Dict, Any


def evaluate(answers: Dict[str, str], answer_key: Dict[str, str]) -> Dict[str, Any]:
    evaluation: Dict[str, Any] = {}
    total_marks = 0
    correct_count = 0
    wrong_count = 0

    for qno, student_ans in answers.items():
        correct_ans = answer_key.get(qno)
        is_correct = student_ans == correct_ans
        marks = 1 if is_correct else 0

        if is_correct:
            correct_count += 1
            total_marks += 1
        else:
            wrong_count += 1

        evaluation[qno] = {
            "student_answer": student_ans,
            "correct_answer": correct_ans,
            "is_correct": is_correct,
            "marks": marks,
        }

    evaluation["summary"] = {
        "total_questions": len(answer_key),
        "correct": correct_count,
        "wrong": wrong_count,
        "total_marks": total_marks,
    }

    return evaluation

