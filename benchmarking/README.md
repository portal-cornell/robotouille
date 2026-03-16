# A* Benchmarking Scripts

This directory contains benchmarking scripts for the A* agent performance analysis.

## Scripts

### 1. `run_synchronous_benchmark.py`
**Purpose**: Benchmark A* on all 10 synchronous environments  
**What it does**: Runs A* on each synchronous environment and measures total execution time  
**Usage**: 
```bash
cd /share/portal/gg387/gonzalo_robotouille_new/robotouille/benchmarking
python run_synchronous_benchmark.py
```
**Output**: Success rate, timing per environment, identifies which environments exceed 5s target

### 2. `profile_astar_performance.py` 
**Purpose**: Detailed performance profiling to identify bottlenecks  
**What it does**: Monkey-patches A* to measure time spent in deepcopy, heuristic, etc.  
**Usage**:
```bash
cd /share/portal/gg387/gonzalo_robotouille_new/robotouille/benchmarking
python profile_astar_performance.py                    # Quick test on 3 environments
python profile_astar_performance.py 0_cheese_sandwich  # Single environment
```
**Output**: Breakdown showing % time spent in deepcopy, heuristic computation, etc.

## Quick Start

To benchmark A* on synchronous environments:
```bash
cd /share/portal/gg387/gonzalo_robotouille_new/robotouille/benchmarking
python run_synchronous_benchmark.py
```

To profile performance bottlenecks:
```bash  
cd /share/portal/gg387/gonzalo_robotouille_new/robotouille/benchmarking
python profile_astar_performance.py
```

## Performance Target
- Find optimal plan within 5 seconds per environment
- Focus on synchronous environments (10 total)
- Identify bottlenecks preventing this target