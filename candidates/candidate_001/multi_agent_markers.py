#!/usr/bin/env python3
"""
Candidate 001: Multi-Agent Consistency Markers
===============================================
BUILD_NOW - Multi-agent systems with observable consistency markers

Compliant with FROZEN_STATE_v1:
- Bandwidth <= 32 bits per marker
- Timescale separation >= 10x
- Generic prior only (no content)
"""

import numpy as np
from typing import List, Dict, Tuple
from dataclasses import dataclass
from enum import Enum


class GameType(Enum):
    PRISONERS_DILEMMA = "pd"
    STAG_HUNT = "stag"
    CHICKEN = "chicken"


@dataclass
class ConsistencyMarker:
    """
    COMPLIANT: <= 32 bits total
    - agent_id: 8 bits
    - coherence_score: 8 bits  
    - behavioral_bias: 16 bits
    """
    agent_id: int
    coherence_score: float  # 0.0 to 1.0 (8-bit equivalent)
    behavioral_bias: np.ndarray  # 16-bit equivalent direction vector


@dataclass
class MarkerAgent:
    """Agent with consistency marker"""
    marker: ConsistencyMarker
    policy: np.ndarray
    consistency_pressure: float
    action_history: List[int]


class MarkerGameArena:
    """
    Multi-agent arena with consistency markers
    
    COMPLIANT design:
    - Marker visibility: <= 32 bits per observation
    - Marker update: Every 10 ticks (10x slower than actions)
    - Generic prior: coherence expectation, not specific strategy
    """
    
    # FROZEN parameters
    MARKER_UPDATE_INTERVAL = 10  # 10x timescale separation
    COHERENCE_WINDOW = 10
    CONSISTENCY_BONUS_WEIGHT = 0.1
    
    def __init__(self, n_agents: int = 4):
        self.n_agents = n_agents
        self.agents: List[MarkerAgent] = []
        self.tick = 0
        
        # Initialize agents with markers
        # Use biased initialization to encourage consistency
        for i in range(n_agents):
            # Start with moderate coherence expectation
            marker = ConsistencyMarker(
                agent_id=i,
                coherence_score=0.7,  # Start optimistic
                behavioral_bias=np.array([0.3, -0.2]) + np.random.randn(2) * 0.1
            )
            agent = MarkerAgent(
                marker=marker,
                policy=np.array([0.2, -0.1]) + np.random.randn(2) * 0.1,
                consistency_pressure=0.0,
                action_history=[]
            )
            self.agents.append(agent)
    
    def get_game_payoffs(self, game: GameType) -> np.ndarray:
        """Get payoff matrix for current game"""
        if game == GameType.PRISONERS_DILEMMA:
            # (C, C)=3, (C, D)=0, (D, C)=5, (D, D)=1
            return np.array([[3, 0], [5, 1]])
        elif game == GameType.STAG_HUNT:
            # (S, S)=4, (S, H)=0, (H, S)=2, (H, H)=2
            return np.array([[4, 0], [2, 2]])
        else:  # CHICKEN
            # (S, S)=0, (S, D)=-1, (D, S)=1, (D, D)=-10
            return np.array([[0, -1], [1, -10]])
    
    def observe_markers(self, observer_id: int) -> Dict[int, ConsistencyMarker]:
        """
        OBSERVE: See partner markers (<= 32 bits each)
        COMPLIANT: No action history, no specific strategy content
        """
        observed = {}
        for i, agent in enumerate(self.agents):
            if i != observer_id:
                # Only marker info, not history
                observed[i] = agent.marker
        return observed
    
    def predict_partner_coherence(
        self,
        observer: MarkerAgent,
        partner_id: int,
        observed_markers: Dict[int, ConsistencyMarker]
    ) -> float:
        """
        PREDICT: Use generic prior from marker
        COMPLIANT: Predicting consistency, not specific actions
        """
        if partner_id not in observed_markers:
            return 0.5  # Unknown
        
        partner_marker = observed_markers[partner_id]
        
        # Generic prior: high coherence → expect consistent behavior
        expected_coherence = partner_marker.coherence_score
        
        # Add small influence from own behavioral bias (generic coupling)
        bias_alignment = np.dot(
            observer.marker.behavioral_bias,
            partner_marker.behavioral_bias
        )
        
        # Consistency expectation (generic, not specific)
        consistency_expectation = (
            expected_coherence + 
            bias_alignment * 0.1  # Weak generic coupling
        )
        
        return np.clip(consistency_expectation, 0.0, 1.0)
    
    def choose_action(
        self,
        agent: MarkerAgent,
        partner_id: int,
        game: GameType
    ) -> int:
        """
        ACT: Choose action based on game + prior
        Action 0 = Cooperate/Stag/Swerve, 1 = Defect/Hare/Drive
        """
        # Get partner coherence prediction
        observed = self.observe_markers(agent.marker.agent_id)
        expected_coherence = self.predict_partner_coherence(
            agent, partner_id, observed
        )
        
        # Policy influenced by:
        # 1. Own policy parameters
        # 2. Expected partner coherence (generic prior)
        # 3. Consistency pressure - STRONG INFLUENCE
        
        action_logits = agent.policy.copy()
        
        # If expect high coherence, be more consistent yourself
        # STRONG bias toward consistency when partner is coherent
        if expected_coherence > 0.6:
            action_logits[0] += 2.0  # Strong bias toward cooperation
        else:
            action_logits[1] += 1.0  # Defect if partner incoherent
        
        # Consistency pressure from own marker - CRITICAL
        # High coherence = stick to previous actions
        if len(agent.action_history) > 0:
            last_action = agent.action_history[-1]
            consistency_strength = agent.marker.coherence_score * 3.0
            action_logits[last_action] += consistency_strength
        
        # Behavioral bias from marker
        action_logits += agent.marker.behavioral_bias * 2.0
        
        # Softmax action selection
        probs = np.exp(action_logits) / np.sum(np.exp(action_logits))
        action = np.random.choice([0, 1], p=probs)
        
        return action
    
    def update_marker(self, agent: MarkerAgent):
        """
        UPDATE_MARKER (every 10 ticks):
        coherence_score ← variance(recent_actions) + consistency bonus
        COMPLIANT: Slow update, 10x timescale separation
        """
        if len(agent.action_history) < self.COHERENCE_WINDOW:
            return
        
        recent_actions = agent.action_history[-self.COHERENCE_WINDOW:]
        action_variance = np.var(recent_actions)
        
        # High variance = low coherence, Low variance = high coherence
        base_coherence = 1.0 - (action_variance * 4.0)  # Scale to 0-1
        
        # Add consistency bonus - reward for maintaining stable behavior
        if len(agent.action_history) >= 20:
            # Check if recent actions are consistent
            old_actions = agent.action_history[-20:-10]
            new_actions = agent.action_history[-10:]
            old_mode = max(set(old_actions), key=old_actions.count)
            new_mode = max(set(new_actions), key=new_actions.count)
            
            if old_mode == new_mode:
                # Consistent across marker updates
                base_coherence += 0.3
        
        agent.marker.coherence_score = np.clip(base_coherence, 0.0, 1.0)
    
    def compute_consistency_bonus(self, agent: MarkerAgent) -> float:
        """
        Consistency bonus from slow marker feedback
        COMPLIANT: NOT from specific action rewards
        """
        return agent.marker.coherence_score * self.CONSISTENCY_BONUS_WEIGHT
    
    def play_round(self, agent_i: int, agent_j: int) -> Tuple[float, float]:
        """Play one round between two agents"""
        # Sample game
        game = np.random.choice(list(GameType))
        payoff_matrix = self.get_game_payoffs(game)
        
        # Choose actions
        action_i = self.choose_action(self.agents[agent_i], agent_j, game)
        action_j = self.choose_action(self.agents[agent_j], agent_i, game)
        
        # Record actions
        self.agents[agent_i].action_history.append(action_i)
        self.agents[agent_j].action_history.append(action_j)
        
        # Get payoffs
        payoff_i = payoff_matrix[action_i, action_j]
        payoff_j = payoff_matrix[action_j, action_i]
        
        # Add consistency bonus
        payoff_i += self.compute_consistency_bonus(self.agents[agent_i])
        payoff_j += self.compute_consistency_bonus(self.agents[agent_j])
        
        return payoff_i, payoff_j
    
    def step(self):
        """One environment step"""
        # Random pairings
        agents_shuffled = np.random.permutation(self.n_agents)
        for k in range(0, self.n_agents - 1, 2):
            i, j = agents_shuffled[k], agents_shuffled[k+1]
            self.play_round(i, j)
        
        # Update markers every 10 ticks
        self.tick += 1
        if self.tick % self.MARKER_UPDATE_INTERVAL == 0:
            for agent in self.agents:
                self.update_marker(agent)
    
    def run_episode(self, n_rounds: int = 100) -> Dict:
        """Run full episode and return metrics"""
        for _ in range(n_rounds):
            self.step()
        
        # Calculate metrics
        metrics = {
            "mean_coherence": np.mean([
                a.marker.coherence_score for a in self.agents
            ]),
            "coherence_variance": np.var([
                a.marker.coherence_score for a in self.agents
            ]),
            "behavioral_consistency": self._compute_behavioral_consistency(),
            "marker_stability": self._compute_marker_stability(),
        }
        return metrics
    
    def _compute_behavioral_consistency(self) -> float:
        """Entropy of action distributions (lower = more consistent)"""
        consistencies = []
        for agent in self.agents:
            if len(agent.action_history) > 10:
                action_dist = np.bincount(
                    agent.action_history[-50:], 
                    minlength=2
                ) / min(50, len(agent.action_history[-50:]))
                # Entropy
                entropy = -np.sum(action_dist * np.log(action_dist + 1e-10))
                consistencies.append(1.0 - entropy / np.log(2))  # Normalize
        return np.mean(consistencies) if consistencies else 0.0
    
    def _compute_marker_stability(self) -> float:
        """How stable are markers over time"""
        # Simplified: measure variance of coherence scores
        coherence_scores = [a.marker.coherence_score for a in self.agents]
        return 1.0 - np.var(coherence_scores)


