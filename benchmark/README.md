# Project Euler Benchmarking Tool

Standardized benchmarking for Project Euler solutions across multiple languages.

## Usage

```bash
# Run all benchmarks
uv run benchmark.py

# Filter by language and/or problem
uv run benchmark.py -l python

uv run benchmark.py -p 0
```

## Output files:

- **benchmark_results.db**
- **results.csv**
- **BENCHMARKS.md**

## Strategy

- 5 warmup runs to prime caches
- 20 timed runs with `perf_counter()`
- Tracks min/avg/max/stdev
- Database only updates if new min is faster 