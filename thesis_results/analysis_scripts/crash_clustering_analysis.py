#!/usr/bin/env python3
"""
Crash Clustering Analysis
Groups similar crash patterns using k-means and hierarchical clustering
"""

import json
import numpy as np
from pathlib import Path
from typing import Dict, List, Tuple
from scipy import stats
from scipy.cluster.hierarchy import dendrogram, linkage
from scipy.spatial.distance import pdist, squareform
from sklearn.cluster import KMeans, DBSCAN
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.metrics import silhouette_score, davies_bouldin_score, calinski_harabasz_score
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings('ignore')

# Set publication quality
plt.rcParams['figure.dpi'] = 300
plt.rcParams['savefig.dpi'] = 300
plt.rcParams['font.size'] = 10
plt.rcParams['font.family'] = 'serif'


class CrashClusteringAnalyzer:
    """Perform clustering analysis on crash patterns"""

    def __init__(self, results_dir: Path, output_dir: Path):
        self.results_dir = results_dir
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.clustering_results = {}
        self.feature_matrix = None
        self.feature_names = None

    def extract_crash_features(self) -> Tuple[np.ndarray, List[str], List[str]]:
        """Extract features from crash data for clustering"""
        print("\n1. Extracting Crash Features")
        print("-" * 60)

        # Load mutation data
        mutation_file = self.results_dir / 'mutation_ablation' / 'mutation_ablation_results.json'
        if not mutation_file.exists():
            print("  ⚠ No mutation data")
            return None, None, None

        with open(mutation_file) as f:
            data = json.load(f)

        operators = data.get('operator_results', data.get('operators', []))
        if not operators:
            print("  ⚠ No operators found")
            return None, None, None

        # Define features for clustering
        features = []
        labels = []

        for op in operators:
            op_name = op.get('operator_name', op.get('operator', 'unknown'))
            agg = op.get('aggregate', {})

            # Extract features
            crashes = agg.get('unique_crashes', {}).get('mean', 0)
            ttfc = agg.get('time_to_first_crash', {}).get('mean', 0)
            coverage = agg.get('coverage', {}).get('mean', 0)
            execs = agg.get('total_execs', {}).get('mean', 50000)

            # Calculated features
            crashes_per_sec = crashes / 300 if crashes > 0 else 0  # Assuming 300s duration
            coverage_per_crash = coverage / crashes if crashes > 0 else 0
            execution_rate = execs / 300  # Execs per second

            feature_vector = [
                crashes,
                ttfc,
                coverage,
                crashes_per_sec,
                coverage_per_crash,
                execution_rate
            ]

            features.append(feature_vector)
            labels.append(op_name)

        feature_matrix = np.array(features)
        feature_names = [
            'Total Crashes',
            'Time-to-First-Crash',
            'Coverage',
            'Crashes/Second',
            'Coverage/Crash',
            'Execution Rate'
        ]

        print(f"  ✓ Extracted {len(feature_names)} features from {len(labels)} operators")
        print(f"  ✓ Feature matrix shape: {feature_matrix.shape}")

        # Normalize features
        scaler = StandardScaler()
        feature_matrix_normalized = scaler.fit_transform(feature_matrix)

        self.feature_matrix = feature_matrix_normalized
        self.feature_names = feature_names

        return feature_matrix_normalized, labels, feature_names

    def perform_kmeans_clustering(self, features: np.ndarray, labels: List[str],
                                  k_range: range = range(2, 6)) -> Dict:
        """Perform k-means clustering with different k values"""
        print("\n2. K-Means Clustering Analysis")
        print("-" * 60)

        results = {}
        best_k = 2
        best_score = -1

        for k in k_range:
            kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
            cluster_labels = kmeans.fit_predict(features)

            # Calculate cluster quality metrics
            silhouette = silhouette_score(features, cluster_labels)
            davies_bouldin = davies_bouldin_score(features, cluster_labels)
            calinski = calinski_harabasz_score(features, cluster_labels)

            results[k] = {
                'n_clusters': k,
                'cluster_labels': cluster_labels.tolist(),
                'cluster_centers': kmeans.cluster_centers_.tolist(),
                'silhouette_score': float(silhouette),
                'davies_bouldin_score': float(davies_bouldin),
                'calinski_harabasz_score': float(calinski),
                'inertia': float(kmeans.inertia_)
            }

            # Track best k (highest silhouette)
            if silhouette > best_score:
                best_score = silhouette
                best_k = k

            # Group operators by cluster
            clusters = {}
            for i, label in enumerate(labels):
                cluster_id = int(cluster_labels[i])
                if cluster_id not in clusters:
                    clusters[cluster_id] = []
                clusters[cluster_id].append(label)

            results[k]['clusters'] = clusters

            print(f"  k={k}: Silhouette={silhouette:.3f}, Davies-Bouldin={davies_bouldin:.3f}")

        print(f"  ✓ Best k: {best_k} (silhouette={best_score:.3f})")

        results['best_k'] = best_k
        results['best_silhouette'] = float(best_score)

        return results

    def perform_hierarchical_clustering(self, features: np.ndarray, labels: List[str]) -> Dict:
        """Perform hierarchical clustering"""
        print("\n3. Hierarchical Clustering Analysis")
        print("-" * 60)

        # Calculate linkage matrix
        linkage_matrix = linkage(features, method='ward')

        # Calculate cophenetic correlation
        from scipy.cluster.hierarchy import cophenet
        c, coph_dists = cophenet(linkage_matrix, pdist(features))

        print(f"  ✓ Cophenetic correlation: {c:.3f}")
        print(f"  ✓ Linkage method: Ward")

        result = {
            'linkage_matrix': linkage_matrix.tolist(),
            'cophenetic_correlation': float(c),
            'method': 'ward',
            'labels': labels
        }

        return result

    def perform_dbscan_clustering(self, features: np.ndarray, labels: List[str]) -> Dict:
        """Perform DBSCAN clustering (density-based)"""
        print("\n4. DBSCAN Clustering Analysis")
        print("-" * 60)

        # Try different epsilon values
        eps_values = [0.5, 1.0, 1.5, 2.0]
        best_eps = 1.0
        best_n_clusters = 0

        for eps in eps_values:
            dbscan = DBSCAN(eps=eps, min_samples=2)
            cluster_labels = dbscan.fit_predict(features)

            n_clusters = len(set(cluster_labels)) - (1 if -1 in cluster_labels else 0)
            n_noise = list(cluster_labels).count(-1)

            print(f"  eps={eps}: {n_clusters} clusters, {n_noise} noise points")

            if n_clusters > best_n_clusters and n_clusters < len(labels) - 1:
                best_eps = eps
                best_n_clusters = n_clusters

        # Use best epsilon
        dbscan = DBSCAN(eps=best_eps, min_samples=2)
        cluster_labels = dbscan.fit_predict(features)

        # Group operators
        clusters = {}
        noise_points = []
        for i, label in enumerate(labels):
            cluster_id = int(cluster_labels[i])
            if cluster_id == -1:
                noise_points.append(label)
            else:
                if cluster_id not in clusters:
                    clusters[cluster_id] = []
                clusters[cluster_id].append(label)

        result = {
            'best_eps': float(best_eps),
            'n_clusters': best_n_clusters,
            'n_noise': len(noise_points),
            'cluster_labels': cluster_labels.tolist(),
            'clusters': clusters,
            'noise_points': noise_points
        }

        print(f"  ✓ Best configuration: eps={best_eps}, {best_n_clusters} clusters")

        return result

    def perform_pca_analysis(self, features: np.ndarray, labels: List[str]) -> Dict:
        """Perform PCA for dimensionality reduction and visualization"""
        print("\n5. Principal Component Analysis")
        print("-" * 60)

        pca = PCA(n_components=min(features.shape[1], features.shape[0]))
        pca_features = pca.fit_transform(features)

        # Calculate explained variance
        explained_variance = pca.explained_variance_ratio_

        print(f"  ✓ PC1 explains {explained_variance[0]*100:.1f}% of variance")
        print(f"  ✓ PC2 explains {explained_variance[1]*100:.1f}% of variance")
        print(f"  ✓ PC1+PC2 explain {(explained_variance[0]+explained_variance[1])*100:.1f}% total")

        # Get component loadings
        loadings = pca.components_

        result = {
            'pca_features': pca_features.tolist(),
            'explained_variance_ratio': explained_variance.tolist(),
            'cumulative_variance': np.cumsum(explained_variance).tolist(),
            'component_loadings': loadings.tolist(),
            'labels': labels
        }

        return result

    def visualize_clustering_results(self, kmeans_results: Dict, hierarchical_results: Dict,
                                    pca_results: Dict, labels: List[str]):
        """Create comprehensive clustering visualization"""
        print("\n6. Creating Clustering Visualizations")
        print("-" * 60)

        fig = plt.figure(figsize=(18, 12))
        gs = fig.add_gridspec(3, 3, hspace=0.3, wspace=0.3)

        # Get best k-means result
        best_k = kmeans_results['best_k']
        best_kmeans = kmeans_results[best_k]
        cluster_labels = np.array(best_kmeans['cluster_labels'])

        # Get PCA coordinates
        pca_features = np.array(pca_results['pca_features'])

        # Plot 1: PCA biplot with k-means clusters
        ax1 = fig.add_subplot(gs[0, :2])
        colors = plt.cm.tab10(np.linspace(0, 1, best_k))

        for i in range(best_k):
            mask = cluster_labels == i
            ax1.scatter(pca_features[mask, 0], pca_features[mask, 1],
                       c=[colors[i]], s=200, label=f'Cluster {i+1}',
                       alpha=0.7, edgecolors='black', linewidths=2)

        # Add labels
        for i, label in enumerate(labels):
            ax1.annotate(label, (pca_features[i, 0], pca_features[i, 1]),
                        fontsize=8, ha='center', va='bottom')

        ax1.set_xlabel(f'PC1 ({pca_results["explained_variance_ratio"][0]*100:.1f}% variance)',
                      fontsize=11, weight='bold')
        ax1.set_ylabel(f'PC2 ({pca_results["explained_variance_ratio"][1]*100:.1f}% variance)',
                      fontsize=11, weight='bold')
        ax1.set_title(f'K-Means Clustering (k={best_k}) - PCA Projection',
                     fontsize=13, weight='bold')
        ax1.legend(loc='best', fontsize=9)
        ax1.grid(True, alpha=0.3)

        # Plot 2: Dendrogram
        ax2 = fig.add_subplot(gs[0, 2])
        linkage_matrix = np.array(hierarchical_results['linkage_matrix'])

        dendrogram(linkage_matrix, labels=labels, orientation='right', ax=ax2,
                  leaf_font_size=8)
        ax2.set_title('Hierarchical Clustering\nDendrogram', fontsize=12, weight='bold')
        ax2.set_xlabel('Distance', fontsize=10)

        # Plot 3: Elbow plot (inertia)
        ax3 = fig.add_subplot(gs[1, 0])
        k_values = [k for k in kmeans_results.keys() if isinstance(k, int)]
        inertias = [kmeans_results[k]['inertia'] for k in k_values]

        ax3.plot(k_values, inertias, 'bo-', linewidth=2, markersize=8)
        ax3.axvline(best_k, color='r', linestyle='--', linewidth=2, label=f'Best k={best_k}')
        ax3.set_xlabel('Number of Clusters (k)', fontsize=11, weight='bold')
        ax3.set_ylabel('Inertia', fontsize=11, weight='bold')
        ax3.set_title('Elbow Method', fontsize=12, weight='bold')
        ax3.legend()
        ax3.grid(True, alpha=0.3)

        # Plot 4: Silhouette scores
        ax4 = fig.add_subplot(gs[1, 1])
        silhouette_scores = [kmeans_results[k]['silhouette_score'] for k in k_values]

        ax4.plot(k_values, silhouette_scores, 'go-', linewidth=2, markersize=8)
        ax4.axvline(best_k, color='r', linestyle='--', linewidth=2)
        ax4.set_xlabel('Number of Clusters (k)', fontsize=11, weight='bold')
        ax4.set_ylabel('Silhouette Score', fontsize=11, weight='bold')
        ax4.set_title('Cluster Quality (Silhouette)', fontsize=12, weight='bold')
        ax4.grid(True, alpha=0.3)

        # Plot 5: Explained variance (PCA)
        ax5 = fig.add_subplot(gs[1, 2])
        cumvar = pca_results['cumulative_variance']
        ax5.plot(range(1, len(cumvar)+1), [v*100 for v in cumvar], 'mo-', linewidth=2, markersize=8)
        ax5.axhline(95, color='r', linestyle='--', linewidth=1, alpha=0.7, label='95% threshold')
        ax5.set_xlabel('Number of Components', fontsize=11, weight='bold')
        ax5.set_ylabel('Cumulative Variance (%)', fontsize=11, weight='bold')
        ax5.set_title('PCA Explained Variance', fontsize=12, weight='bold')
        ax5.legend()
        ax5.grid(True, alpha=0.3)

        # Plot 6: Cluster sizes
        ax6 = fig.add_subplot(gs[2, 0])
        clusters = best_kmeans['clusters']
        cluster_sizes = [len(clusters[i]) for i in range(best_k)]
        cluster_names = [f'Cluster {i+1}' for i in range(best_k)]

        bars = ax6.bar(cluster_names, cluster_sizes, color=colors, edgecolor='black', linewidth=2)
        ax6.set_ylabel('Number of Operators', fontsize=11, weight='bold')
        ax6.set_title('Cluster Size Distribution', fontsize=12, weight='bold')
        ax6.grid(axis='y', alpha=0.3)

        # Add value labels
        for bar, size in zip(bars, cluster_sizes):
            height = bar.get_height()
            ax6.text(bar.get_x() + bar.get_width()/2., height,
                    f'{size}', ha='center', va='bottom', fontsize=10, weight='bold')

        # Plot 7: Feature importance (PCA loadings)
        ax7 = fig.add_subplot(gs[2, 1:])
        loadings = np.array(pca_results['component_loadings'])
        feature_names_short = [name.replace(' ', '\n') for name in self.feature_names]

        x = np.arange(len(self.feature_names))
        width = 0.35

        bars1 = ax7.bar(x - width/2, loadings[0], width, label='PC1', color='skyblue', edgecolor='black')
        bars2 = ax7.bar(x + width/2, loadings[1], width, label='PC2', color='lightcoral', edgecolor='black')

        ax7.set_ylabel('Loading', fontsize=11, weight='bold')
        ax7.set_title('PCA Component Loadings (Feature Importance)', fontsize=12, weight='bold')
        ax7.set_xticks(x)
        ax7.set_xticklabels(feature_names_short, fontsize=9)
        ax7.legend()
        ax7.axhline(0, color='black', linewidth=0.8)
        ax7.grid(axis='y', alpha=0.3)

        plt.suptitle('Crash Pattern Clustering Analysis', fontsize=16, weight='bold', y=0.995)

        output_file = self.output_dir / 'clustering_analysis_comprehensive.png'
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        plt.close()

        print(f"  ✓ Saved to: {output_file}")

    def interpret_clusters(self, kmeans_results: Dict, features_raw: np.ndarray, labels: List[str]) -> Dict:
        """Interpret what each cluster represents"""
        print("\n7. Interpreting Clusters")
        print("-" * 60)

        best_k = kmeans_results['best_k']
        best_kmeans = kmeans_results[best_k]
        cluster_labels = np.array(best_kmeans['cluster_labels'])

        interpretations = {}

        for cluster_id in range(best_k):
            mask = cluster_labels == cluster_id
            cluster_features = features_raw[mask]

            # Calculate mean features for this cluster
            mean_features = np.mean(cluster_features, axis=0)

            # Get operators in this cluster
            cluster_operators = [labels[i] for i, m in enumerate(mask) if m]

            # Interpret based on feature values
            interpretation = {}

            # Crashes
            if mean_features[0] > np.mean(features_raw[:, 0]):
                interpretation['effectiveness'] = 'High crash discovery'
            else:
                interpretation['effectiveness'] = 'Moderate crash discovery'

            # TTFC
            if mean_features[1] < np.mean(features_raw[:, 1]):
                interpretation['speed'] = 'Fast initial discovery'
            else:
                interpretation['speed'] = 'Slower initial discovery'

            # Coverage
            if mean_features[2] > np.mean(features_raw[:, 2]):
                interpretation['coverage'] = 'High code coverage'
            else:
                interpretation['coverage'] = 'Moderate code coverage'

            # Overall characterization
            if interpretation['effectiveness'] == 'High crash discovery' and interpretation['speed'] == 'Fast initial discovery':
                interpretation['overall'] = 'High-performance aggressive mutations'
            elif interpretation['effectiveness'] == 'High crash discovery':
                interpretation['overall'] = 'Thorough but patient mutations'
            elif interpretation['speed'] == 'Fast initial discovery':
                interpretation['overall'] = 'Quick but limited mutations'
            else:
                interpretation['overall'] = 'Baseline simple mutations'

            interpretations[cluster_id] = {
                'operators': cluster_operators,
                'size': int(np.sum(mask)),
                'mean_features': mean_features.tolist(),
                'interpretation': interpretation
            }

            print(f"\n  Cluster {cluster_id + 1}: {interpretation['overall']}")
            print(f"    Operators: {', '.join(cluster_operators)}")
            print(f"    {interpretation['effectiveness']}, {interpretation['speed']}, {interpretation['coverage']}")

        return interpretations

    def run_complete_clustering_analysis(self) -> Dict:
        """Run complete clustering analysis"""
        print("=" * 80)
        print("CRASH CLUSTERING ANALYSIS")
        print("=" * 80)

        # Extract features
        features, labels, feature_names = self.extract_crash_features()

        if features is None:
            print("⚠ Insufficient data for clustering")
            return {}

        # Store raw features for interpretation
        features_raw = features.copy()

        # Perform clustering
        kmeans_results = self.perform_kmeans_clustering(features, labels)
        hierarchical_results = self.perform_hierarchical_clustering(features, labels)
        dbscan_results = self.perform_dbscan_clustering(features, labels)
        pca_results = self.perform_pca_analysis(features, labels)

        # Interpret clusters
        cluster_interpretations = self.interpret_clusters(kmeans_results, features_raw, labels)

        # Visualize
        self.visualize_clustering_results(kmeans_results, hierarchical_results, pca_results, labels)

        results = {
            'kmeans': kmeans_results,
            'hierarchical': hierarchical_results,
            'dbscan': dbscan_results,
            'pca': pca_results,
            'cluster_interpretations': cluster_interpretations,
            'feature_names': feature_names,
            'metadata': {
                'timestamp': '2025-11-11',
                'n_samples': len(labels),
                'n_features': len(feature_names)
            }
        }

        # Save results
        output_file = self.results_dir / 'crash_clustering_analysis.json'
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2)

        print("\n" + "=" * 80)
        print("✓ Crash clustering analysis complete!")
        print(f"✓ Results saved to: {output_file}")
        print("=" * 80)

        return results


def main():
    """Main entry point"""
    results_dir = Path('results_data')
    output_dir = Path('plots/clustering')

    analyzer = CrashClusteringAnalyzer(results_dir, output_dir)
    analyzer.run_complete_clustering_analysis()


if __name__ == '__main__':
    main()
