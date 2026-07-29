"""
Constants module containing system-wide default calibration parameters.
"""

# Business & Tariff settings
DEFAULT_TARIFF = 8.5          # INR per kWh
DEFAULT_CARBON_FACTOR = 0.82    # kg CO2 per kWh (India Grid Standard)

# Technical alert thresholds
POWER_FACTOR_THRESHOLD = 0.90   # Alert if Power Factor drops below this
HVAC_TEMP_LOW_THRESHOLD = 24.0   # Degree Celsius, below which AC usage is inefficient
PEAK_LOAD_MULTIPLIER = 1.5      # Alert if load exceeds 1.5x historical mean
IDLE_LOAD_THRESHOLD_KW = 2.0    # kW, threshold for idle consumption with zero occupants

# Target metrics
TARGET_POWER_FACTOR = 0.95      # Desired power factor for efficiency calculations
BUILDING_EEI_BENCHMARK = 0.15   # kWh per floor-occupant benchmark
