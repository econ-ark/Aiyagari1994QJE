#!/usr/bin/env python3
"""
Performance Benchmarking Suite for Aiyagari (1994) Model Implementation

This script provides comprehensive performance benchmarks for the computational
implementation of the Aiyagari (1994) model, measuring execution times,
memory usage, and convergence characteristics across different parameter sets.
"""

import time
import psutil
import json
import sys
import os
from datetime import datetime
from pathlib import Path
import subprocess
import tempfile
import platform

class AiyagariBenchmark:
    """Benchmark suite for Aiyagari model performance testing."""
    
    def __init__(self):
        self.results = {
            'timestamp': datetime.now().isoformat(),
            'system_info': self._get_system_info(),
            'benchmarks': {}
        }
        
    def _get_system_info(self):
        """Collect system information for benchmark context."""
        return {
            'platform': platform.platform(),
            'processor': platform.processor(),
            'python_version': platform.python_version(),
            'cpu_count': psutil.cpu_count(),
            'memory_total_gb': round(psutil.virtual_memory().total / (1024**3), 2),
            'architecture': platform.architecture()[0]
        }
    
    def _monitor_process(self, process):
        """Monitor a subprocess for performance metrics."""
        start_time = time.time()
        max_memory = 0
        cpu_times = []
        
        try:
            ps_process = psutil.Process(process.pid)
            
            while process.poll() is None:
                try:
                    # Memory usage
                    memory_info = ps_process.memory_info()
                    max_memory = max(max_memory, memory_info.rss)
                    
                    # CPU usage
                    cpu_percent = ps_process.cpu_percent()
                    cpu_times.append(cpu_percent)
                    
                    time.sleep(0.1)  # Sample every 100ms
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    break
                    
        except psutil.NoSuchProcess:
            pass
            
        end_time = time.time()
        
        return {
            'execution_time': end_time - start_time,
            'max_memory_mb': round(max_memory / (1024**2), 2),
            'avg_cpu_percent': round(sum(cpu_times) / len(cpu_times), 2) if cpu_times else 0,
            'return_code': process.returncode
        }
    
    def benchmark_baseline(self):
        """Benchmark the baseline (quick) reproduction."""
        print("🏃 Running baseline benchmark...")
        
        if not os.path.exists('reproduce_min.sh'):
            return {'error': 'reproduce_min.sh not found'}
            
        try:
            process = subprocess.Popen(
                ['bash', 'reproduce_min.sh'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            metrics = self._monitor_process(process)
            stdout, stderr = process.communicate()
            
            metrics.update({
                'test_type': 'baseline',
                'description': 'Single parameter combination (σ=0.2, ρ=0.6, μ=1)',
                'stdout_lines': len(stdout.splitlines()),
                'stderr_lines': len(stderr.splitlines()),
                'success': process.returncode == 0
            })
            
            return metrics
            
        except Exception as e:
            return {'error': str(e)}
    
    def benchmark_docker_build(self):
        """Benchmark Docker image build time."""
        print("🐳 Running Docker build benchmark...")
        
        if not os.path.exists('Dockerfile'):
            return {'error': 'Dockerfile not found'}
            
        try:
            # Clean any existing test images
            subprocess.run(['docker', 'rmi', 'aiyagari-benchmark:test'], 
                         capture_output=True, check=False)
            
            process = subprocess.Popen(
                ['docker', 'build', '-t', 'aiyagari-benchmark:test', '.'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            metrics = self._monitor_process(process)
            stdout, stderr = process.communicate()
            
            # Get image size
            image_size = 0
            try:
                result = subprocess.run(
                    ['docker', 'images', 'aiyagari-benchmark:test', '--format', '{{.Size}}'],
                    capture_output=True, text=True, check=True
                )
                image_size = result.stdout.strip()
            except subprocess.CalledProcessError:
                pass
            
            metrics.update({
                'test_type': 'docker_build',
                'description': 'Docker image build time and resource usage',
                'image_size': image_size,
                'success': process.returncode == 0
            })
            
            # Cleanup
            subprocess.run(['docker', 'rmi', 'aiyagari-benchmark:test'], 
                         capture_output=True, check=False)
            
            return metrics
            
        except Exception as e:
            return {'error': str(e)}
    
    def benchmark_environment_setup(self):
        """Benchmark conda environment creation time."""
        print("🐍 Running environment setup benchmark...")
        
        if not os.path.exists('binder/environment.yml'):
            return {'error': 'binder/environment.yml not found'}
            
        try:
            # Create temporary environment name
            temp_env = f"aiyagari-benchmark-{int(time.time())}"
            
            process = subprocess.Popen(
                ['mamba', 'env', 'create', '-n', temp_env, '-f', 'binder/environment.yml'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            metrics = self._monitor_process(process)
            stdout, stderr = process.communicate()
            
            # Cleanup
            subprocess.run(['mamba', 'env', 'remove', '-n', temp_env, '-y'], 
                         capture_output=True, check=False)
            
            metrics.update({
                'test_type': 'environment_setup',
                'description': 'Conda environment creation from environment.yml',
                'success': process.returncode == 0
            })
            
            return metrics
            
        except Exception as e:
            return {'error': str(e)}
    
    def run_all_benchmarks(self):
        """Run all available benchmarks."""
        benchmarks = [
            ('baseline', self.benchmark_baseline),
            ('environment_setup', self.benchmark_environment_setup),
            ('docker_build', self.benchmark_docker_build),
        ]
        
        print(f"🚀 Starting Aiyagari Model Benchmark Suite")
        print(f"📊 System: {self.results['system_info']['platform']}")
        print(f"💾 Memory: {self.results['system_info']['memory_total_gb']} GB")
        print(f"🔧 CPUs: {self.results['system_info']['cpu_count']}")
        print("=" * 60)
        
        for name, benchmark_func in benchmarks:
            try:
                result = benchmark_func()
                self.results['benchmarks'][name] = result
                
                if 'error' in result:
                    print(f"❌ {name}: {result['error']}")
                else:
                    success_icon = "✅" if result.get('success', False) else "❌"
                    exec_time = result.get('execution_time', 0)
                    memory = result.get('max_memory_mb', 0)
                    print(f"{success_icon} {name}: {exec_time:.1f}s, {memory:.1f}MB")
                    
            except Exception as e:
                self.results['benchmarks'][name] = {'error': str(e)}
                print(f"💥 {name}: Exception - {str(e)}")
        
        return self.results
    
    def save_results(self, filename=None):
        """Save benchmark results to JSON file."""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"benchmark_results_{timestamp}.json"
            
        with open(filename, 'w') as f:
            json.dump(self.results, f, indent=2)
            
        print(f"📁 Results saved to: {filename}")
        return filename
    
    def print_summary(self):
        """Print a summary of benchmark results."""
        print("\n" + "=" * 60)
        print("📈 BENCHMARK SUMMARY")
        print("=" * 60)
        
        total_time = 0
        successful_tests = 0
        failed_tests = 0
        
        for name, result in self.results['benchmarks'].items():
            if 'error' in result:
                print(f"❌ {name:20} FAILED: {result['error']}")
                failed_tests += 1
            else:
                exec_time = result.get('execution_time', 0)
                memory = result.get('max_memory_mb', 0)
                success = result.get('success', False)
                
                status = "PASSED" if success else "FAILED"
                icon = "✅" if success else "❌"
                
                print(f"{icon} {name:20} {status:8} {exec_time:6.1f}s {memory:8.1f}MB")
                
                if success:
                    successful_tests += 1
                    total_time += exec_time
                else:
                    failed_tests += 1
        
        print("-" * 60)
        print(f"📊 Total successful tests: {successful_tests}")
        print(f"💥 Total failed tests: {failed_tests}")
        print(f"⏱️  Total execution time: {total_time:.1f}s")
        print(f"🖥️  System: {self.results['system_info']['platform']}")


def main():
    """Main benchmark execution function."""
    benchmark = AiyagariBenchmark()
    
    try:
        # Run all benchmarks
        benchmark.run_all_benchmarks()
        
        # Save results
        results_file = benchmark.save_results()
        
        # Print summary
        benchmark.print_summary()
        
        print(f"\n🎯 Benchmark complete! Results saved to {results_file}")
        
    except KeyboardInterrupt:
        print("\n⚠️  Benchmark interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Benchmark failed with error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main() 