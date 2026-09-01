# math_visualizer.py
"""
Mathematical visualization utilities for the AI Teacher.

This module creates educational mathematical visuals such as:

- Function graphs
- Coordinate plots
- Equations
- Number lines
- Geometric shapes
- Data charts

The implementation uses matplotlib, which is free and
runs locally.

The generated visuals are saved under:
    data/generated_visuals/
"""

from __future__ import annotations

import math
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple


class MathVisualizer:
    """
    Generate mathematical visualizations locally using matplotlib.
    """

    def __init__(
        self,
        output_directory: str = "data/generated_visuals",
    ) -> None:
        self.output_directory = Path(output_directory)
        self.output_directory.mkdir(
            parents=True,
            exist_ok=True,
        )

    def plot_function(
        self,
        expression: str,
        x_min: float = -10,
        x_max: float = 10,
        points: int = 500,
        title: Optional[str] = None,
        x_label: str = "x",
        y_label: str = "y",
        filename: Optional[str] = None,
        output_format: str = "png",
    ) -> Dict[str, Any]:
        """
        Plot a mathematical function.

        Example:

            visualizer.plot_function(
                expression="x**2",
                x_min=-5,
                x_max=5,
            )

        Supported expression examples:

            x**2
            2*x + 1
            sin(x)
            cos(x)
            sqrt(abs(x))
            exp(x)
            log(abs(x))
        """

        if not expression.strip():
            raise ValueError(
                "Expression cannot be empty."
            )

        if x_max <= x_min:
            raise ValueError(
                "x_max must be greater than x_min."
            )

        if points < 10:
            raise ValueError(
                "points must be at least 10."
            )

        output_format = self._validate_format(
            output_format
        )

        plt = self._get_matplotlib()

        x_values = self._linspace(
            x_min,
            x_max,
            points,
        )

        y_values = []

        for x in x_values:
            try:
                y = self._evaluate_expression(
                    expression,
                    x,
                )

                if (
                    not math.isfinite(y)
                    or abs(y) > 1e10
                ):
                    y = float("nan")

            except Exception:
                y = float("nan")

            y_values.append(y)

        fig, ax = plt.subplots(
            figsize=(9, 5.5)
        )

        ax.plot(
            x_values,
            y_values,
        )

        ax.axhline(
            0,
            linewidth=0.8,
        )

        ax.axvline(
            0,
            linewidth=0.8,
        )

        ax.grid(
            True,
            alpha=0.25,
        )

        ax.set_xlabel(x_label)
        ax.set_ylabel(y_label)

        ax.set_title(
            title or f"y = {expression}"
        )

        fig.tight_layout()

        output_path = self._get_output_path(
            filename or "function_graph",
            output_format,
        )

        fig.savefig(
            output_path,
            format=output_format,
            bbox_inches="tight",
        )

        plt.close(fig)

        return {
            "success": True,
            "type": "function_graph",
            "expression": expression,
            "path": str(output_path),
            "format": output_format,
            "x_range": [
                x_min,
                x_max,
            ],
        }

    def plot_points(
        self,
        points: Sequence[
            Tuple[float, float]
        ],
        title: str = "Coordinate Points",
        x_label: str = "x",
        y_label: str = "y",
        connect: bool = False,
        filename: Optional[str] = None,
        output_format: str = "png",
    ) -> Dict[str, Any]:
        """
        Plot a collection of coordinate points.
        """

        if not points:
            raise ValueError(
                "At least one point is required."
            )

        output_format = self._validate_format(
            output_format
        )

        plt = self._get_matplotlib()

        x_values = [
            point[0]
            for point in points
        ]

        y_values = [
            point[1]
            for point in points
        ]

        fig, ax = plt.subplots(
            figsize=(8, 6)
        )

        if connect:
            ax.plot(
                x_values,
                y_values,
                marker="o",
            )
        else:
            ax.scatter(
                x_values,
                y_values,
            )

        for x, y in points:
            ax.annotate(
                f"({x}, {y})",
                (x, y),
                xytext=(5, 5),
                textcoords="offset points",
            )

        ax.axhline(
            0,
            linewidth=0.8,
        )

        ax.axvline(
            0,
            linewidth=0.8,
        )

        ax.grid(
            True,
            alpha=0.25,
        )

        ax.set_title(title)
        ax.set_xlabel(x_label)
        ax.set_ylabel(y_label)

        fig.tight_layout()

        output_path = self._get_output_path(
            filename or "coordinate_points",
            output_format,
        )

        fig.savefig(
            output_path,
            format=output_format,
            bbox_inches="tight",
        )

        plt.close(fig)

        return {
            "success": True,
            "type": "coordinate_plot",
            "path": str(output_path),
            "format": output_format,
            "points": [
                {
                    "x": point[0],
                    "y": point[1],
                }
                for point in points
            ],
        }

    def plot_number_line(
        self,
        minimum: int,
        maximum: int,
        highlighted: Optional[
            Sequence[float]
        ] = None,
        title: str = "Number Line",
        filename: Optional[str] = None,
        output_format: str = "png",
    ) -> Dict[str, Any]:
        """
        Create a number-line visualization.
        """

        if maximum <= minimum:
            raise ValueError(
                "maximum must be greater than minimum."
            )

        output_format = self._validate_format(
            output_format
        )

        highlighted = list(
            highlighted or []
        )

        plt = self._get_matplotlib()

        fig, ax = plt.subplots(
            figsize=(10, 2.5)
        )

        ax.hlines(
            0,
            minimum,
            maximum,
            linewidth=2,
        )

        for value in range(
            minimum,
            maximum + 1,
        ):
            ax.vlines(
                value,
                -0.08,
                0.08,
                linewidth=1.5,
            )

            ax.text(
                value,
                -0.18,
                str(value),
                ha="center",
                va="top",
            )

        for value in highlighted:
            ax.scatter(
                [value],
                [0],
                s=100,
                zorder=3,
            )

        ax.set_xlim(
            minimum - 0.5,
            maximum + 0.5,
        )

        ax.set_ylim(
            -0.45,
            0.45,
        )

        ax.set_title(title)
        ax.axis("off")

        fig.tight_layout()

        output_path = self._get_output_path(
            filename or "number_line",
            output_format,
        )

        fig.savefig(
            output_path,
            format=output_format,
            bbox_inches="tight",
        )

        plt.close(fig)

        return {
            "success": True,
            "type": "number_line",
            "path": str(output_path),
            "format": output_format,
            "minimum": minimum,
            "maximum": maximum,
            "highlighted": highlighted,
        }

    def plot_bar_chart(
        self,
        labels: Sequence[str],
        values: Sequence[float],
        title: str = "Bar Chart",
        x_label: str = "",
        y_label: str = "Value",
        filename: Optional[str] = None,
        output_format: str = "png",
    ) -> Dict[str, Any]:
        """
        Create a simple bar chart.
        """

        if not labels:
            raise ValueError(
                "At least one label is required."
            )

        if len(labels) != len(values):
            raise ValueError(
                "labels and values must have the same length."
            )

        output_format = self._validate_format(
            output_format
        )

        plt = self._get_matplotlib()

        fig, ax = plt.subplots(
            figsize=(9, 5)
        )

        positions = list(
            range(len(labels))
        )

        ax.bar(
            positions,
            values,
        )

        ax.set_xticks(
            positions
        )

        ax.set_xticklabels(
            labels,
            rotation=30,
            ha="right",
        )

        ax.set_title(title)
        ax.set_xlabel(x_label)
        ax.set_ylabel(y_label)

        ax.grid(
            axis="y",
            alpha=0.25,
        )

        fig.tight_layout()

        output_path = self._get_output_path(
            filename or "bar_chart",
            output_format,
        )

        fig.savefig(
            output_path,
            format=output_format,
            bbox_inches="tight",
        )

        plt.close(fig)

        return {
            "success": True,
            "type": "bar_chart",
            "path": str(output_path),
            "format": output_format,
            "labels": list(labels),
            "values": list(values),
        }

    def plot_geometry(
        self,
        shape: str,
        parameters: Dict[str, float],
        title: Optional[str] = None,
        filename: Optional[str] = None,
        output_format: str = "png",
    ) -> Dict[str, Any]:
        """
        Generate a basic geometric visualization.

        Supported shapes:

        - circle
        - rectangle
        - square
        - triangle
        """

        shape = shape.strip().lower()

        supported = {
            "circle",
            "rectangle",
            "square",
            "triangle",
        }

        if shape not in supported:
            raise ValueError(
                f"Unsupported shape: {shape}. "
                f"Supported shapes: {sorted(supported)}"
            )

        output_format = self._validate_format(
            output_format
        )

        plt = self._get_matplotlib()

        fig, ax = plt.subplots(
            figsize=(7, 7)
        )

        if shape == "circle":
            self._draw_circle(
                ax,
                parameters,
            )

        elif shape in {
            "rectangle",
            "square",
        }:
            self._draw_rectangle(
                ax,
                parameters,
                shape,
            )

        elif shape == "triangle":
            self._draw_triangle(
                ax,
                parameters,
            )

        ax.set_aspect(
            "equal",
            adjustable="box",
        )

        ax.grid(
            True,
            alpha=0.25,
        )

        ax.set_title(
            title or shape.capitalize()
        )

        fig.tight_layout()

        output_path = self._get_output_path(
            filename or f"{shape}_diagram",
            output_format,
        )

        fig.savefig(
            output_path,
            format=output_format,
            bbox_inches="tight",
        )

        plt.close(fig)

        return {
            "success": True,
            "type": "geometry",
            "shape": shape,
            "parameters": parameters,
            "path": str(output_path),
            "format": output_format,
        }

    def create_equation_card(
        self,
        equation: str,
        explanation: Optional[str] = None,
        title: str = "Mathematical Formula",
        filename: Optional[str] = None,
        output_format: str = "png",
    ) -> Dict[str, Any]:
        """
        Create an image containing a mathematical equation
        and optional explanation.
        """

        if not equation.strip():
            raise ValueError(
                "Equation cannot be empty."
            )

        output_format = self._validate_format(
            output_format
        )

        plt = self._get_matplotlib()

        fig, ax = plt.subplots(
            figsize=(10, 4)
        )

        ax.text(
            0.5,
            0.62,
            self._latex_safe(
                equation
            ),
            ha="center",
            va="center",
            fontsize=24,
        )

        if explanation:
            ax.text(
                0.5,
                0.25,
                explanation,
                ha="center",
                va="center",
                fontsize=13,
                wrap=True,
            )

        ax.set_title(title)
        ax.axis("off")

        fig.tight_layout()

        output_path = self._get_output_path(
            filename or "equation_card",
            output_format,
        )

        fig.savefig(
            output_path,
            format=output_format,
            bbox_inches="tight",
        )

        plt.close(fig)

        return {
            "success": True,
            "type": "equation_card",
            "equation": equation,
            "path": str(output_path),
            "format": output_format,
        }

    def _draw_circle(
        self,
        ax: Any,
        parameters: Dict[str, float],
    ) -> None:
        """
        Draw a circle.
        """

        radius = float(
            parameters.get(
                "radius",
                1,
            )
        )

        if radius <= 0:
            raise ValueError(
                "Circle radius must be positive."
            )

        center_x = float(
            parameters.get(
                "center_x",
                0,
            )
        )

        center_y = float(
            parameters.get(
                "center_y",
                0,
            )
        )

        import matplotlib.patches as patches

        circle = patches.Circle(
            (
                center_x,
                center_y,
            ),
            radius,
            fill=False,
            linewidth=2,
        )

        ax.add_patch(circle)

        ax.scatter(
            [center_x],
            [center_y],
            s=40,
        )

        ax.set_xlim(
            center_x - radius * 1.4,
            center_x + radius * 1.4,
        )

        ax.set_ylim(
            center_y - radius * 1.4,
            center_y + radius * 1.4,
        )

    def _draw_rectangle(
        self,
        ax: Any,
        parameters: Dict[str, float],
        shape: str,
    ) -> None:
        """
        Draw a rectangle or square.
        """

        width = float(
            parameters.get(
                "width",
                parameters.get(
                    "side",
                    2,
                ),
            )
        )

        height = float(
            parameters.get(
                "height",
                parameters.get(
                    "side",
                    2,
                ),
            )
        )

        if width <= 0 or height <= 0:
            raise ValueError(
                "Rectangle dimensions must be positive."
            )

        import matplotlib.patches as patches

        rectangle = patches.Rectangle(
            (
                0,
                0,
            ),
            width,
            height,
            fill=False,
            linewidth=2,
        )

        ax.add_patch(rectangle)

        ax.text(
            width / 2,
            -height * 0.08,
            f"width = {width:g}",
            ha="center",
        )

        ax.text(
            width * 1.03,
            height / 2,
            f"height = {height:g}",
            va="center",
            rotation=90,
        )

        ax.set_xlim(
            -width * 0.2,
            width * 1.3,
        )

        ax.set_ylim(
            -height * 0.2,
            height * 1.2,
        )

    def _draw_triangle(
        self,
        ax: Any,
        parameters: Dict[str, float],
    ) -> None:
        """
        Draw a basic triangle.

        Supported parameters:

        base
        height
        """

        base = float(
            parameters.get(
                "base",
                4,
            )
        )

        height = float(
            parameters.get(
                "height",
                3,
            )
        )

        if base <= 0 or height <= 0:
            raise ValueError(
                "Triangle dimensions must be positive."
            )

        x = [
            0,
            base,
            base / 2,
            0,
        ]

        y = [
            0,
            0,
            height,
            0,
        ]

        ax.plot(
            x,
            y,
            linewidth=2,
        )

        ax.text(
            base / 2,
            -height * 0.08,
            f"base = {base:g}",
            ha="center",
        )

        ax.text(
            base / 2,
            height / 2,
            f"height = {height:g}",
            ha="center",
        )

        ax.set_xlim(
            -base * 0.2,
            base * 1.2,
        )

        ax.set_ylim(
            -height * 0.2,
            height * 1.2,
        )

    def _evaluate_expression(
        self,
        expression: str,
        x: float,
    ) -> float:
        """
        Safely evaluate a mathematical expression.

        Only approved mathematical functions and constants
        are available.
        """

        allowed = {
            "x": x,
            "pi": math.pi,
            "e": math.e,
            "sin": math.sin,
            "cos": math.cos,
            "tan": math.tan,
            "asin": math.asin,
            "acos": math.acos,
            "atan": math.atan,
            "sqrt": math.sqrt,
            "log": math.log,
            "log10": math.log10,
            "exp": math.exp,
            "abs": abs,
            "floor": math.floor,
            "ceil": math.ceil,
        }

        expression = expression.strip()

        # Prevent common unsafe constructs.
        forbidden = {
            "__",
            "import",
            "open(",
            "exec(",
            "eval(",
            "compile(",
            "globals(",
            "locals(",
        }

        lowered = expression.lower()

        if any(
            item in lowered
            for item in forbidden
        ):
            raise ValueError(
                "Expression contains unsupported operations."
            )

        # Convert common mathematical notation.
        expression = expression.replace(
            "^",
            "**",
        )

        result = eval(
            expression,
            {
                "__builtins__": {},
            },
            allowed,
        )

        if not isinstance(
            result,
            (int, float),
        ):
            raise ValueError(
                "Expression did not produce a numeric result."
            )

        return float(result)

    @staticmethod
    def _linspace(
        start: float,
        stop: float,
        count: int,
    ) -> List[float]:
        """
        Create evenly spaced numeric values.
        """

        if count == 1:
            return [start]

        step = (
            stop - start
        ) / (count - 1)

        return [
            start + step * index
            for index in range(count)
        ]

    def _get_matplotlib(self):
        """
        Import matplotlib lazily.

        The Agg backend is used so visualization generation
        works on servers without a graphical desktop.
        """

        try:
            import matplotlib

            matplotlib.use("Agg")

            import matplotlib.pyplot as plt

            return plt

        except ImportError as exc:
            raise RuntimeError(
                "matplotlib is not installed. "
                "Install it with: pip install matplotlib"
            ) from exc

    @staticmethod
    def _validate_format(
        output_format: str,
    ) -> str:
        """
        Validate image output format.
        """

        output_format = (
            output_format
            .strip()
            .lower()
        )

        if output_format not in {
            "png",
            "svg",
            "pdf",
        }:
            raise ValueError(
                "output_format must be png, svg, or pdf."
            )

        return output_format

    def _get_output_path(
        self,
        filename: str,
        output_format: str,
    ) -> Path:
        """
        Create a safe output path.
        """

        filename = Path(
            filename
        ).stem

        filename = re.sub(
            r"[^a-zA-Z0-9_-]+",
            "_",
            filename,
        )

        filename = filename.strip("_")

        if not filename:
            filename = "math_visual"

        output_path = (
            self.output_directory
            / f"{filename}.{output_format}"
        )

        return output_path

    @staticmethod
    def _latex_safe(
        equation: str,
    ) -> str:
        """
        Convert a basic equation into matplotlib-friendly math text.
        """

        equation = equation.strip()

        # If the user already supplied math delimiters,
        # remove them before adding our own.
        equation = equation.strip("$")

        replacements = {
            "sqrt": r"\sqrt",
            "pi": r"\pi",
            "<=": r"\leq",
            ">=": r"\geq",
        }

        for old, new in replacements.items():
            equation = equation.replace(
                old,
                new,
            )

        return f"${equation}$"


# Default shared math visualizer.
math_visualizer = MathVisualizer()