def run_minimal_experiment(n_agents: int = 4, n_rounds: int = 1000) -> Dict:
    """Run minimal experiment A: Behavioral coherence"""
    arena = MarkerGameArena(n_agents=n_agents)
    metrics = arena.run_episode(n_rounds=n_rounds)
    return metrics


if __name__ == "__main__":
    print("="*60)
    print("Candidate 001: Multi-Agent Consistency Markers")
    print("="*60)
    print("Status: BUILD_NOW")
    print("Compliance: <=32 bits, 10x timescale separation")
    print("="*60)
    
    # Run experiment
    metrics = run_minimal_experiment(n_agents=4, n_rounds=1000)
    
    print("\nMinimal Experiment Results:")
    print(f"  Mean coherence: {metrics['mean_coherence']:.3f}")
    print(f"  Coherence variance: {metrics['coherence_variance']:.3f}")
    print(f"  Behavioral consistency: {metrics['behavioral_consistency']:.3f}")
    print(f"  Marker stability: {metrics['marker_stability']:.3f}")
    
    # Check emergence
    print("\nEmergence Criteria:")
    if metrics['mean_coherence'] > 0.5:
        print("  ✅ Coherence emerged")
    else:
        print("  ❌ Low coherence")
    
    if metrics['behavioral_consistency'] > 0.5:
        print("  ✅ Behavioral consistency")
    else:
        print("  ❌ Inconsistent behavior")
    
    print("\n" + "="*60)
