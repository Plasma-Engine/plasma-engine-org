#!/usr/bin/env python3
"""State Cleanup and Optimization for Self-Healing System.

Manages cleanup of temporary state, optimization of automation frequency,
and maintenance of system efficiency. Runs as the final step of the
orchestrator workflow.
"""

from __future__ import annotations

import json
import os
import sys
import time
import typing as t
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path


@dataclass
class CleanupMetrics:
    """Metrics for cleanup operations."""
    
    files_cleaned: int = 0
    space_freed_bytes: int = 0
    state_files_optimized: int = 0
    old_records_removed: int = 0


def cleanup_old_state_files() -> CleanupMetrics:
    """Clean up old state files and optimize storage."""
    
    metrics = CleanupMetrics()
    state_dir = Path(".github/state")
    
    if not state_dir.exists():
        return metrics
    
    # Clean up old temporary files
    temp_patterns = ["*.tmp", "*.lock", "*.temp"]
    for pattern in temp_patterns:
        for temp_file in state_dir.glob(pattern):
            try:
                file_size = temp_file.stat().st_size
                temp_file.unlink()
                metrics.files_cleaned += 1
                metrics.space_freed_bytes += file_size
            except Exception as exc:
                print(f"Warning: Failed to remove {temp_file}: {exc}")
    
    # Optimize rate limit state
    rate_limit_file = state_dir / "rate-limits.json"
    if rate_limit_file.exists():
        try:
            with open(rate_limit_file, 'r') as f:
                rate_data = json.load(f)
            
            # Reset counters if window is very old
            window_start = rate_data.get("window_start", "")
            if window_start:
                window_time = datetime.fromisoformat(window_start.replace('Z', '+00:00'))
                if datetime.utcnow().replace(tzinfo=window_time.tzinfo) - window_time > timedelta(hours=2):
                    rate_data.update({
                        "coderabbit_requests": 0,
                        "claude_requests": 0,
                        "cursor_requests": 0,
                        "window_start": datetime.utcnow().isoformat(),
                        "last_updated": datetime.utcnow().isoformat(),
                    })
                    
                    with open(rate_limit_file, 'w') as f:
                        json.dump(rate_data, f, indent=2)
                    
                    metrics.state_files_optimized += 1
                    
        except Exception as exc:
            print(f"Warning: Failed to optimize rate limit state: {exc}")
    
    # Optimize health history
    health_file = state_dir / "health-history.json"
    if health_file.exists():
        try:
            with open(health_file, 'r') as f:
                health_data = json.load(f)
            
            if isinstance(health_data, list):
                original_count = len(health_data)
                
                # Remove records older than 7 days
                cutoff_time = datetime.utcnow() - timedelta(days=7)
                filtered_data = []
                
                for record in health_data:
                    try:
                        record_time = datetime.fromisoformat(
                            record.get("timestamp", "").replace('Z', '+00:00')
                        )
                        if record_time > cutoff_time:
                            filtered_data.append(record)
                    except (ValueError, TypeError):
                        # Keep records without valid timestamps
                        filtered_data.append(record)
                
                # Keep only last 168 records (1 week at hourly intervals)
                filtered_data = filtered_data[-168:]
                
                if len(filtered_data) < original_count:
                    with open(health_file, 'w') as f:
                        json.dump(filtered_data, f, indent=2)
                    
                    metrics.old_records_removed += original_count - len(filtered_data)
                    metrics.state_files_optimized += 1
                    
        except Exception as exc:
            print(f"Warning: Failed to optimize health history: {exc}")
    
    return metrics


def analyze_system_performance() -> dict[str, t.Any]:
    """Analyze recent system performance for optimization."""
    
    state_dir = Path(".github/state")
    health_file = state_dir / "health-history.json"
    
    analysis = {
        "average_response_time": 0.0,
        "success_rate": 0.0,
        "bottleneck_services": [],
        "optimization_suggestions": [],
        "recent_activity_level": "normal",
    }
    
    if not health_file.exists():
        return analysis
    
    try:
        with open(health_file, 'r') as f:
            health_data = json.load(f)
        
        if not isinstance(health_data, list) or len(health_data) < 3:
            return analysis
        
        # Analyze recent records (last 24 hours)
        recent_cutoff = datetime.utcnow() - timedelta(hours=24)
        recent_records = []
        
        for record in health_data[-24:]:  # Last 24 records
            try:
                record_time = datetime.fromisoformat(
                    record.get("timestamp", "").replace('Z', '+00:00')
                )
                if record_time > recent_cutoff:
                    recent_records.append(record)
            except (ValueError, TypeError):
                continue
        
        if not recent_records:
            return analysis
        
        # Calculate success rates
        workflow_success_rates = {}
        total_prs_processed = 0
        
        for record in recent_records:
            workflow_stats = record.get("workflow_analysis", {}).get("workflow_stats", {})
            for workflow_name, stats in workflow_stats.items():
                if workflow_name not in workflow_success_rates:
                    workflow_success_rates[workflow_name] = []
                workflow_success_rates[workflow_name].append(stats.get("success_rate", 0.0))
            
            total_prs_processed += record.get("pr_analysis", {}).get("total_open_prs", 0)
        
        # Calculate average success rate
        all_rates = []
        for rates in workflow_success_rates.values():
            all_rates.extend(rates)
        
        if all_rates:
            analysis["success_rate"] = sum(all_rates) / len(all_rates)
        
        # Identify bottlenecks
        for workflow_name, rates in workflow_success_rates.items():
            avg_rate = sum(rates) / len(rates) if rates else 0
            if avg_rate < 0.8:  # Less than 80% success rate
                analysis["bottleneck_services"].append({
                    "service": workflow_name,
                    "success_rate": avg_rate,
                    "severity": "high" if avg_rate < 0.6 else "medium"
                })
        
        # Determine activity level
        avg_prs = total_prs_processed / len(recent_records) if recent_records else 0
        if avg_prs > 10:
            analysis["recent_activity_level"] = "high"
        elif avg_prs < 3:
            analysis["recent_activity_level"] = "low"
        
        # Generate optimization suggestions
        if analysis["success_rate"] < 0.7:
            analysis["optimization_suggestions"].append(
                "Consider increasing automation retry attempts"
            )
        
        if analysis["recent_activity_level"] == "high":
            analysis["optimization_suggestions"].append(
                "Consider increasing rate limits during high activity periods"
            )
        
        if len(analysis["bottleneck_services"]) > 2:
            analysis["optimization_suggestions"].append(
                "Multiple services showing low success rates - investigate common issues"
            )
        
    except Exception as exc:
        print(f"Warning: Failed to analyze system performance: {exc}")
    
    return analysis


