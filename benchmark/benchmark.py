import argparse
import csv
import datetime
import sqlite3
import statistics
import subprocess
import time
from pathlib import Path

RUNS = 20
WARMUP = 5

BENCHMARK_DIR = Path(__file__).parent
DB_FILE = BENCHMARK_DIR / "benchmark_results.db"
CSV_FILE = BENCHMARK_DIR / "results.csv"
MD_FILE = BENCHMARK_DIR / "BENCHMARKS.md"

LANGUAGE_CONFIGS = {
    "python": {
        "dir": "python",
        "command_prefix": ["uv", "run", "python"],
        "file_pattern": "main.py",
    },
    # "rust": {
    #     "dir": "rust",
    #     "command_prefix": ["cargo", "run", "--release", "--manifest-path"],
    #     "file_pattern": "Cargo.toml",
    # },
}


def init_database():
    """Initialize SQLite database for storing benchmark results."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS benchmarks (
            problem INTEGER,
            language TEXT,
            min_time REAL,
            avg_time REAL,
            max_time REAL,
            stdev REAL,
            timestamp TEXT,
            answer TEXT,
            PRIMARY KEY (problem, language)
        )
    """
    )


def discover_problems(language, project_root):
    """Auto-discover problems from directory structure."""
    config = LANGUAGE_CONFIGS.get(language)
    if not config:
        return []

    lang_dir = project_root / config["dir"]
    if not lang_dir.exists():
        return []

    problems = []
    for problem_dir in sorted(lang_dir.glob("problem-*")):
        if problem_dir.is_dir():
            problem_num = problem_dir.name.split("-")[1]
            try:
                problem_num = int(problem_num)
                main_file = problem_dir / config["file_pattern"]
                if main_file.exists():
                    problems.append(
                        {
                            "number": problem_num,
                            "path": problem_dir,
                        }
                    )
            except ValueError:
                continue

    return problems


def run_command(cmd):
    """Execute a command and capture output."""
    result = subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        check=True,
        text=True,
    )
    return result.stdout.strip()


def benchmark(cmd, runs, warmup):
    """Run benchmark with warmup and collect statistics."""
    # Warm-up runs (not measured)
    for _ in range(warmup):
        run_command(cmd)

    times = []
    answer = None
    for _ in range(runs):
        start = time.perf_counter()
        output = run_command(cmd)
        end = time.perf_counter()
        times.append(end - start)

        # Capture answer from first run and validate consistency
        if answer is None:
            answer = output
        elif answer != output:
            raise ValueError(
                f"Inconsistent output detected: expected '{answer}', got '{output}'"
            )

    return {
        "avg": statistics.mean(times),
        "min": min(times),
        "max": max(times),
        "stdev": statistics.stdev(times) if len(times) > 1 else 0.0,
        "answer": answer,
    }


def update_database(conn, problem, language, stats):
    """Update database only if the new time is faster than the existing record."""
    cursor = conn.cursor()

    # Check for any existing answer for this problem (across all languages)
    cursor.execute(
        "SELECT answer FROM benchmarks WHERE problem = ? AND answer IS NOT NULL LIMIT 1",
        (problem,),
    )
    existing_answer = cursor.fetchone()

    # Validate answer consistency across languages
    if existing_answer is not None:
        if stats["answer"] != existing_answer[0]:
            raise ValueError(
                f"Answer mismatch for problem {problem}: "
                f"expected '{existing_answer[0]}', got '{stats['answer']}'"
            )

    # Check if record exists for this specific language
    cursor.execute(
        "SELECT min_time FROM benchmarks WHERE problem = ? AND language = ?",
        (problem, language),
    )
    existing = cursor.fetchone()
    timestamp = datetime.datetime.now().isoformat()

    if existing is None:
        cursor.execute(
            """
            INSERT INTO benchmarks (problem, language, min_time, avg_time, max_time, stdev, timestamp, answer)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                problem,
                language,
                stats["min"],
                stats["avg"],
                stats["max"],
                stats["stdev"],
                timestamp,
                stats["answer"],
            ),
        )
        conn.commit()
        return True, "new"
    elif stats["min"] < existing[0]:
        cursor.execute(
            """
            UPDATE benchmarks
            SET min_time = ?, avg_time = ?, max_time = ?, stdev = ?, timestamp = ?, answer = ?
            WHERE problem = ? AND language = ?
        """,
            (
                stats["min"],
                stats["avg"],
                stats["max"],
                stats["stdev"],
                timestamp,
                stats["answer"],
                problem,
                language,
            ),
        )
        conn.commit()
        return True, "improved"
    else:
        return False, "slower"


def get_all_results(conn):
    """Retrieve all benchmark results from database."""
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT problem, language, min_time, avg_time, max_time, stdev, timestamp
        FROM benchmarks
        ORDER BY problem, language
    """
    )
    return cursor.fetchall()


