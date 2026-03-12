#!/usr/bin/env python3
"""
Layer 1: Experiment Operator

自动实验执行器 - 只读假设文档，运行实验，输出结果，不修改核心
"""

import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

class ExperimentOperator:
    """Layer 1: 只负责执行，不决策"""
    
    def __init__(self, base_path: str = "/home/admin/atlas-hec-v2.1-repo/socs_universe_search"):
        self.base = Path(base_path)
        self.hypothesis_path = self.base / "experiments"
        self.output_path = self.base / "research_ops" / "outputs"
        self.output_path.mkdir(parents=True, exist_ok=True)
        
    def read_hypothesis(self, name: str) -> dict:
        """读取假设文档 (只读)"""
        status_file = self.base / "hypothesis_tree" / "status_tracker.json"
        with open(status_file) as f:
            tracker = json.load(f)
        return tracker["hypotheses"].get(name, {})
    
    def check_sandbox(self) -> bool:
        """验证沙箱边界"""
        # 确保不会修改核心文件
        protected = [
            self.base / "src" / "universe_runner.rs",
            self.base / "src" / "consciousness_index.rs",
        ]
        for p in protected:
            if not p.exists():
                print(f"⚠️  Protected file missing: {p}")
                return False
        return True
    
    def run_experiment(self, hypothesis: str, gate: str, config: dict = None) -> dict:
        """
        运行实验脚本
        
        允许执行:
        - research_ops/ 下的脚本
        - experiments/run_*_gate*.py
        
        禁止:
        - 修改 src/ 下的任何文件
        - 修改已确认的 HYPOTHESIS_*.md
        """
        
        # 构建命令
        if hypothesis == "O1_OctopusLike":
            if gate == "Gate_2":
                script = self.hypothesis_path / "run_hypothesis_o1_gate2.py"
            else:
                script = self.hypothesis_path / f"run_hypothesis_o1_{gate.lower()}.py"
        elif hypothesis == "OQS_OctoQueenSwarm":
            if gate == "Gate_1_5":
                script = self.output_path / "run_oqs_gate1_5.py"  # 待生成
            else:
                script = self.hypothesis_path / f"run_oqs_{gate.lower()}.py"
        else:
            raise ValueError(f"Unknown hypothesis: {hypothesis}")
        
        if not script.exists():
            return {
                "status": "SCRIPT_NOT_FOUND",
                "script": str(script),
                "message": "Need to generate correction script first"
            }
        
        # 执行实验（沙箱内）
        print(f"🔬 Running: {script.name}")
        result = subprocess.run(
            [sys.executable, str(script)],
            capture_output=True,
            text=True,
            timeout=300
        )
        
        # 解析结果
        output = result.stdout
        
        # 提取关键指标（从输出中解析）
        metrics = self._parse_metrics(output)
        
        # 判断 PASS/PARTIAL/FAIL
        verdict = self._determine_verdict(hypothesis, gate, metrics)
        
        return {
            "timestamp": datetime.now().isoformat(),
            "hypothesis": hypothesis,
            "gate": gate,
            "script": str(script),
            "exit_code": result.returncode,
            "verdict": verdict,
            "metrics": metrics,
            "raw_output": output[-2000:] if len(output) > 2000 else output,  # 截断
        }
    
    def _parse_metrics(self, output: str) -> dict:
        """从输出中提取指标"""
        metrics = {}
        
        # 简单的行解析
        for line in output.split('\n'):
            if 'CWCI' in line and ':' in line:
                try:
                    value = float(line.split(':')[-1].strip().split()[0])
                    metrics['cwci'] = value
                except:
                    pass
            if 'retention' in line.lower():
                try:
                    value = float(line.split('=')[-1].strip().replace('%', ''))
                    metrics['retention'] = value / 100 if value > 1 else value
                except:
                    pass
        
        return metrics
    
    def _determine_verdict(self, hypothesis: str, gate: str, metrics: dict) -> str:
        """根据指标判断结果"""
        
        if hypothesis == "O1_OctopusLike" and gate == "Gate_2":
            # Gate 2: retention > 0.85, CWCI maintained
            retention = metrics.get('retention', 0)
            if retention > 0.90:
                return "PASSED"
            elif retention > 0.85:
                return "PARTIAL"
            else:
                return "FAILED"
        
        elif hypothesis == "OQS_OctoQueenSwarm" and gate == "Gate_1_5":
            # Gate 1.5: Should reach comparable level to Ant
            cwci = metrics.get('cwci', 0)
            if cwci > 0.25:  # Ant was ~0.31
                return "PASSED"
            elif cwci > 0.20:
                return "PARTIAL"
            else:
                return "FAILED"
        
        return "UNKNOWN"
    
    def update_status_tracker(self, result: dict) -> None:
        """更新 Layer 2 状态追踪器"""
        tracker_path = self.base / "hypothesis_tree" / "status_tracker.json"
        
        with open(tracker_path) as f:
            tracker = json.load(f)
        
        hyp_key = result['hypothesis']
        gate_key = result['gate'].replace('_', '_')
        
        if hyp_key in tracker["hypotheses"]:
            tracker["hypotheses"][hyp_key]["gates"][gate_key] = {
                "status": result['verdict'],
                "date": result['timestamp'][:10],
                "metrics": result['metrics'],
                "auto_executed": True
            }
            tracker["last_updated"] = result['timestamp']
        
        with open(tracker_path, 'w') as f:
            json.dump(tracker, f, indent=2)
        
        print(f"✅ Status tracker updated: {hyp_key} {gate_key} = {result['verdict']}")
    
    def generate_report(self, result: dict) -> str:
        """生成实验报告"""
        report_path = self.output_path / f"{result['hypothesis']}_{result['gate']}_{datetime.now():%Y%m%d_%H%M%S}.md"
        
        report = f"""# Experiment Report: {result['hypothesis']} {result['gate']}

**Timestamp**: {result['timestamp']}  
**Verdict**: {result['verdict']}  
**Auto-Executed**: Yes

## Metrics

```json
{json.dumps(result['metrics'], indent=2)}
```

## Raw Output (truncated)

```
{result['raw_output'][:1000]}
```

## Next Actions

Based on verdict **{result['verdict']}**:

"""
        
        if result['verdict'] == "PASSED":
            report += "- [ ] Proceed to next Gate\n- [ ] Update hypothesis_tree/status_tracker.json\n"
        elif result['verdict'] == "PARTIAL":
            report += "- [ ] Layer 3: Failure-Mode Triage\n- [ ] Generate minimal correction proposal\n"
        else:
            report += "- [ ] Layer 3: First Failure Mode Analysis\n- [ ] Layer 4: Architecture Edit Proposal (if structural)\n"
        
        report_path.write_text(report)
        print(f"📝 Report saved: {report_path}")
        
        return str(report_path)
    
    def run(self, hypothesis: str, gate: str):
        """主执行流程"""
        print(f"\n{'='*60}")
        print(f"Layer 1 Experiment Operator")
        print(f"{'='*60}")
        
        # 1. 验证沙箱
        if not self.check_sandbox():
            print("❌ Sandbox check failed")
            return
        
        # 2. 读取假设 (只读)
        hyp_data = self.read_hypothesis(hypothesis)
        print(f"\n📋 Hypothesis: {hyp_data.get('name', hypothesis)}")
        print(f"   Current status: {hyp_data.get('status', 'UNKNOWN')}")
        
        # 3. 运行实验
        result = self.run_experiment(hypothesis, gate)
        print(f"\n🔍 Verdict: {result['verdict']}")
        print(f"   Metrics: {result['metrics']}")
        
        # 4. 更新状态 (Layer 2)
        self.update_status_tracker(result)
        
        # 5. 生成报告
        report_path = self.generate_report(result)
        
        # 6. 如果 PARTIAL/FAILED，触发 Layer 3
        if result['verdict'] in ["PARTIAL", "FAILED"]:
            print(f"\n⚠️  Triggering Layer 3 Failure-Mode Triage...")
            print(f"   See: failure_triage/{hypothesis}_{gate}_diagnosis.md")
        
        return result


def main():
    """命令行入口"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Layer 1: Experiment Operator")
    parser.add_argument("hypothesis", choices=["O1_OctopusLike", "OQS_OctoQueenSwarm"])
    parser.add_argument("gate", help="e.g., Gate_2, Gate_1_5")
    
    args = parser.parse_args()
    
    operator = ExperimentOperator()
    result = operator.run(args.hypothesis, args.gate)
    
    # 返回码
    if result['verdict'] == "PASSED":
        sys.exit(0)
    elif result['verdict'] == "PARTIAL":
        sys.exit(1)  # 需要 Layer 3 诊断
    else:
        sys.exit(2)  # 需要 Layer 3/4 介入


if __name__ == "__main__":
    main()