def generate_optimization_recommendations(
    cleanup_metrics: CleanupMetrics,
    performance_analysis: dict
) -> list[str]:
    """Generate specific optimization recommendations."""
    
    recommendations = []
    
    # Based on cleanup metrics
    if cleanup_metrics.files_cleaned > 10:
        recommendations.append(
            "High number of temporary files detected - consider optimizing state management"
        )
    
    if cleanup_metrics.old_records_removed > 50:
        recommendations.append(
            "Large amount of old data removed - verify retention policies are appropriate"
        )
    
    # Based on performance analysis
    success_rate = performance_analysis.get("success_rate", 1.0)
    if success_rate < 0.8:
        recommendations.append(
            f"Overall success rate is {success_rate:.1%} - investigate workflow failures"
        )
    
    bottlenecks = performance_analysis.get("bottleneck_services", [])
    if bottlenecks:
        recommendations.append(
            f"Bottleneck services detected: {', '.join([b['service'] for b in bottlenecks])}"
        )
    
    activity_level = performance_analysis.get("recent_activity_level", "normal")
    if activity_level == "high":
        recommendations.append(
            "High activity detected - consider scaling automation resources"
        )
    elif activity_level == "low":
        recommendations.append(
            "Low activity detected - consider reducing automation frequency to save resources"
        )
    
    # Add performance-based suggestions
    recommendations.extend(performance_analysis.get("optimization_suggestions", []))
    
    return recommendations


def update_system_config_if_needed(recommendations: list[str]) -> bool:
    """Update system configuration based on recommendations if needed."""
    
    # This is a placeholder for future dynamic configuration updates
    # For now, we just log recommendations
    
    if not recommendations:
        return False
    
    print("\\n📝 Optimization Recommendations:")
    for i, rec in enumerate(recommendations, 1):
        print(f"   {i}. {rec}")
    
    # In the future, this could automatically adjust:
    # - Rate limits based on activity
    # - Retry attempts based on success rates  
    # - Workflow frequency based on performance
    # - Resource allocation based on bottlenecks
    
    return False  # No automatic updates implemented yet


def main() -> None:
    """Main state cleanup and optimization logic."""
    
    print("🧹 Self-Healing System State Cleanup")
    
    # Perform cleanup operations
    cleanup_metrics = cleanup_old_state_files()
    print(f"   Files cleaned: {cleanup_metrics.files_cleaned}")
    print(f"   Space freed: {cleanup_metrics.space_freed_bytes:,} bytes")
    print(f"   State files optimized: {cleanup_metrics.state_files_optimized}")
    
    # Analyze system performance
    performance_analysis = analyze_system_performance()
    success_rate = performance_analysis.get("success_rate", 0.0)
    activity_level = performance_analysis.get("recent_activity_level", "unknown")
    print(f"   Recent success rate: {success_rate:.1%}")
    print(f"   Activity level: {activity_level}")
    
    # Generate optimization recommendations
    recommendations = generate_optimization_recommendations(
        cleanup_metrics, performance_analysis
    )
    
    # Update configuration if needed
    config_updated = update_system_config_if_needed(recommendations)
    
    # Create final summary
    summary = {
        "timestamp": datetime.utcnow().isoformat(),
        "cleanup_metrics": {
            "files_cleaned": cleanup_metrics.files_cleaned,
            "space_freed_bytes": cleanup_metrics.space_freed_bytes,
            "state_files_optimized": cleanup_metrics.state_files_optimized,
            "old_records_removed": cleanup_metrics.old_records_removed,
        },
        "performance_analysis": performance_analysis,
        "recommendations_count": len(recommendations),
        "recommendations": recommendations,
        "config_updated": config_updated,
        "system_health": "good" if success_rate > 0.8 else "needs_attention",
    }
    
    print(f"\\n✅ State cleanup complete:")
    print(f"   System health: {summary['system_health']}")
    print(f"   Recommendations: {len(recommendations)}")
    print(f"   Configuration updated: {'Yes' if config_updated else 'No'}")
    
    print(f"\\n{json.dumps(summary, indent=2)}")


if __name__ == "__main__":
    main()