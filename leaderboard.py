import sqlite3 as db


def show_leaderboard(conn):
    cur = conn.cursor()

    # Determine correct column name dynamically
    cur.execute("PRAGMA table_info(leaderboard)")
    cols = [r[1] for r in cur.fetchall()]
    total_col = "total_questions" if "total_questions" in cols else "limit"

    cur.execute(
        f"SELECT name, score, [{total_col}], scoreper FROM leaderboard ORDER BY scoreper DESC, score DESC"
    )
    results = cur.fetchall()
    cur.close()

    if not results:
        print("\n[!] Leaderboard is empty. Be the first to play!")
        return

    print("\n" + "=" * 20 + " LEADERBOARD " + "=" * 20)
    print(f"{'Rank':<6}{'Name':<20}{'Score':<10}{'Total':<10}{'Percentage':<12}")
    print("-" * 58)
    for rank, (name, score, total_q, scoreper) in enumerate(results, 1):
        print(f"{rank:<6}{name:<20}{score:<10}{total_q:<10}{scoreper:<10.2f}%")
    print("-" * 58)
