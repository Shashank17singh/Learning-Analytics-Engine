import csv
import os
import sqlite3 as db


def loadQuestions(conn):
    """Load questions from a CSV file using Python's standard csv module."""
    cur = conn.cursor()
    filename = input("Enter CSV file path [default: assessment_engine.csv]: ").strip()
    if not filename:
        filename = "assessment_engine.csv"

    # If file not found in current directory, check in the script's directory
    if not os.path.exists(filename):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        alt_path = os.path.join(script_dir, filename)
        if os.path.exists(alt_path):
            filename = alt_path
        else:
            print(f"[!] File not found: '{filename}'")
            return

    try:
        with open(filename, "r", encoding="utf-8-sig", errors="replace") as fp:
            reader = csv.reader(fp)
            rows_to_insert = []
            header_skipped = False

            for row in reader:
                if not row or not any(field.strip() for field in row):
                    continue

                # Detect and skip header row
                if not header_skipped:
                    header_skipped = True
                    first_col = row[0].strip().lower()
                    if (
                        "qno" in first_col
                        or "question" in first_col
                        or "ques" in first_col
                    ):
                        continue

                # Parse row based on column format
                if len(row) >= 9 and row[0].strip().isdigit():
                    ques = row[1].strip()
                    a = row[2].strip()
                    b = row[3].strip()
                    c = row[4].strip()
                    d = row[5].strip()
                    correct = row[6].strip()
                    review = row[7].strip() if len(row) > 7 else ""
                    explanation = row[8].strip() if len(row) > 8 else ""
                elif len(row) >= 8:
                    ques = row[0].strip()
                    a = row[1].strip()
                    b = row[2].strip()
                    c = row[3].strip()
                    d = row[4].strip()
                    correct = row[5].strip()
                    review = row[6].strip() if len(row) > 6 else ""
                    explanation = row[7].strip() if len(row) > 7 else ""
                else:
                    continue

                # Normalize correct answer: if text matches an option, map to option letter
                correct_lower = correct.lower()
                if correct_lower in ["a", "b", "c", "d"]:
                    mapped_correct = correct_lower
                elif correct_lower == a.lower():
                    mapped_correct = "a"
                elif correct_lower == b.lower():
                    mapped_correct = "b"
                elif correct_lower == c.lower():
                    mapped_correct = "c"
                elif correct_lower == d.lower():
                    mapped_correct = "d"
                else:
                    mapped_correct = correct

                rows_to_insert.append(
                    (ques, a, b, c, d, mapped_correct, review, explanation)
                )

            if not rows_to_insert:
                print("[!] No valid question rows found in the CSV file.")
                return

            cur.executemany(
                "INSERT INTO questions(ques, a, b, c, d, correct, review, explanation) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                rows_to_insert,
            )
            conn.commit()
            print(
                f"[+] Successfully loaded {len(rows_to_insert)} questions from '{filename}'."
            )

    except Exception as e:
        print(f"[!] Error loading CSV file: {e}")
    finally:
        cur.close()


def addQuestion(conn):
    """Manually add a single question with validation and parameterized query."""
    cur = conn.cursor()
    print("\n--- Add New Question ---")
    ques = input("Enter question: ").strip()
    if not ques:
        print("[!] Question cannot be empty.")
        cur.close()
        return

    a = input("Enter Option A: ").strip()
    b = input("Enter Option B: ").strip()
    c = input("Enter Option C: ").strip()
    d = input("Enter Option D: ").strip()
    correct = input("Enter correct answer (a/b/c/d or text): ").strip().lower()
    review = input("Enter review (optional): ").strip()
    explanation = input("Enter explanation (optional): ").strip()

    # Map text to letter if applicable
    if correct in ["a", "b", "c", "d"]:
        pass
    elif correct == a.lower():
        correct = "a"
    elif correct == b.lower():
        correct = "b"
    elif correct == c.lower():
        correct = "c"
    elif correct == d.lower():
        correct = "d"

    cur.execute(
        "INSERT INTO questions(ques, a, b, c, d, correct, review, explanation) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        (ques, a, b, c, d, correct, review, explanation),
    )
    conn.commit()
    cur.close()
    print("[+] Question added successfully!")