def export_csv(results):
    """Export results to CSV file."""
    with open(CSV_FILE, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(
            [
                "Problem",
                "Language",
                "Min (s)",
                "Avg (s)",
                "Max (s)",
                "StdDev (s)",
                "Last Updated",
            ]
        )
        for row in results:
            timestamp = datetime.datetime.fromisoformat(row[6]).strftime(
                "%Y-%m-%d %H:%M:%S"
            )
            writer.writerow(
                [
                    row[0],  # problem
                    row[1],  # language
                    f"{row[2]:.6f}",  # min_time
                    f"{row[3]:.6f}",  # avg_time
                    f"{row[4]:.6f}",  # max_time
                    f"{row[5]:.6f}",  # stdev
                    timestamp,
                ]
            )


def export_markdown(results):
    """Export results to Markdown file for GitHub viewing."""
    with open(MD_FILE, "w") as f:
        f.write("# Project Euler Benchmark Results\n\n")
        f.write(
            f"Last updated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        )
        f.write(
            "| Problem | Language | Min (s) | Avg (s) | Max (s) | StdDev (s) | Last Updated |\n"
        )
        f.write(
            "|---------|----------|---------|---------|---------|------------|---------------|\n"
        )

        for row in results:
            timestamp = datetime.datetime.fromisoformat(row[6]).strftime("%Y-%m-%d")
            f.write(
                f"| {row[0]} | {row[1]} | {row[2]:.6f} | {row[3]:.6f} | {row[4]:.6f} | {row[5]:.6f} | {timestamp} |\n"
            )


def main():
    parser = argparse.ArgumentParser(description="Benchmark Project Euler solutions")
    parser.add_argument(
        "-l",
        "--language",
        help="Filter by language (e.g., python, rust, go)",
        choices=list(LANGUAGE_CONFIGS.keys()),
    )
    parser.add_argument("-p", "--problem", type=int, help="Filter by problem number")

    args = parser.parse_args()
    conn = init_database()

    # Determine which languages to benchmark
    languages = [args.language] if args.language else list(LANGUAGE_CONFIGS.keys())
    total_benchmarks = 0
    improved_count = 0
    new_count = 0
    project_root = Path(__file__).parent.parent

    for language in languages:
        problems = discover_problems(language, project_root)

        if args.problem is not None:
            problems = [p for p in problems if p["number"] == args.problem]

        if not problems:
            print(
                f"No problems found for {language}"
                + (f" #{args.problem}" if args.problem else "")
            )
            continue

        config = LANGUAGE_CONFIGS[language]

        for problem in problems:
            total_benchmarks += 1
            print(
                f"Running Euler #{problem['number']} ({language})...",
                end=" ",
                flush=True,
            )

            if language == "python":
                cmd = config["command_prefix"] + [
                    str(problem["path"] / config["file_pattern"])
                ]
            else:
                cmd = config["command_prefix"] + [str(problem["path"])]

            try:
                stats = benchmark(cmd, RUNS, WARMUP)
                _, status = update_database(conn, problem["number"], language, stats)

                if status == "new":
                    new_count += 1
                    print(f"NEW: {stats['min']:.6f}s")
                elif status == "improved":
                    improved_count += 1
                    print(f"IMPROVED: {stats['min']:.6f}s")
                else:
                    print(f"  {stats['min']:.6f}s (not faster)")
            except Exception as e:
                print(f"FAILED: {e}")

    results = get_all_results(conn)
    export_csv(results)
    export_markdown(results)

    conn.close()

    print(f"\n{'='*60}")
    print(f"Benchmarked {total_benchmarks} problem(s)")
    print(f"New records: {new_count}")
    print(f"Improved records: {improved_count}")
    print(f"\nResults exported to:")
    print(f"  - {CSV_FILE}")
    print(f"  - {MD_FILE}")
    print(f"  - {DB_FILE}")


if __name__ == "__main__":
    main()
