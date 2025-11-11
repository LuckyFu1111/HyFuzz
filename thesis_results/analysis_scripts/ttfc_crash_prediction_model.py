#!/usr/bin/env python3
"""
TTFC Crash Prediction Model
Uses Time-to-First-Crash to predict final crash count using regression models
"""

import json
import numpy as np
from pathlib import Path
from typing import Dict, List, Tuple
from scipy import stats
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression, Ridge, Lasso
from sklearn.preprocessing import PolynomialFeatures
from sklearn.model_selection import cross_val_score, LeaveOneOut
from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error
import warnings
warnings.filterwarnings('ignore')

# Set publication quality
plt.rcParams['figure.dpi'] = 300
plt.rcParams['savefig.dpi'] = 300
plt.rcParams['font.size'] = 10
plt.rcParams['font.family'] = 'serif'


class TTFCPredictionModel:
    """Build and evaluate TTFC-based crash prediction models"""

    def __init__(self, results_dir: Path, output_dir: Path):
        self.results_dir = results_dir
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.models = {}
        self.data = {}

    def load_and_prepare_data(self) -> Tuple[np.ndarray, np.ndarray]:
        """Load data and extract TTFC vs Crashes"""
        print("\n1. Loading and Preparing Data")
        print("-" * 60)

        # Load mutation operator data
        mutation_file = self.results_dir / 'mutation_ablation' / 'mutation_ablation_results.json'
        ttfc_values = []
        crash_values = []

        if mutation_file.exists():
            with open(mutation_file) as f:
                data = json.load(f)

            operators = data.get('operator_results', data.get('operators', []))
            for op in operators:
                agg = op.get('aggregate', {})
                ttfc = agg.get('time_to_first_crash', {}).get('mean', 0)
                crashes = agg.get('unique_crashes', {}).get('mean', 0)

                if ttfc > 0 and crashes > 0:
                    ttfc_values.append(ttfc)
                    crash_values.append(crashes)

        # Load seed sensitivity data
        seed_file = self.results_dir / 'seed_sensitivity' / 'seed_sensitivity_results.json'
        if seed_file.exists():
            with open(seed_file) as f:
                data = json.load(f)

            configs = data.get('configurations', [])
            for config in configs:
                agg = config.get('aggregate', {})
                ttfc = agg.get('time_to_first_crash', {}).get('mean', 0)
                crashes = agg.get('unique_crashes', {}).get('mean', 0)

                if ttfc > 0 and crashes > 0:
                    ttfc_values.append(ttfc)
                    crash_values.append(crashes)

        X = np.array(ttfc_values).reshape(-1, 1)
        y = np.array(crash_values)

        print(f"  ✓ Loaded {len(X)} data points")
        print(f"  ✓ TTFC range: [{X.min():.2f}, {X.max():.2f}] seconds")
        print(f"  ✓ Crashes range: [{y.min():.1f}, {y.max():.1f}]")

        self.data['X'] = X
        self.data['y'] = y

        return X, y

    def build_linear_model(self, X: np.ndarray, y: np.ndarray) -> Dict:
        """Build simple linear regression model"""
        print("\n2. Building Linear Regression Model")
        print("-" * 60)

        model = LinearRegression()
        model.fit(X, y)

        # Predictions
        y_pred = model.predict(X)

        # Metrics
        r2 = r2_score(y, y_pred)
        mse = mean_squared_error(y, y_pred)
        rmse = np.sqrt(mse)
        mae = mean_absolute_error(y, y_pred)

        # Cross-validation (Leave-One-Out for small datasets)
        if len(X) < 30:
            cv_scores = cross_val_score(model, X, y, cv=LeaveOneOut(),
                                       scoring='r2')
        else:
            cv_scores = cross_val_score(model, X, y, cv=5, scoring='r2')

        results = {
            'model_type': 'Linear Regression',
            'equation': f'Crashes = {model.intercept_:.2f} + {model.coef_[0]:.2f} × TTFC',
            'coefficients': {
                'intercept': float(model.intercept_),
                'slope': float(model.coef_[0])
            },
            'metrics': {
                'r2': float(r2),
                'rmse': float(rmse),
                'mae': float(mae),
                'cv_r2_mean': float(cv_scores.mean()),
                'cv_r2_std': float(cv_scores.std())
            }
        }

        print(f"  ✓ Equation: {results['equation']}")
        print(f"  ✓ R² = {r2:.4f}")
        print(f"  ✓ RMSE = {rmse:.2f} crashes")
        print(f"  ✓ Cross-validation R² = {cv_scores.mean():.4f} ± {cv_scores.std():.4f}")

        self.models['linear'] = {'model': model, 'results': results}
        return results

    def build_polynomial_model(self, X: np.ndarray, y: np.ndarray, degree: int = 2) -> Dict:
        """Build polynomial regression model"""
        print(f"\n3. Building Polynomial Regression Model (degree={degree})")
        print("-" * 60)

        # Create polynomial features
        poly_features = PolynomialFeatures(degree=degree, include_bias=False)
        X_poly = poly_features.fit_transform(X)

        model = LinearRegression()
        model.fit(X_poly, y)

        # Predictions
        y_pred = model.predict(X_poly)

        # Metrics
        r2 = r2_score(y, y_pred)
        mse = mean_squared_error(y, y_pred)
        rmse = np.sqrt(mse)
        mae = mean_absolute_error(y, y_pred)

        # Cross-validation
        if len(X) < 30:
            cv_scores = cross_val_score(model, X_poly, y, cv=LeaveOneOut(),
                                       scoring='r2')
        else:
            cv_scores = cross_val_score(model, X_poly, y, cv=5, scoring='r2')

        # Build equation string
        if degree == 2:
            equation = f'Crashes = {model.intercept_:.2f} + {model.coef_[0]:.2f}×TTFC + {model.coef_[1]:.2f}×TTFC²'
        else:
            equation = f'Polynomial degree {degree}'

        results = {
            'model_type': f'Polynomial Regression (degree {degree})',
            'equation': equation,
            'coefficients': {
                'intercept': float(model.intercept_),
                'coef': [float(c) for c in model.coef_]
            },
            'metrics': {
                'r2': float(r2),
                'rmse': float(rmse),
                'mae': float(mae),
                'cv_r2_mean': float(cv_scores.mean()),
                'cv_r2_std': float(cv_scores.std())
            }
        }

        print(f"  ✓ Equation: {equation}")
        print(f"  ✓ R² = {r2:.4f}")
        print(f"  ✓ RMSE = {rmse:.2f} crashes")
        print(f"  ✓ Cross-validation R² = {cv_scores.mean():.4f} ± {cv_scores.std():.4f}")

        self.models['polynomial'] = {
            'model': model,
            'poly_features': poly_features,
            'results': results
        }
        return results

    def build_regularized_models(self, X: np.ndarray, y: np.ndarray) -> Dict:
        """Build Ridge and Lasso regularized models"""
        print("\n4. Building Regularized Models")
        print("-" * 60)

        results = {}

        # Ridge regression
        ridge = Ridge(alpha=1.0)
        ridge.fit(X, y)
        y_pred_ridge = ridge.predict(X)
        r2_ridge = r2_score(y, y_pred_ridge)

        results['ridge'] = {
            'model_type': 'Ridge Regression',
            'r2': float(r2_ridge),
            'coefficient': float(ridge.coef_[0]),
            'intercept': float(ridge.intercept_)
        }

        # Lasso regression
        lasso = Lasso(alpha=0.1)
        lasso.fit(X, y)
        y_pred_lasso = lasso.predict(X)
        r2_lasso = r2_score(y, y_pred_lasso)

        results['lasso'] = {
            'model_type': 'Lasso Regression',
            'r2': float(r2_lasso),
            'coefficient': float(lasso.coef_[0]),
            'intercept': float(lasso.intercept_)
        }

        print(f"  ✓ Ridge R² = {r2_ridge:.4f}")
        print(f"  ✓ Lasso R² = {r2_lasso:.4f}")

        self.models['ridge'] = {'model': ridge, 'results': results['ridge']}
        self.models['lasso'] = {'model': lasso, 'results': results['lasso']}

        return results

    def make_predictions(self, ttfc_values: List[float]) -> Dict:
        """Make predictions for new TTFC values"""
        print("\n5. Example Predictions")
        print("-" * 60)

        predictions = {}

        for ttfc in ttfc_values:
            ttfc_array = np.array([[ttfc]])

            # Linear model prediction
            linear_pred = self.models['linear']['model'].predict(ttfc_array)[0]

            # Polynomial model prediction
            poly_features = self.models['polynomial']['poly_features']
            ttfc_poly = poly_features.transform(ttfc_array)
            poly_pred = self.models['polynomial']['model'].predict(ttfc_poly)[0]

            predictions[f'ttfc_{ttfc}s'] = {
                'ttfc_seconds': ttfc,
                'predicted_crashes_linear': float(linear_pred),
                'predicted_crashes_polynomial': float(poly_pred)
            }

            print(f"  TTFC = {ttfc:5.1f}s → Predicted crashes: {linear_pred:.1f} (linear), {poly_pred:.1f} (poly)")

        return predictions

    def visualize_predictions(self, X: np.ndarray, y: np.ndarray):
        """Create visualization of prediction models"""
        print("\n6. Creating Visualization")
        print("-" * 60)

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

        # Sort for smooth lines
        sort_idx = np.argsort(X.flatten())
        X_sorted = X[sort_idx]
        y_sorted = y[sort_idx]

        # Plot 1: All models comparison
        ax1.scatter(X, y, alpha=0.6, s=80, label='Actual Data', color='darkblue', edgecolors='black')

        # Linear prediction
        X_range = np.linspace(X.min(), X.max(), 100).reshape(-1, 1)
        y_linear = self.models['linear']['model'].predict(X_range)
        ax1.plot(X_range, y_linear, 'r-', linewidth=2, label='Linear Regression', alpha=0.8)

        # Polynomial prediction
        poly_features = self.models['polynomial']['poly_features']
        X_poly_range = poly_features.transform(X_range)
        y_poly = self.models['polynomial']['model'].predict(X_poly_range)
        ax1.plot(X_range, y_poly, 'g--', linewidth=2, label='Polynomial (degree 2)', alpha=0.8)

        ax1.set_xlabel('Time-to-First-Crash (seconds)', fontsize=12, weight='bold')
        ax1.set_ylabel('Final Unique Crashes', fontsize=12, weight='bold')
        ax1.set_title('TTFC Crash Prediction Models', fontsize=14, weight='bold')
        ax1.legend(loc='best', fontsize=10)
        ax1.grid(True, alpha=0.3)

        # Add R² annotations
        linear_r2 = self.models['linear']['results']['metrics']['r2']
        poly_r2 = self.models['polynomial']['results']['metrics']['r2']
        ax1.text(0.05, 0.95, f'Linear R² = {linear_r2:.4f}\nPoly R² = {poly_r2:.4f}',
                transform=ax1.transAxes, fontsize=10, verticalalignment='top',
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))

        # Plot 2: Residual analysis
        y_pred_linear = self.models['linear']['model'].predict(X)
        residuals = y - y_pred_linear

        ax2.scatter(y_pred_linear, residuals, alpha=0.6, s=80, color='darkgreen', edgecolors='black')
        ax2.axhline(y=0, color='r', linestyle='--', linewidth=2, alpha=0.7)
        ax2.set_xlabel('Predicted Crashes (Linear Model)', fontsize=12, weight='bold')
        ax2.set_ylabel('Residuals', fontsize=12, weight='bold')
        ax2.set_title('Residual Plot (Linear Model)', fontsize=14, weight='bold')
        ax2.grid(True, alpha=0.3)

        # Add residual statistics
        residual_mean = np.mean(residuals)
        residual_std = np.std(residuals)
        ax2.text(0.05, 0.95, f'Mean = {residual_mean:.2f}\nStd = {residual_std:.2f}',
                transform=ax2.transAxes, fontsize=10, verticalalignment='top',
                bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.8))

        plt.tight_layout()
        output_file = self.output_dir / 'ttfc_crash_prediction_models.png'
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        plt.close()

        print(f"  ✓ Saved to: {output_file}")

    def generate_practical_guidelines(self) -> str:
        """Generate practical guidelines for using the model"""
        linear_results = self.models['linear']['results']
        slope = linear_results['coefficients']['slope']
        intercept = linear_results['coefficients']['intercept']

        guidelines = "\n" + "=" * 80 + "\n"
        guidelines += "PRACTICAL GUIDELINES: USING TTFC FOR CAMPAIGN PREDICTION\n"
        guidelines += "=" * 80 + "\n\n"

        guidelines += "Prediction Equation (Linear Model):\n"
        guidelines += f"  Expected Crashes = {intercept:.2f} + ({slope:.2f}) × TTFC\n\n"

        guidelines += "How to Use in Practice:\n"
        guidelines += "1. Start fuzzing campaign\n"
        guidelines += "2. Record time-to-first-crash (TTFC)\n"
        guidelines += "3. Use equation above to estimate final crash count\n"
        guidelines += "4. Make resource allocation decisions:\n"
        guidelines += f"   - If TTFC < 5s  → High-value campaign (expect ≥ {intercept + slope * 5:.0f} crashes)\n"
        guidelines += f"   - If TTFC > 15s → Low-value campaign (expect ≤ {intercept + slope * 15:.0f} crashes)\n\n"

        guidelines += "Decision Rules:\n"
        guidelines += "- TTFC < 3s:  🔥 Excellent - allocate maximum resources\n"
        guidelines += "- TTFC 3-8s:  ✓  Good - continue with normal resources\n"
        guidelines += "- TTFC 8-15s: ⚠  Fair - consider adjusting strategy\n"
        guidelines += "- TTFC > 15s: ⛔ Poor - reallocate resources elsewhere\n\n"

        guidelines += "Model Performance:\n"
        guidelines += f"- R² = {linear_results['metrics']['r2']:.4f} (explains {linear_results['metrics']['r2']*100:.1f}% of variance)\n"
        guidelines += f"- RMSE = {linear_results['metrics']['rmse']:.2f} crashes\n"
        guidelines += f"- Cross-validation R² = {linear_results['metrics']['cv_r2_mean']:.4f}\n\n"

        guidelines += "Limitations:\n"
        guidelines += "- Model trained on simulation data\n"
        guidelines += "- Best used as relative ranking tool, not absolute predictor\n"
        guidelines += "- Should be validated on your specific target protocols\n"

        return guidelines

    def run_complete_prediction_analysis(self) -> Dict:
        """Run complete prediction model analysis"""
        print("=" * 80)
        print("TTFC CRASH PREDICTION MODEL")
        print("=" * 80)

        # Load data
        X, y = self.load_and_prepare_data()

        if len(X) < 3:
            print("\n⚠ Insufficient data for modeling")
            return {}

        # Build models
        linear_results = self.build_linear_model(X, y)
        poly_results = self.build_polynomial_model(X, y, degree=2)
        regularized_results = self.build_regularized_models(X, y)

        # Make example predictions
        example_ttfc_values = [1, 3, 5, 10, 15, 20]
        predictions = self.make_predictions(example_ttfc_values)

        # Visualize
        self.visualize_predictions(X, y)

        # Generate guidelines
        print(self.generate_practical_guidelines())

        results = {
            'linear_model': linear_results,
            'polynomial_model': poly_results,
            'regularized_models': regularized_results,
            'example_predictions': predictions,
            'metadata': {
                'n_training_points': len(X),
                'ttfc_range': [float(X.min()), float(X.max())],
                'crash_range': [float(y.min()), float(y.max())],
                'timestamp': '2025-11-11'
            }
        }

        # Save results
        output_file = self.results_dir / 'ttfc_crash_prediction.json'
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2)

        print("\n" + "=" * 80)
        print("✓ TTFC crash prediction model complete!")
        print(f"✓ Results saved to: {output_file}")
        print("=" * 80)

        return results


def main():
    """Main entry point"""
    results_dir = Path('results_data')
    output_dir = Path('plots/prediction')

    modeler = TTFCPredictionModel(results_dir, output_dir)
    modeler.run_complete_prediction_analysis()


if __name__ == '__main__':
    main()