def viewQuestions(conn):
    """Display all stored questions in the database."""
    cur = conn.cursor()
    cur.execute(
        "SELECT qno, ques, a, b, c, d, correct, review, explanation FROM questions ORDER BY qno ASC"
    )
    questions = cur.fetchall()
    cur.close()

    if not questions:
        print("\n[!] No questions found in the database.")
        return

    print(f"\n{'=' * 60}")
    print(f"Total Questions: {len(questions)}")
    print(f"{'=' * 60}")
    for qno, ques, a, b, c, d, correct, review, explanation in questions:
        print(f"\nQ{qno}: {ques}")
        print(f"  a) {a}")
        print(f"  b) {b}")
        print(f"  c) {c}")
        print(f"  d) {d}")
        print(f"  >> Correct: {correct}")
        if review:
            print(f"  >> Review: {review}")
        if explanation:
            print(f"  >> Explanation: {explanation}")
        print("-" * 60)


def updateQuestion(conn):
    """Update an existing question's details."""
    cur = conn.cursor()
    try:
        qno = int(input("\nEnter Question Number (qno) to update: ").strip())
    except ValueError:
        print("[!] Invalid question number.")
        cur.close()
        return

    cur.execute(
        "SELECT qno, ques, a, b, c, d, correct, review, explanation FROM questions WHERE qno = ?",
        (qno,),
    )
    row = cur.fetchone()
    if not row:
        print(f"[!] Question #{qno} not found.")
        cur.close()
        return

    _, old_ques, old_a, old_b, old_c, old_d, old_correct, old_review, old_explanation = (
        row
    )
    print("\n(Press Enter to keep current value)")

    new_ques = input(f"Question [{old_ques}]: ").strip() or old_ques
    new_a = input(f"Option A [{old_a}]: ").strip() or old_a
    new_b = input(f"Option B [{old_b}]: ").strip() or old_b
    new_c = input(f"Option C [{old_c}]: ").strip() or old_c
    new_d = input(f"Option D [{old_d}]: ").strip() or old_d
    new_correct = (
        input(f"Correct Answer [{old_correct}]: ").strip().lower() or old_correct
    )
    new_review = input(f"Review [{old_review}]: ").strip()
    if not new_review and old_review:
        new_review = old_review
    new_explanation = input(f"Explanation [{old_explanation}]: ").strip()
    if not new_explanation and old_explanation:
        new_explanation = old_explanation

    cur.execute(
        """UPDATE questions
           SET ques = ?, a = ?, b = ?, c = ?, d = ?, correct = ?, review = ?, explanation = ?
           WHERE qno = ?""",
        (
            new_ques,
            new_a,
            new_b,
            new_c,
            new_d,
            new_correct,
            new_review,
            new_explanation,
            qno,
        ),
    )
    conn.commit()
    cur.close()
    print(f"[+] Question #{qno} updated successfully!")


def deleteQuestion(conn):
    """Delete a specific question or all questions."""
    cur = conn.cursor()
    print("\n--- Delete Questions ---")
    print("1) Remove all questions")
    print("2) Remove specific question by ID")
    print("3) Cancel")

    try:
        ch = int(input("Enter your choice -> ").strip())
    except ValueError:
        print("[!] Invalid input.")
        cur.close()
        return

    if ch == 1:
        confirm = (
            input("Are you sure you want to delete ALL questions? (y/n): ")
            .strip()
            .lower()
        )
        if confirm == "y":
            cur.execute("DELETE FROM questions")
            conn.commit()
            print("[+] All questions removed.")
        else:
            print("Operation cancelled.")
    elif ch == 2:
        try:
            choice = int(input("Enter Question Number (qno) to delete: ").strip())
        except ValueError:
            print("[!] Invalid question number.")
            cur.close()
            return
        cur.execute("DELETE FROM questions WHERE qno = ?", (choice,))
        if cur.rowcount > 0:
            conn.commit()
            print(f"[+] Question #{choice} deleted.")
        else:
            print(f"[!] Question #{choice} not found.")
    elif ch == 3:
        print("Cancelled.")
    else:
        print("[!] Invalid choice.")

    cur.close()


# Alias for backward compatibility
delteQuestion = deleteQuestion
