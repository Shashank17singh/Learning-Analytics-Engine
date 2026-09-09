import random
import sqlite3 as db
import time


def play_assessment(conn):
    cur = conn.cursor()
    print("\n" + "=" * 40)
    print("           START ASSESSMENT")
    print("=" * 40)

    name = input("Enter your name: ").strip()
    if not name:
        name = "Anonymous"

    # Fetch all questions
    cur.execute(
        "SELECT qno, ques, a, b, c, d, correct, explanation FROM questions"
    )
    all_questions = cur.fetchall()

    if not all_questions:
        print("\n[!] No questions available. Please contact the administrator.")
        cur.close()
        return

    total_avail = len(all_questions)
    try:
        n_input = input(
            f"Choose number of questions to attempt (5 to {min(50, total_avail)}, default: 10): "
        ).strip()
        num_q = int(n_input) if n_input else 10
        num_q = max(1, min(num_q, total_avail))
    except ValueError:
        num_q = min(10, total_avail)

    # Randomize question selection so new unique questions appear every time
    questions = random.sample(all_questions, num_q)
    print(f"\n[+] Selected {len(questions)} randomized questions for your assessment.")

    score = 0
    total = len(questions)
    start_time = time.time()

    for i, (qno, ques, a, b, c, d, correct, explanation) in enumerate(
        questions, 1
    ):
        print(f"\nQ{i}: {ques}")
        print(f"  a) {a}")
        print(f"  b) {b}")
        print(f"  c) {c}")
        print(f"  d) {d}")

        options_map = {
            "a": str(a).strip().lower(),
            "b": str(b).strip().lower(),
            "c": str(c).strip().lower(),
            "d": str(d).strip().lower(),
        }
        correct_clean = str(correct).strip().lower()

        while True:
            ans = input("Your answer (a/b/c/d): ").strip().lower()
            if ans in ["a", "b", "c", "d"] or ans in options_map.values():
                break
            else:
                print("  [!] Please enter a valid option (a, b, c, d).")

        # Determine if answer is correct
        is_correct = False
        if ans in ["a", "b", "c", "d"]:
            if ans == correct_clean:
                is_correct = True
            elif options_map.get(ans) == correct_clean:
                is_correct = True
        elif ans == correct_clean:
            is_correct = True

        # Determine formatted display of the correct answer
        if correct_clean in ["a", "b", "c", "d"]:
            letter_texts = {"a": a, "b": b, "c": c, "d": d}
            correct_display = (
                f"{correct_clean.upper()}) {letter_texts.get(correct_clean, '')}"
            )
        else:
            rev_letter = None
            for letter, opt_text in options_map.items():
                if opt_text == correct_clean:
                    rev_letter = letter.upper()
                    break
            correct_display = f"{rev_letter}) {correct}" if rev_letter else str(correct)

        if is_correct:
            print("  [+] Correct!")
            score += 1
        else:
            print(f"  [-] Wrong! Correct answer: {correct_display}")
            if explanation and explanation.strip():
                print(f"  [Explanation] {explanation.strip()}")

    time_taken_seconds = max(1, int(time.time() - start_time))
    score_percentage = (score / total) * 100
    passed = 1 if score_percentage >= 50.0 else 0

    print("\n" + "=" * 40)
    print(f"Assessment Completed! Final Score for {name}:")
    print(f"Score: {score}/{total} ({score_percentage:.2f}%)")
    print(f"Time Taken: {time_taken_seconds} seconds")
    print(f"Status: {'PASSED [OK]' if passed else 'NEEDS IMPROVEMENT'}")
    print("=" * 40)

    # 1. Log attempt into attempts table for Data Science analytics
    cur.execute(
        """
        INSERT INTO attempts (
            student_name, score, total_questions, score_percentage,
            time_taken_seconds, attempt_date, passed
        ) VALUES (?, ?, ?, ?, ?, datetime('now'), ?)
    """,
        (name, score, total, score_percentage, time_taken_seconds, passed),
    )

    # 2. Save to leaderboard
    cur.execute("PRAGMA table_info(leaderboard)")
    cols = [r[1] for r in cur.fetchall()]
    total_col = "total_questions" if "total_questions" in cols else "limit"

    cur.execute(
        f"INSERT INTO leaderboard (name, score, [{total_col}], scoreper) VALUES (?, ?, ?, ?)",
        (name, score, total, score_percentage),
    )
    conn.commit()
    cur.close()
    print("[+] Score saved to leaderboard and logged for analytics.")
