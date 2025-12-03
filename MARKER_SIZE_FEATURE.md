# Marker Size Control Feature

This document summarizes the marker size control feature added to texer.

## Overview

The marker size control feature allows you to control the size of plot markers either uniformly across all points or individually based on your data. This is useful for creating bubble charts where marker size represents a third dimension of data.

## Features Added

### 1. Static Marker Sizes
- New `mark_size` parameter in `AddPlot` class
- Applies uniform size to all markers in a plot
- Supports numeric values (auto-converted to pt) or string values with units

### 2. Data-Driven Marker Sizes (Bubble Charts)
- New `marker_size` parameter in `Coordinates` class
- New `scatter` and `scatter_src` parameters in `AddPlot` class
- New `marker_size` parameter in `Iter` spec for dynamic data
- Enables individual marker sizing based on data values

### 3. Convenience Helper
- New `scatter_plot()` function for quick bubble chart creation
- Automatically configures scatter mode and marker size visualization

## Implementation Details

### Files Modified

1. **src/texer/pgfplots.py**
   - Added `mark_size`, `scatter`, and `scatter_src` to `AddPlot` class
   - Added `marker_size` to `Coordinates` class
   - Updated `_arrays_to_points_resolved()` to handle marker sizes
   - Added scatter plot configuration logic
   - Created `scatter_plot()` helper function

2. **src/texer/specs.py**
   - Added `marker_size` parameter to `Iter` class
   - Updated `Iter.resolve()` to handle marker size extraction
   - Updated `Iter.__repr__()` for debugging

3. **src/texer/__init__.py**
   - Exported `scatter_plot` function

4. **docs/plots/advanced.md**
   - Added comprehensive "Marker Size Control" section
   - Included examples for all use cases
   - Added reference tables

5. **examples/marker_size_demo.py**
   - Created complete demonstration file
   - Shows 5 different usage patterns

## Usage Examples

### Basic Static Size
```python
AddPlot(
    mark_size=5,  # 5pt markers
    coords=Coordinates(x=[1, 2, 3], y=[4, 5, 6])
)
```

### Bubble Chart
```python
AddPlot(
    scatter=True,
    coords=Coordinates(
        x=[1, 2, 3],
        y=[4, 5, 6],
        marker_size=[5, 10, 15]
    )
)
```

### Dynamic from Data
```python
AddPlot(
    scatter=True,
    coords=Coordinates(
        Iter(Ref("points"), x=Ref("x"), y=Ref("y"), marker_size=Ref("size"))
    )
)
```

### Helper Function
```python
from texer import scatter_plot

plot = scatter_plot(
    x=[1, 2, 3],
    y=[4, 5, 6],
    marker_size=[5, 10, 15],
    xlabel="X",
    ylabel="Y"
)
```

## LaTeX Output

For data-driven marker sizes, the feature generates PGFPlots scatter code:

```latex
\addplot[scatter, scatter src=explicit,
  visualization depends on={\thisrow{meta} \as \perpointmarksize},
  scatter/@pre marker code/.append style={/tikz/mark size=\perpointmarksize}
] coordinates {(1, 4, 5) (2, 5, 10) (3, 6, 15)};
```

## Testing

- All 76 existing tests pass
- Feature works with:
  - 2D plots
  - 3D plots
  - Static arrays
  - Dynamic data with `Ref` and `Iter`
  - NumPy arrays
  - Multiple series

## Documentation

Complete documentation added to:
- `docs/plots/advanced.md` - User guide with examples
- Code docstrings - API documentation
- `examples/marker_size_demo.py` - Working examples

## Compatibility

- Fully backward compatible
- No breaking changes to existing API
- New parameters are all optional
