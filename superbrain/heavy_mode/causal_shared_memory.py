#!/usr/bin/env python3
"""
CAUSAL SHARED MEMORY - Phase D Implementation
跨實例因果圖共享機制

目標：讓多個 Heavy Mode 實例共享因果知識，避免重複探索
"""

import numpy as np
import json
import time
from typing import Dict, List, Optional, Set
from dataclasses import dataclass, asdict
from pathlib import Path
import threading


@dataclass
class SharedCausalEvent:
    """可在進程間共享的因果事件"""
    event_id: str
    timestamp: float
    worker_id: int
    config_sig: str
    drift_score: float
    confidence: float
    
    def to_dict(self) -> Dict:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, d: Dict) -> 'SharedCausalEvent':
        return cls(**d)


class CausalSharedMemory:
    """
    跨 Heavy Mode 實例的共享因果記憶
    
    使用文件系統作為共享存儲（簡單但有效）
    未來可升級為 Redis/共享內存
    """
    
    def __init__(self, shared_dir: str = "/tmp/akashic_shared"):
        self.shared_dir = Path(shared_dir)
        self.shared_dir.mkdir(exist_ok=True)
        
        # 事件存儲
        self.events_file = self.shared_dir / "causal_events.jsonl"
        self.lock_file = self.shared_dir / "causal.lock"
        
        # 本地緩存
        self.local_cache: Dict[str, SharedCausalEvent] = {}
        self.last_sync = 0
        
        # 統計
        self.stats = {
            "events_shared": 0,
            "events_received": 0,
            "sync_operations": 0
        }
        
        print(f"[CAUSAL-SHARED] Initialized at {shared_dir}")
    
    def _acquire_lock(self) -> bool:
        """簡單的文件鎖（非阻塞）"""
        try:
            # 使用 PID 文件作為鎖
            if self.lock_file.exists():
                pid = int(self.lock_file.read_text())
                # 檢查進程是否存在
                try:
                    import os
                    os.kill(pid, 0)
                    return False  # 進程存在，鎖被持有
                except ProcessLookupError:
                    pass  # 進程不存在，可以獲取鎖
            
            self.lock_file.write_text(str(time.time()))
            return True
        except Exception:
            return False
    
    def _release_lock(self):
        """釋放鎖"""
        try:
            if self.lock_file.exists():
                self.lock_file.unlink()
        except Exception:
            pass
    
    def publish_event(self, event: SharedCausalEvent):
        """發布事件到共享存儲"""
        if not self._acquire_lock():
            return False
        
        try:
            with open(self.events_file, 'a') as f:
                f.write(json.dumps(event.to_dict()) + '\n')
            
            self.stats["events_shared"] += 1
            return True
        except Exception as e:
            print(f"[CAUSAL-SHARED] Publish error: {e}")
            return False
        finally:
            self._release_lock()
    
    def sync_events(self) -> List[SharedCausalEvent]:
        """同步所有新事件"""
        if not self.events_file.exists():
            return []
        
        if not self._acquire_lock():
            return []
        
        try:
            events = []
            with open(self.events_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        data = json.loads(line)
                        event = SharedCausalEvent.from_dict(data)
                        
                        # 只獲取新事件
                        if event.event_id not in self.local_cache:
                            self.local_cache[event.event_id] = event
                            events.append(event)
                            self.stats["events_received"] += 1
                    except json.JSONDecodeError:
                        continue
            
            self.stats["sync_operations"] += 1
            self.last_sync = time.time()
            return events
        except Exception as e:
            print(f"[CAUSAL-SHARED] Sync error: {e}")
            return []
        finally:
            self._release_lock()
    
    def get_config_knowledge(self, config_sig: str) -> Optional[Dict]:
        """獲取特定配置的共享知識"""
        self.sync_events()
        
        relevant_events = [
            e for e in self.local_cache.values()
            if e.config_sig == config_sig
        ]
        
        if not relevant_events:
            return None
        
        # 聚合知識
        drift_scores = [e.drift_score for e in relevant_events]
        confidences = [e.confidence for e in relevant_events]
        
        return {
            "config_sig": config_sig,
            "avg_drift": float(np.mean(drift_scores)),
            "std_drift": float(np.std(drift_scores)),
            "avg_confidence": float(np.mean(confidences)),
            "n_observations": len(relevant_events),
            "sources": list(set(e.worker_id for e in relevant_events))
        }
    
    def get_exploration_recommendations(self, current_worker: int) -> List[Dict]:
        """
        基於全局知識生成探索建議
        
        建議高不確定性或高風險的配置
        """
        self.sync_events()
        
        # 按配置分組
        config_groups: Dict[str, List[SharedCausalEvent]] = {}
        for event in self.local_cache.values():
            if event.config_sig not in config_groups:
                config_groups[event.config_sig] = []
            config_groups[event.config_sig].append(event)
        
        recommendations = []
        
        for config_sig, events in config_groups.items():
            n_obs = len(events)
            avg_conf = np.mean([e.confidence for e in events])
            avg_drift = np.mean([e.drift_score for e in events])
            
            # 低置信度 = 需要更多探索
            uncertainty = 1.0 - avg_conf
            
            # 高 drift = 危險區域
            risk = avg_drift if avg_drift > 0.5 else 0.0
            
            # 綜合評分
            priority = uncertainty * 0.6 + risk * 0.4
            
            recommendations.append({
                "config_sig": config_sig,
                "priority": float(priority),
                "uncertainty": float(uncertainty),
                "risk": float(risk),
                "n_observations": n_obs,
                "recommendation": "explore" if uncertainty > 0.5 else "verify" if risk > 0.5 else "skip"
            })
        
        # 按優先級排序
        recommendations.sort(key=lambda x: x["priority"], reverse=True)
        return recommendations[:10]  # Top 10
    
    def get_stats(self) -> Dict:
        """獲取統計信息"""
        return {
            **self.stats,
            "cached_events": len(self.local_cache),
            "shared_dir": str(self.shared_dir)
        }


# ============================================================================
# 測試
# ============================================================================

if __name__ == "__main__":
    print("CAUSAL SHARED MEMORY - Phase D Test")
    print("=" * 50)
    
    # 創建兩個共享內存實例（模擬兩個 worker）
    shared = CausalSharedMemory("/tmp/test_causal_shared")
    
    # Worker 1 發布事件
    event1 = SharedCausalEvent(
        event_id="test_1",
        timestamp=time.time(),
        worker_id=1,
        config_sig="P2T3M3D1",
        drift_score=0.35,
        confidence=0.8
    )
    shared.publish_event(event1)
    
    event2 = SharedCausalEvent(
        event_id="test_2",
        timestamp=time.time(),
        worker_id=1,
        config_sig="P2T3M3D1",
        drift_score=0.38,
        confidence=0.75
    )
    shared.publish_event(event2)
    
    # Worker 2 同步並查詢
    print("\nSyncing events...")
    new_events = shared.sync_events()
    print(f"Received {len(new_events)} new events")
    
    # 查詢配置知識
    print("\nQuerying config knowledge...")
    knowledge = shared.get_config_knowledge("P2T3M3D1")
    if knowledge:
        print(f"Config: {knowledge['config_sig']}")
        print(f"  Avg drift: {knowledge['avg_drift']:.3f}")
        print(f"  Avg confidence: {knowledge['avg_confidence']:.3f}")
        print(f"  Observations: {knowledge['n_observations']}")
    
    # 獲取推薦
    print("\nExploration recommendations:")
    recs = shared.get_exploration_recommendations(current_worker=2)
    for i, rec in enumerate(recs, 1):
        print(f"  {i}. {rec['config_sig']}: priority={rec['priority']:.2f}, "
              f"action={rec['recommendation']}")
    
    # 統計
    print("\nStats:")
    print(f"  {shared.get_stats()}")
    
    print("\n✓ Phase D Shared Memory Test Complete")
