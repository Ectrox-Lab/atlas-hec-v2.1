#!/usr/bin/env python3
"""
Task 1: Gate Operator
自动跑实验，输出 PASS/PARTIAL/FAIL
"""

import argparse
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

class GateOperator:
    def __init__(self, base_path: str = "/home/admin/atlas-hec-v2.1-repo/socs_universe_search"):
        self.base = Path(base_path)
        self.results_dir = Path(__file__).parent.parent / "results"
        self.results_dir.mkdir(exist_ok=True)
        
    def run_gate(self, hypothesis: str, gate: str) -> dict:
        """执行指定 Gate 实验"""
        
        # 映射到实验脚本
        script_map = {
            ("O1", "Gate_1"): "run_hypothesis_o1_gate1.py",
            ("O1", "Gate_2"): "run_hypothesis_o1_gate2.py",
            ("OQS", "Gate_1"): "run_oqs_gate1.py",
            # Gate_1_5 是修正后的版本，需要生成
        }
        
        key = (hypothesis, gate)
        if key not in script_map:
            return {
                "status": "SCRIPT_NOT_FOUND",
                "message": f"No script for {hypothesis} {gate}"
            }
        
        script = self.base / "experiments" / script_map[key]
        
        # 执行实验
        print(f"🔬 Running: {script.name}")
        result = subprocess.run(
            [sys.executable, str(script)],
            capture_output=True,
            text=True,
            timeout=300,
            cwd=self.base
        )
        
        # 解析结果
        output = result.stdout
        verdict = self._extract_verdict(output)
        metrics = self._extract_metrics(output)
        
        # 构建结果
        result_data = {
            "timestamp": datetime.now().isoformat(),
            "hypothesis": hypothesis,
            "gate": gate,
            "script": str(script),
            "exit_code": result.returncode,
            "verdict": verdict,
            "metrics": metrics,
            "raw_output": output[-1500:] if len(output) > 1500 else output
        }
        
        # 保存结果
        result_file = self.results_dir / f"{hypothesis}_{gate}_{datetime.now():%Y%m%d_%H%M%S}.json"
        with open(result_file, 'w') as f:
            json.dump(result_data, f, indent=2)
        
        print(f"✅ Result saved: {result_file}")
        print(f"📊 Verdict: {verdict}")
        
        return result_data
    
    def _extract_verdict(self, output: str) -> str:
        """从输出中提取判决"""
        if "Gate 2 = PASS" in output or "Gate 1 = PASS" in output:
            return "PASSED"
        elif "Gate 2 = PARTIAL" in output or "Gate 1 = PARTIAL" in output:
            return "PARTIAL"
        elif "Gate 2 = FAIL" in output or "Gate 1 = FAIL" in output:
            return "FAILED"
        return "UNKNOWN"
    
    def _extract_metrics(self, output: str) -> dict:
        """从输出中提取指标"""
        metrics = {}
        
        # 解析 CWCI
        for line in output.split('\n'):
            if 'CWCI' in line and ('0.' in line or '1.' in line):
                try:
                    # 尝试提取数字
                    parts = line.split()
                    for p in parts:
                        if p.replace('.', '').replace('-', '').isdigit():
                            metrics['cwci'] = float(p)
                            break
                except:
                    pass
        
        # 解析 retention
        if 'retention' in output.lower():
            try:
                for line in output.split('\n'):
                    if 'retention' in line.lower() and '=' in line:
                        val = line.split('=')[-1].strip().replace('%', '')
                        metrics['retention'] = float(val)
            except:
                pass
        
        return metrics

def main():
    parser = argparse.ArgumentParser(description="Gate Operator")
    parser.add_argument("--hypothesis", choices=["O1", "OQS"], required=True)
    parser.add_argument("--gate", choices=["Gate_1", "Gate_2", "Gate_1_5"], required=True)
    
    args = parser.parse_args()
    
    operator = GateOperator()
    result = operator.run_gate(args.hypothesis, args.gate)
    
    # 返回码
    if result['verdict'] == "PASSED":
        sys.exit(0)
    elif result['verdict'] == "PARTIAL":
        sys.exit(1)
    else:
        sys.exit(2)

if __name__ == "__main__":
    main()
