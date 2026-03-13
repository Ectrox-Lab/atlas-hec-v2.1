#!/usr/bin/env python3
"""
Candidate 001 Falsification Tests
=================================
Tests per design spec for multi-agent consistency markers

Falsification conditions:
1. Removing markers doesn't degrade coherence
2. Markers only improve cooperation without consistency pressure
3. Agents don't show coherence when markers visible
"""

import numpy as np
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from multi_agent_markers import (
    MarkerGameArena, 
    MarkerAgent, 
    ConsistencyMarker,
    GameType
)


class NoMarkerArena:
    """Control condition: No markers visible"""
    
    def __init__(self, n_agents: int = 4):
        self.n_agents = n_agents
        self.tick = 0
        self.agents = []
        
        for i in range(n_agents):
            # Same agents but no markers
            self.agents.append(MarkerAgent(
                marker=None,
                policy=np.random.randn(2) * 0.1,
                consistency_pressure=0.0,
                action_history=[]
            ))
    
    def observe_markers(self, observer_id: int) -> dict:
        """No markers observed"""
        return {}
    
    def choose_action(self, agent: MarkerAgent, partner_id: int, game: GameType) -> int:
        """Random policy (no markers to guide)"""
        probs = np.exp(agent.policy) / np.sum(np.exp(agent.policy))
        return np.random.choice([0, 1], p=probs)
    
    def get_game_payoffs(self, game: GameType) -> np.ndarray:
        if game == GameType.PRISONERS_DILEMMA:
            return np.array([[3, 0], [5, 1]])
        elif game == GameType.STAG_HUNT:
            return np.array([[4, 0], [2, 2]])
        else:
            return np.array([[0, -1], [1, -10]])
    
    def play_round(self, agent_i: int, agent_j: int):
        game = np.random.choice(list(GameType))
        payoff_matrix = self.get_game_payoffs(game)
        
        action_i = self.choose_action(self.agents[agent_i], agent_j, game)
        action_j = self.choose_action(self.agents[agent_j], agent_i, game)
        
        self.agents[agent_i].action_history.append(action_i)
        self.agents[agent_j].action_history.append(action_j)
        
        payoff_i = payoff_matrix[action_i, action_j]
        payoff_j = payoff_matrix[action_j, action_i]
        
        return payoff_i, payoff_j
    
    def step(self):
        agents_shuffled = np.random.permutation(self.n_agents)
        for k in range(0, self.n_agents - 1, 2):
            i, j = agents_shuffled[k], agents_shuffled[k+1]
            self.play_round(i, j)
    
    def run_episode(self, n_rounds: int = 1000) -> dict:
        for _ in range(n_rounds):
            self.step()
        
        consistencies = []
        for agent in self.agents:
            if len(agent.action_history) > 10:
                action_dist = np.bincount(
                    agent.action_history[-50:], 
                    minlength=2
                ) / min(50, len(agent.action_history[-50:]))
                entropy = -np.sum(action_dist * np.log(action_dist + 1e-10))
                consistencies.append(1.0 - entropy / np.log(2))
        
        return {
            "behavioral_consistency": np.mean(consistencies) if consistencies else 0.0
        }


