"""Configuration for complexity calculation.

This file contains all constants, weights, and thresholds used in
the complexity calculation for property file changes.
"""

from dataclasses import dataclass
from typing import Tuple


@dataclass(frozen=True)
class MetricWeights:
    """Weights for complexity metrics.
    
    These weights determine the contribution of each metric
    to the block complexity score.
    
    Formula: block_score = (key_count × KEYS) + (max_depth × DEPTH) 
                          + (duplicate_count × DUPLICATES) + (loc × LOC)
    """
    
    KEYS: float = 0.40          # 40% - Number of keys
    DEPTH: float = 0.30         # 30% - Hierarchy depth
    DUPLICATES: float = 0.20    # 20% - Duplicate/override count
    LOC: float = 0.10           # 10% - Lines of code


@dataclass(frozen=True)
class NormalizationConfig:
    """Configuration for complexity score normalization.
    
    Uses asymptotic scaling formula:
    normalized = MAX_SCALE × (raw_score / (raw_score + HALF_POINT))
    
    This ensures scores are bounded and fit within risk thresholds.
    """
    
    MAX_SCALE: float = 40.0     # Maximum possible normalized value
    HALF_POINT: float = 30.0    # Raw score that maps to 50% of MAX_SCALE (i.e., 20)


@dataclass(frozen=True)
class RiskThresholds:
    """Thresholds for risk level classification.
    
    Risk levels based on normalized complexity score:
    - 0 to LOW_MAX: Low risk
    - LOW_MAX to MEDIUM_MAX: Medium risk
    - MEDIUM_MAX to HIGH_MAX: High risk
    - Above HIGH_MAX: Very High risk
    """
    
    LOW_MAX: float = 10.0       # 0-10: Low
    MEDIUM_MAX: float = 20.0    # 10-20: Medium
    HIGH_MAX: float = 30.0      # 20-30: High
    # > 30: Very High


@dataclass(frozen=True)
class RiskLevelInfo:
    """Risk level names and interpretations."""
    
    LOW: Tuple[str, str] = ("Low", "Simple, stable, and easy to maintain")
    MEDIUM: Tuple[str, str] = ("Medium", "Moderate complexity; review recommended")
    HIGH: Tuple[str, str] = ("High", "Complex structure; refactoring advised")
    VERY_HIGH: Tuple[str, str] = ("Very High", "Critical complexity; high failure risk")
    NO_CHANGES: Tuple[str, str] = ("Low", "No changes detected")
    SKIPPED: Tuple[str, str] = ("Skipped", "Change skipped from complexity calculation")


# Global configuration instances
METRIC_WEIGHTS = MetricWeights()
NORMALIZATION_CONFIG = NormalizationConfig()
RISK_THRESHOLDS = RiskThresholds()
RISK_LEVELS = RiskLevelInfo()
