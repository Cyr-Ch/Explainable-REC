"""
Visualization utilities for Chat-SGP results

Provides functions to plot energy flows, cost comparisons, and 24-hour profiles.
"""

import matplotlib.pyplot as plt
import numpy as np
from typing import Dict, Any, Optional, List
from pathlib import Path


def plot_energy_flows(data: Dict[str, Any], result: Dict[str, Any], 
                     save_path: Optional[str] = None, show: bool = True) -> None:
    """
    Plot 24-hour energy flows (PV, Load, Battery, Grid)
    
    Args:
        data: Data dictionary with PV, Load, and battery profiles
        result: Optimization result dictionary
        save_path: Optional path to save the plot
        show: Whether to display the plot
    """
    hours = list(range(24))
    pv = data.get('PV', [0] * 24)
    load = data.get('Load', [0] * 24)
    
    # Get battery and grid flows from result if available
    battery_charge = result.get('battery_charge', [0] * 24)
    battery_discharge = result.get('battery_discharge', [0] * 24)
    grid_import = result.get('grid_import', [0] * 24)
    grid_export = result.get('grid_export', [0] * 24)
    
    fig, axes = plt.subplots(2, 1, figsize=(12, 10))
    
    # Top plot: Energy flows
    ax1 = axes[0]
    ax1.plot(hours, pv, 'g-', label='PV Generation', linewidth=2, marker='o', markersize=4)
    ax1.plot(hours, load, 'r-', label='Load Demand', linewidth=2, marker='s', markersize=4)
    
    # Plot battery charge/discharge
    if any(battery_charge):
        ax1.bar([h - 0.2 for h in hours], battery_charge, width=0.4, 
                label='Battery Charge', color='blue', alpha=0.6)
    if any(battery_discharge):
        ax1.bar([h + 0.2 for h in hours], [-d for d in battery_discharge], width=0.4,
                label='Battery Discharge', color='orange', alpha=0.6)
    
    ax1.set_xlabel('Hour of Day', fontsize=12)
    ax1.set_ylabel('Energy (kWh)', fontsize=12)
    ax1.set_title('24-Hour Energy Flows', fontsize=14, fontweight='bold')
    ax1.legend(loc='best', fontsize=10)
    ax1.grid(True, alpha=0.3)
    ax1.set_xticks(hours)
    ax1.set_xlim(-0.5, 23.5)
    
    # Bottom plot: Grid interactions
    ax2 = axes[1]
    if any(grid_import):
        ax2.bar([h - 0.2 for h in hours], grid_import, width=0.4,
                label='Grid Import', color='red', alpha=0.7)
    if any(grid_export):
        ax2.bar([h + 0.2 for h in hours], grid_export, width=0.4,
                label='Grid Export', color='green', alpha=0.7)
    
    ax2.axhline(y=0, color='k', linestyle='-', linewidth=0.5)
    ax2.set_xlabel('Hour of Day', fontsize=12)
    ax2.set_ylabel('Energy (kWh)', fontsize=12)
    ax2.set_title('Grid Interactions', fontsize=14, fontweight='bold')
    ax2.legend(loc='best', fontsize=10)
    ax2.grid(True, alpha=0.3)
    ax2.set_xticks(hours)
    ax2.set_xlim(-0.5, 23.5)
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Plot saved to {save_path}")
    
    if show:
        plt.show()
    else:
        plt.close()


def plot_cost_comparison(baseline_cost: float, scenario_cost: float,
                        scenario_name: str = "Scenario",
                        save_path: Optional[str] = None, show: bool = True) -> None:
    """
    Plot cost comparison between baseline and scenario
    
    Args:
        baseline_cost: Baseline total cost
        scenario_cost: Scenario total cost
        scenario_name: Name of the scenario
        save_path: Optional path to save the plot
        show: Whether to display the plot
    """
    fig, ax = plt.subplots(figsize=(8, 6))
    
    costs = [baseline_cost, scenario_cost]
    labels = ['Baseline', scenario_name]
    colors = ['blue', 'green' if scenario_cost < baseline_cost else 'red']
    
    bars = ax.bar(labels, costs, color=colors, alpha=0.7, edgecolor='black', linewidth=1.5)
    
    # Add value labels on bars
    for bar, cost in zip(bars, costs):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'EUR {cost:.2f}',
                ha='center', va='bottom', fontsize=12, fontweight='bold')
    
    # Add change percentage
    if baseline_cost > 0:
        change = scenario_cost - baseline_cost
        change_pct = (change / baseline_cost) * 100
        change_text = f"{change:+.2f} EUR ({change_pct:+.1f}%)"
        
        ax.text(0.5, max(costs) * 0.9, f'Change: {change_text}',
                ha='center', va='center', fontsize=11,
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    
    ax.set_ylabel('Total Cost (EUR)', fontsize=12)
    ax.set_title('Cost Comparison: Baseline vs Scenario', fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3, axis='y')
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Plot saved to {save_path}")
    
    if show:
        plt.show()
    else:
        plt.close()


def plot_24h_profile(profile: List[float], label: str, 
                    save_path: Optional[str] = None, show: bool = True) -> None:
    """
    Plot a 24-hour profile
    
    Args:
        profile: List of 24 values
        label: Label for the profile
        save_path: Optional path to save the plot
        show: Whether to display the plot
    """
    hours = list(range(24))
    
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(hours, profile, 'o-', linewidth=2, markersize=6, label=label)
    ax.fill_between(hours, profile, alpha=0.3)
    
    ax.set_xlabel('Hour of Day', fontsize=12)
    ax.set_ylabel('Value', fontsize=12)
    ax.set_title(f'24-Hour Profile: {label}', fontsize=14, fontweight='bold')
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3)
    ax.set_xticks(hours)
    ax.set_xlim(-0.5, 23.5)
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Plot saved to {save_path}")
    
    if show:
        plt.show()
    else:
        plt.close()


def plot_multiple_scenarios(scenarios: List[Dict[str, Any]], 
                           save_path: Optional[str] = None, show: bool = True) -> None:
    """
    Plot multiple scenarios for comparison
    
    Args:
        scenarios: List of scenario dictionaries, each with 'name', 'cost', and optionally 'data'
        save_path: Optional path to save the plot
        show: Whether to display the plot
    """
    fig, ax = plt.subplots(figsize=(12, 6))
    
    names = [s['name'] for s in scenarios]
    costs = [s['cost'] for s in scenarios]
    
    colors = plt.cm.viridis(np.linspace(0, 1, len(scenarios)))
    bars = ax.bar(names, costs, color=colors, alpha=0.7, edgecolor='black', linewidth=1.5)
    
    # Add value labels
    for bar, cost in zip(bars, costs):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'EUR {cost:.2f}',
                ha='center', va='bottom', fontsize=10, fontweight='bold')
    
    ax.set_ylabel('Total Cost (EUR)', fontsize=12)
    ax.set_title('Multiple Scenarios Comparison', fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3, axis='y')
    plt.xticks(rotation=45, ha='right')
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Plot saved to {save_path}")
    
    if show:
        plt.show()
    else:
        plt.close()