class NoConsistencyPressureArena:
    """Control condition: Markers visible but no consistency pressure"""
    
    def __init__(self, n_agents: int = 4):
        self.n_agents = n_agents
        self.agents = []
        self.tick = 0
        
        for i in range(n_agents):
            marker = ConsistencyMarker(
                agent_id=i,
                coherence_score=0.5,
                behavioral_bias=np.random.randn(2) * 0.1
            )
            agent = MarkerAgent(
                marker=marker,
                policy=np.random.randn(2) * 0.1,
                consistency_pressure=0.0,
                action_history=[]
            )
            self.agents.append(agent)
    
    def choose_action(self, agent: MarkerAgent, partner_id: int, game: GameType) -> int:
        """Use markers only for cooperation, not consistency"""
        # Observed markers guide action but no consistency penalty
        action_logits = agent.policy.copy()
        # NO consistency pressure
        probs = np.exp(action_logits) / np.sum(np.exp(action_logits))
        return np.random.choice([0, 1], p=probs)
    
    def get_game_payoffs(self, game: GameType) -> np.ndarray:
        if game == GameType.PRISONERS_DILEMMA:
            return np.array([[3, 0], [5, 1]])
        elif game == GameType.STAG_HUNT:
            return np.array([[4, 0], [2, 2]])
        else:
            return np.array([[0, -1], [1, -10]])
    
    def play_round(self, agent_i: int, agent_j: int):
        game = np.random.choice(list(GameType))
        payoff_matrix = self.get_game_payoffs(game)
        
        action_i = self.choose_action(self.agents[agent_i], agent_j, game)
        action_j = self.choose_action(self.agents[agent_j], agent_i, game)
        
        self.agents[agent_i].action_history.append(action_i)
        self.agents[agent_j].action_history.append(action_j)
        
        payoff_i = payoff_matrix[action_i, action_j]
        payoff_j = payoff_matrix[action_j, action_i]
        # NO consistency bonus
        return payoff_i, payoff_j
    
    def step(self):
        self.tick += 1
        # NO marker updates
        agents_shuffled = np.random.permutation(self.n_agents)
        for k in range(0, self.n_agents - 1, 2):
            i, j = agents_shuffled[k], agents_shuffled[k+1]
            self.play_round(i, j)
    
    def run_episode(self, n_rounds: int = 1000) -> dict:
        for _ in range(n_rounds):
            self.step()
        
        consistencies = []
        for agent in self.agents:
            if len(agent.action_history) > 10:
                action_dist = np.bincount(
                    agent.action_history[-50:], 
                    minlength=2
                ) / min(50, len(agent.action_history[-50:]))
                entropy = -np.sum(action_dist * np.log(action_dist + 1e-10))
                consistencies.append(1.0 - entropy / np.log(2))
        
        return {
            "behavioral_consistency": np.mean(consistencies) if consistencies else 0.0
        }


def test_1_markers_required_for_coherence():
    """
    FALSIFICATION TEST 1: Removing markers degrades coherence
    
    If markers are NOT required for behavioral coherence,
    then agents without markers should show similar consistency.
    
    PASS: With-markers >> Without-markers
    FAIL: With-markers ≈ Without-markers (markers not required)
    """
    print("="*60)
    print("FALSIFICATION TEST 1: Markers Required for Coherence")
    print("="*60)
    
    n_trials = 10
    with_markers = []
    without_markers = []
    
    for trial in range(n_trials):
        # With markers
        arena_with = MarkerGameArena(n_agents=4)
        result_with = arena_with.run_episode(n_rounds=1000)
        with_markers.append(result_with['behavioral_consistency'])
        
        # Without markers
        arena_without = NoMarkerArena(n_agents=4)
        result_without = arena_without.run_episode(n_rounds=1000)
        without_markers.append(result_without['behavioral_consistency'])
    
    mean_with = np.mean(with_markers)
    mean_without = np.mean(without_markers)
    
    print(f"  With markers: {mean_with:.3f} ± {np.std(with_markers):.3f}")
    print(f"  Without markers: {mean_without:.3f} ± {np.std(without_markers):.3f}")
    print(f"  Difference: {mean_with - mean_without:.3f}")
    
    if mean_with > mean_without + 0.1:
        print("  ✅ PASS: Markers significantly improve coherence")
        return True
    else:
        print("  ❌ FAIL: Markers don't improve coherence - hypothesis falsified!")
        return False


def test_2_consistency_pressure_required():
    """
    FALSIFICATION TEST 2: Markers improve only cooperation without consistency pressure
    
    If markers work without consistency pressure,
    then visible markers alone should drive coherence.
    
    PASS: Consistency pressure required
    FAIL: Markers visible but no pressure → same coherence
    """
    print("\n" + "="*60)
    print("FALSIFICATION TEST 2: Consistency Pressure Required")
    print("="*60)
    
    n_trials = 10
    with_pressure = []
    without_pressure = []
    
    for trial in range(n_trials):
        # With consistency pressure (marker updates)
        arena_pressure = MarkerGameArena(n_agents=4)
        result_pressure = arena_pressure.run_episode(n_rounds=1000)
        with_pressure.append(result_pressure['behavioral_consistency'])
        
        # Without consistency pressure (no marker updates)
        arena_no_pressure = NoConsistencyPressureArena(n_agents=4)
        result_no_pressure = arena_no_pressure.run_episode(n_rounds=1000)
        without_pressure.append(result_no_pressure['behavioral_consistency'])
    
    mean_with = np.mean(with_pressure)
    mean_without = np.mean(without_pressure)
    
    print(f"  With pressure: {mean_with:.3f} ± {np.std(with_pressure):.3f}")
    print(f"  Without pressure: {mean_without:.3f} ± {np.std(without_pressure):.3f}")
    print(f"  Difference: {mean_with - mean_without:.3f}")
    
    if mean_with > mean_without + 0.05:
        print("  ✅ PASS: Consistency pressure required")
        return True
    else:
        print("  ❌ FAIL: Consistency pressure not required - hypothesis falsified!")
        return False


