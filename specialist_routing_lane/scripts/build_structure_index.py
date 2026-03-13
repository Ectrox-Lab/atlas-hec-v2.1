#!/usr/bin/env python3
"""
Structure Index Builder
P2.6 Specialist Routing Lane - Gate SR1

Builds embedding space and clusters for structure fingerprints.
"""

import argparse
import json
import logging
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import yaml
import numpy as np

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class StructureIndexBuilder:
    """Builds clustering index for structure fingerprints"""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config = self._load_config(config_path)
        self.fingerprints: List[Dict] = []
        self.embeddings: Optional[np.ndarray] = None
        self.clusters: Optional[np.ndarray] = None
        self.candidate_ids: List[str] = []
        
    def _load_config(self, path: Optional[str]) -> Dict:
        """Load clustering configuration"""
        if path is None:
            path = Path(__file__).parent.parent / "configs" / "clustering_config.yaml"
        
        try:
            with open(path, 'r') as f:
                return yaml.safe_load(f)
        except Exception as e:
            logger.warning(f"Could not load config: {e}. Using defaults.")
            return self._default_config()
    
    def _default_config(self) -> Dict:
        """Default configuration"""
        return {
            "preprocessing": {
                "normalization": {"method": "robust"},
                "dimensionality_reduction": {"method": "umap", "umap": {"n_neighbors": 15, "min_dist": 0.1}}
            },
            "clustering": {
                "primary_algorithm": "hdbscan",
                "hdbscan": {"min_cluster_size": 5, "min_samples": 3}
            }
        }
    
    def load_fingerprints(self, input_path: Path) -> None:
        """Load fingerprints from JSONL file"""
        logger.info(f"Loading fingerprints from {input_path}")
        
        with open(input_path, 'r') as f:
            for line in f:
                if line.strip():
                    self.fingerprints.append(json.loads(line))
        
        self.candidate_ids = [fp["candidate_id"] for fp in self.fingerprints]
        logger.info(f"Loaded {len(self.fingerprints)} fingerprints")
    
    def flatten_fingerprint(self, fp: Dict) -> np.ndarray:
        """Flatten fingerprint dict to vector"""
        vector = []
        
        # Organizational
        org = fp.get("organizational", {})
        vector.extend([
            org.get("cwci_total", 0),
            org.get("specialization", 0),
            org.get("integration", 0),
            org.get("broadcast", 0),
            float(org.get("hierarchy_depth", 1)),
            org.get("autonomy_strength", 0),
        ])
        # Encode memory_partition_style
        style = org.get("memory_partition_style", "distributed")
        style_encoding = {"distributed": 0, "centralized": 1, "hybrid": 2, "federated": 3}
        vector.append(float(style_encoding.get(style, 0)))
        
        # Robustness
        rob = fp.get("robustness", {})
        vector.extend([
            rob.get("scale_retention", 0),
            rob.get("seed_variance", 0),
            rob.get("cwci_min", 0),
            rob.get("cwci_max", 0),
            rob.get("stress_coverage", 0),
            rob.get("pass_rate", 0),
        ])
        
        # Behavioral
        beh = fp.get("behavioral", {})
        vector.extend([
            beh.get("recovery_time", 0),
            beh.get("energy_stability", 0),
            beh.get("coordination_score", 0),
            beh.get("hazard_resistance", 0),
            beh.get("communication_cost", 0),
        ])
        
        # Failure
        fail = fp.get("failure", {})
        vector.append(fail.get("seed_spike_risk", 0))
        
        # Derived
        der = fp.get("derived", {})
        vector.extend([
            der.get("stability_index", 0),
            der.get("consciousness_depth", 0),
            der.get("robustness_score", 0),
            der.get("risk_score", 0),
        ])
        
        return np.array(vector, dtype=np.float32)
    
    def build_feature_matrix(self) -> np.ndarray:
        """Build feature matrix from fingerprints"""
        logger.info("Building feature matrix")
        
        vectors = [self.flatten_fingerprint(fp) for fp in self.fingerprints]
        X = np.stack(vectors)
        
        logger.info(f"Feature matrix shape: {X.shape}")
        return X
    
    def normalize(self, X: np.ndarray) -> np.ndarray:
        """Normalize features"""
        method = self.config.get("preprocessing", {}).get("normalization", {}).get("method", "robust")
        
        if method == "standard":
            from sklearn.preprocessing import StandardScaler
            scaler = StandardScaler()
            return scaler.fit_transform(X)
        elif method == "robust":
            from sklearn.preprocessing import RobustScaler
            scaler = RobustScaler()
            return scaler.fit_transform(X)
        elif method == "minmax":
            from sklearn.preprocessing import MinMaxScaler
            scaler = MinMaxScaler()
            return scaler.fit_transform(X)
        else:
            return X
    
    def reduce_dimensions(self, X: np.ndarray) -> np.ndarray:
        """Reduce dimensions for visualization and clustering"""
        dr_config = self.config.get("preprocessing", {}).get("dimensionality_reduction", {})
        method = dr_config.get("method", "umap")
        
        if method == "umap":
            try:
                import umap
                umap_config = dr_config.get("umap", {})
                reducer = umap.UMAP(
                    n_neighbors=umap_config.get("n_neighbors", 15),
                    min_dist=umap_config.get("min_dist", 0.1),
                    n_components=umap_config.get("n_components", 2),
                    random_state=umap_config.get("random_state", 42)
                )
                return reducer.fit_transform(X)
            except ImportError:
                logger.warning("UMAP not available, using PCA fallback")
                method = "pca"
        
        if method == "pca":
            from sklearn.decomposition import PCA
            pca_config = dr_config.get("pca", {})
            n_components = pca_config.get("n_components", 0.95)
            
            if n_components < 1:
                pca = PCA(n_components=n_components)
            else:
                pca = PCA(n_components=int(n_components))
            return pca.fit_transform(X)
        
        if method == "tsne":
            from sklearn.manifold import TSNE
            tsne_config = dr_config.get("tsne", {})
            tsne = TSNE(
                n_components=2,
                perplexity=tsne_config.get("perplexity", 30),
                random_state=tsne_config.get("random_state", 42)
            )
            return tsne.fit_transform(X)
        
        return X
    
    def cluster(self, X: np.ndarray) -> np.ndarray:
        """Perform clustering"""
        cluster_config = self.config.get("clustering", {})
        algorithm = cluster_config.get("primary_algorithm", "hdbscan")
        
        if algorithm == "hdbscan":
            try:
                import hdbscan
                hdb_config = cluster_config.get("hdbscan", {})
                # Adjust min_cluster_size for small datasets
                min_cluster_size = min(hdb_config.get("min_cluster_size", 5), len(X) // 2)
                min_samples = min(hdb_config.get("min_samples", 3), min_cluster_size - 1)
                clusterer = hdbscan.HDBSCAN(
                    min_cluster_size=max(min_cluster_size, 3),
                    min_samples=max(min_samples, 2),
                    metric=hdb_config.get("metric", "euclidean"),
                    cluster_selection_method=hdb_config.get("cluster_selection_method", "eom")
                )
                labels = clusterer.fit_predict(X)
                n_clusters = len(set(labels)) - (1 if -1 in labels else 0)
                logger.info(f"HDBSCAN found {n_clusters} clusters")
                if n_clusters < 2:
                    logger.warning("HDBSCAN found too few clusters, using KMeans")
                    algorithm = "kmeans"
                else:
                    return labels
            except ImportError:
                logger.warning("HDBSCAN not available, using KMeans fallback")
                algorithm = "kmeans"
            except Exception as e:
                logger.warning(f"HDBSCAN failed: {e}, using KMeans")
                algorithm = "kmeans"
        
        if algorithm == "kmeans":
            from sklearn.cluster import KMeans
            # Use elbow method or silhouette to find optimal k
            from sklearn.metrics import silhouette_score
            
            best_k = 3
            best_score = -1
            for k in range(2, min(10, len(X))):
                kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
                labels = kmeans.fit_predict(X)
                if len(set(labels)) > 1:
                    score = silhouette_score(X, labels)
                    if score > best_score:
                        best_k = k
                        best_score = score
            
            kmeans = KMeans(n_clusters=best_k, random_state=42, n_init=10)
            labels = kmeans.fit_predict(X)
            logger.info(f"KMeans found {best_k} clusters (silhouette: {best_score:.3f})")
            return labels
        
        # Fallback: all in one cluster
        return np.zeros(len(X), dtype=int)
    
    def label_regions(self, labels: np.ndarray) -> Dict[int, str]:
        """Assign semantic labels to clusters"""
        region_labels = {}
        
        for cluster_id in set(labels):
            if cluster_id == -1:
                region_labels[cluster_id] = "noise"
                continue
            
            # Get fingerprints in this cluster
            indices = np.where(labels == cluster_id)[0]
            cluster_fps = [self.fingerprints[i] for i in indices]
            
            # Calculate average metrics
            avg_risk = np.mean([fp.get("derived", {}).get("risk_score", 0) for fp in cluster_fps])
            avg_retention = np.mean([fp.get("robustness", {}).get("scale_retention", 0) for fp in cluster_fps])
            avg_variance = np.mean([fp.get("robustness", {}).get("seed_variance", 0) for fp in cluster_fps])
            avg_pass = np.mean([fp.get("robustness", {}).get("pass_rate", 0) for fp in cluster_fps])
            
            # Label based on criteria
            if avg_risk > 0.7:
                region_labels[cluster_id] = "seed_spike_zone"
            elif avg_retention > 0.8 and avg_variance < 0.2 and avg_pass > 0.7:
                region_labels[cluster_id] = "stable_region"
            elif avg_variance > 0.4:
                region_labels[cluster_id] = "high_variance_region"
            else:
                region_labels[cluster_id] = f"region_{cluster_id}"
        
        return region_labels
    
    def build_index(self, input_path: Path, output_dir: Path) -> Dict:
        """Build complete structure index"""
        # Load data
        self.load_fingerprints(input_path)
        
        if len(self.fingerprints) < 3:
            logger.error("Need at least 3 fingerprints for clustering")
            return {}
        
        # Build features
        X = self.build_feature_matrix()
        
        # Normalize
        X_norm = self.normalize(X)
        
        # Reduce dimensions
        self.embeddings = self.reduce_dimensions(X_norm)
        
        # Cluster
        self.clusters = self.cluster(self.embeddings)
        
        # Label regions
        region_labels = self.label_regions(self.clusters)
        
        # Build results
        results = {
            "candidates": [],
            "clusters": {},
            "region_labels": region_labels,
            "statistics": {}
        }
        
        for i, fp in enumerate(self.fingerprints):
            cluster_id = int(self.clusters[i])
            results["candidates"].append({
                "candidate_id": fp["candidate_id"],
                "candidate_name": fp.get("candidate_name", fp["candidate_id"]),
                "cluster_id": cluster_id,
                "region_label": region_labels.get(cluster_id, "unknown"),
                "embedding": self.embeddings[i].tolist(),
                "risk_score": fp.get("derived", {}).get("risk_score", 0)
            })
        
        # Cluster statistics
        for cluster_id in set(self.clusters):
            indices = np.where(self.clusters == cluster_id)[0]
            cluster_candidates = [results["candidates"][i] for i in indices]
            results["clusters"][str(cluster_id)] = {
                "size": len(indices),
                "region_label": region_labels.get(cluster_id, "unknown"),
                "candidates": [c["candidate_id"] for c in cluster_candidates]
            }
        
        # Overall statistics
        results["statistics"] = {
            "total_candidates": len(self.fingerprints),
            "num_clusters": len(set(self.clusters)) - (1 if -1 in self.clusters else 0),
            "noise_points": int(np.sum(self.clusters == -1)),
            "embedding_dim": self.embeddings.shape[1]
        }
        
        return results
    
    def save_results(self, results: Dict, output_dir: Path) -> None:
        """Save clustering results"""
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Convert numpy types to Python types for JSON serialization
        def convert_keys(obj):
            if isinstance(obj, dict):
                return {str(k): convert_keys(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [convert_keys(i) for i in obj]
            elif isinstance(obj, (np.integer, np.floating)):
                return float(obj) if isinstance(obj, np.floating) else int(obj)
            elif isinstance(obj, np.ndarray):
                return obj.tolist()
            return obj
        
        results = convert_keys(results)
        
        # Save main results
        with open(output_dir / "regions_v1.json", 'w') as f:
            json.dump(results, f, indent=2)
        
        # Save embeddings
        np.save(output_dir / "embedding_v1.npy", self.embeddings)
        
        # Save cluster labels
        np.save(output_dir / "clusters_v1.npy", self.clusters)
        
        # Save candidate mapping
        mapping = {c["candidate_id"]: c for c in results["candidates"]}
        with open(output_dir / "candidate_mapping.json", 'w') as f:
            json.dump(mapping, f, indent=2)
        
        logger.info(f"Results saved to {output_dir}")


def main():
    parser = argparse.ArgumentParser(
        description="Build structure index from fingerprints"
    )
    parser.add_argument(
        "--input", "-i",
        type=Path,
        required=True,
        help="Input fingerprints file (JSONL)"
    )
    parser.add_argument(
        "--output", "-o",
        type=Path,
        required=True,
        help="Output directory for index files"
    )
    parser.add_argument(
        "--config", "-c",
        type=Path,
        help="Path to clustering config YAML"
    )
    
    args = parser.parse_args()
    
    if not args.input.exists():
        logger.error(f"Input file does not exist: {args.input}")
        sys.exit(1)
    
    # Build index
    builder = StructureIndexBuilder(args.config)
    results = builder.build_index(args.input, args.output)
    
    if not results:
        logger.error("Failed to build index")
        sys.exit(1)
    
    # Save results
    builder.save_results(results, args.output)
    
    # Print summary
    print("\n" + "="*60)
    print("INDEX BUILDING SUMMARY")
    print("="*60)
    stats = results["statistics"]
    print(f"Total candidates: {stats['total_candidates']}")
    print(f"Clusters found: {stats['num_clusters']}")
    print(f"Noise points: {stats['noise_points']}")
    print(f"Embedding dimension: {stats['embedding_dim']}")
    
    print("\nRegion Distribution:")
    for cluster_id, info in results["clusters"].items():
        print(f"  {info['region_label']} (n={info['size']}): {info['candidates'][:3]}...")


if __name__ == "__main__":
    main()
