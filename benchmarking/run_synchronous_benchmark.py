#!/usr/bin/env python3
"""
Simple benchmark runner for A* on synchronous environments.
Run this to get timing results on all 10 synchronous environments.

Usage:
    python run_synchronous_benchmark.py

This will test all synchronous environments and report which ones exceed 5 seconds.
"""

import subprocess
import sys
import os
import time

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def run_synchronous_benchmark():
    """Run A* on all synchronous environments and measure timing."""
    
    synchronous_envs = [
        "synchronous/0_cheese_sandwich",
        "synchronous/1_lettuce_sandwich", 
        "synchronous/2_lettuce_tomato_sandwich",
        "synchronous/3_burger",
        "synchronous/4_cheeseburger",
        "synchronous/5_double_cheeseburger",
        "synchronous/6_lettuce_tomato_cheeseburger",
        "synchronous/7_two_lettuce_chicken_sandwich",
        "synchronous/8_two_lettuce_tomato_burger",
        "synchronous/9_onion_cheese_burger_and_lettuce_tomato_chicken_sandwich"
    ]
    
    print("A* SYNCHRONOUS ENVIRONMENTS BENCHMARK")
    print("=" * 50)
    print("Target: Find optimal plan within 5 seconds per environment")
    print(f"Testing {len(synchronous_envs)} environments...")
    print()
    
    results = []
    total_time = 0
    
    for i, env_name in enumerate(synchronous_envs):
        env_short = env_name.split('/')[-1]
        print(f"[{i+1:2d}/{len(synchronous_envs)}] Testing {env_short}")
        
        start_time = time.time()
        
        try:
            # Run single environment test - need to run from main robotouille directory
            robotouille_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            cmd = [
                'python', 'main.py',
                f'environment_name={env_name}',
                'agent_name=astar',
                'game.render_mode=rgb_array',
                'game.max_steps=300'
            ]
            
            result = subprocess.run(cmd, 
                                  capture_output=True, 
                                  text=True, 
                                  timeout=10,  # 10 second hard timeout
                                  cwd=robotouille_dir)
            
            exec_time = time.time() - start_time
            
            # Check if successful (look for "Optimal Plan" in output)
            success = "Optimal Plan:" in result.stdout
            
            if success:
                # Extract plan length
                lines = result.stdout.split('\n')
                plan_length = None
                for line in lines:
                    if line.startswith("Length:"):
                        plan_length = int(line.split(":")[1].strip())
                        break
                
                results.append({
                    'env': env_short,
                    'success': True,
                    'time': exec_time,
                    'steps': plan_length,
                    'meets_target': exec_time <= 5.0
                })
                
                status = "✓" if exec_time <= 5.0 else "⚠"
                print(f"    {status} {exec_time:.2f}s - {plan_length} steps")
                
            else:
                results.append({
                    'env': env_short,
                    'success': False,
                    'time': exec_time,
                    'steps': None,
                    'meets_target': False
                })
                print(f"    ✗ FAILED ({exec_time:.2f}s)")
                
            total_time += exec_time
            
        except subprocess.TimeoutExpired:
            results.append({
                'env': env_short,
                'success': False,
                'time': 10.0,
                'steps': None,
                'meets_target': False
            })
            total_time += 10.0
            print(f"    ✗ TIMEOUT (>10s)")
            
        except Exception as e:
            print(f"    ✗ ERROR: {e}")
    
    # Summary
    print("\n" + "=" * 50)
    print("BENCHMARK RESULTS")
    print("=" * 50)
    
    successful = [r for r in results if r['success']]
    if successful:
        success_rate = len(successful) / len(results)
        avg_time = sum(r['time'] for r in successful) / len(successful)
        target_met = sum(1 for r in successful if r['meets_target']) / len(successful)
        
        print(f"Success Rate:    {success_rate:.1%} ({len(successful)}/{len(results)})")
        print(f"Average Time:    {avg_time:.2f}s")
        print(f"Target Met Rate: {target_met:.1%}")
        print(f"Total Time:      {total_time:.1f}s")
        
        print(f"\nDetailed Results:")
        for r in results:
            if r['success']:
                target = "✓" if r['meets_target'] else "⚠"
                print(f"  {r['env']:35} ✓ {r['steps']:3d} steps  {r['time']:6.2f}s {target}")
            else:
                print(f"  {r['env']:35} ✗ FAILED")
        
        # Identify problem environments
        slow_envs = [r for r in successful if not r['meets_target']]
        if slow_envs:
            print(f"\nEnvironments exceeding 5s target:")
            for r in slow_envs:
                print(f"  {r['env']:35} {r['time']:6.2f}s")
        else:
            print(f"\n✓ ALL ENVIRONMENTS MEET 5-SECOND TARGET!")
            
    else:
        print("❌ No environments completed successfully")

if __name__ == "__main__":
    run_synchronous_benchmark()