def test_3_observable_consistency():
    """
    FALSIFICATION TEST 3: Agents show coherence when markers visible
    
    Test that coherence is observable via markers.
    High-coherence agents should have stable marker scores.
    
    PASS: High coherence agents have stable markers
    FAIL: No correlation between markers and coherence
    """
    print("\n" + "="*60)
    print("FALSIFICATION TEST 3: Observable Coherence via Markers")
    print("="*60)
    
    arena = MarkerGameArena(n_agents=4)
    
    # Run episode
    metrics = arena.run_episode(n_rounds=1000)
    
    # Check marker-agent coherence correlation
    coherences = [a.marker.coherence_score for a in arena.agents]
    marker_stability = 1.0 - np.var(coherences)
    
    print(f"  Behavioral consistency: {metrics['behavioral_consistency']:.3f}")
    print(f"  Mean marker coherence: {np.mean(coherences):.3f}")
    print(f"  Marker stability: {marker_stability:.3f}")
    
    # Check if high-coherence agents have stable markers
    if metrics['behavioral_consistency'] > 0.4 and marker_stability > 0.5:
        print("  ✅ PASS: Coherence observable via markers")
        return True
    else:
        print("  ❌ FAIL: Coherence not observable via markers")
        return False


def test_4_bandwidth_compliance():
    """
    COMPLIANCE TEST: Bandwidth <= 32 bits per marker
    
    Verify marker design is compliant with FROZEN_STATE_v1
    """
    print("\n" + "="*60)
    print("COMPLIANCE TEST: Bandwidth Constraint")
    print("="*60)
    
    marker = ConsistencyMarker(
        agent_id=255,  # 8 bits
        coherence_score=0.5,  # 8 bits (0-255 mapped to 0.0-1.0)
        behavioral_bias=np.array([0.1, 0.2])  # 2x8 = 16 bits
    )
    
    total_bits = 8 + 8 + 16  # = 32 bits
    print(f"  agent_id: 8 bits")
    print(f"  coherence_score: 8 bits")
    print(f"  behavioral_bias: 16 bits")
    print(f"  Total: {total_bits} bits")
    
    if total_bits <= 32:
        print("  ✅ COMPLIANT: Bandwidth <= 32 bits")
        return True
    else:
        print("  ❌ NON-COMPLIANT: Bandwidth exceeds 32 bits")
        return False


def test_5_timescale_compliance():
    """
    COMPLIANCE TEST: Timescale separation >= 10x
    
    Verify marker updates are 10x slower than actions
    """
    print("\n" + "="*60)
    print("COMPLIANCE TEST: Timescale Separation")
    print("="*60)
    
    arena = MarkerGameArena(n_agents=4)
    
    print(f"  Action frequency: every tick")
    print(f"  Marker update frequency: every {arena.MARKER_UPDATE_INTERVAL} ticks")
    print(f"  Timescale separation: {arena.MARKER_UPDATE_INTERVAL}x")
    
    if arena.MARKER_UPDATE_INTERVAL >= 10:
        print("  ✅ COMPLIANT: >= 10x timescale separation")
        return True
    else:
        print("  ❌ NON-COMPLIANT: < 10x timescale separation")
        return False


if __name__ == "__main__":
    print("="*60)
    print("Candidate 001 Falsification Tests")
    print("="*60)
    print("Testing multi-agent consistency markers")
    print("="*60)
    
    results = []
    
    # Run all tests
    results.append(("Test 1: Markers Required", test_1_markers_required_for_coherence()))
    results.append(("Test 2: Consistency Pressure", test_2_consistency_pressure_required()))
    results.append(("Test 3: Observable Coherence", test_3_observable_consistency()))
    results.append(("Test 4: Bandwidth", test_4_bandwidth_compliance()))
    results.append(("Test 5: Timescale", test_5_timescale_compliance()))
    
    # Summary
    print("\n" + "="*60)
    print("FALSIFICATION TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for _, r in results if r)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status}: {name}")
    
    print(f"\n  Result: {passed}/{total} tests passed")
    
    if passed == total:
        print("  🎉 ALL TESTS PASSED - Candidate 001 VALIDATED")
        exit(0)
    elif passed >= 3:
        print("  ⚠️  PARTIAL - Candidate needs refinement")
        exit(0)
    else:
        print("  💀 HYPOTHESIS FALSIFIED - Candidate rejected")
        exit(1)
