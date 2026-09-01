# diagram_generator.py
"""
Educational diagram generator for the AI Teacher.

This module generates simple educational diagrams locally
using Graphviz when available.

It supports:

- Flowcharts
- Concept diagrams
- Process diagrams
- Relationship diagrams
- Simple labeled diagrams

The generated diagrams can be saved as PNG, SVG, or PDF.

Graphviz is optional. If it is not installed, the service
returns a structured diagram description that can be rendered
by another visual provider later.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Dict, List, Optional


class DiagramGenerator:
    """
    Generate educational diagrams.

    The generator is intentionally provider-independent and
    supports local Graphviz rendering.
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

    def generate(
        self,
        title: str,
        nodes: List[Dict[str, Any]],
        relationships: Optional[List[Dict[str, Any]]] = None,
        output_format: str = "png",
        filename: Optional[str] = None,
        direction: str = "TB",
    ) -> Dict[str, Any]:
        """
        Generate a diagram from nodes and relationships.

        Parameters
        ----------
        title:
            Diagram title.

        nodes:
            List of node dictionaries.

            Example:
                [
                    {
                        "id": "input",
                        "label": "Student Input"
                    },
                    {
                        "id": "ai",
                        "label": "AI Teacher"
                    }
                ]

        relationships:
            List of edge dictionaries.

            Example:
                [
                    {
                        "source": "input",
                        "target": "ai",
                        "label": "question"
                    }
                ]

        output_format:
            png, svg, or pdf.

        filename:
            Optional output filename.

        direction:
            Graph direction:
            TB = top to bottom
            LR = left to right
        """

        if not title.strip():
            raise ValueError(
                "Diagram title cannot be empty."
            )

        if not nodes:
            raise ValueError(
                "At least one diagram node is required."
            )

        output_format = output_format.lower().strip()

        if output_format not in {
            "png",
            "svg",
            "pdf",
        }:
            raise ValueError(
                "output_format must be png, svg, or pdf."
            )

        if direction not in {
            "TB",
            "BT",
            "LR",
            "RL",
        }:
            raise ValueError(
                "direction must be TB, BT, LR, or RL."
            )

        relationships = relationships or []

        safe_filename = self._safe_filename(
            filename or title
        )

        try:
            import graphviz
        except ImportError:
            return {
                "success": False,
                "rendered": False,
                "provider": "graphviz",
                "error": (
                    "Graphviz Python package is not installed."
                ),
                "diagram": self._build_description(
                    title,
                    nodes,
                    relationships,
                ),
            }

        graph = graphviz.Digraph(
            name="AI_Teacher_Diagram",
            format=output_format,
        )

        graph.attr(
            rankdir=direction,
            bgcolor="transparent",
            pad="0.3",
            nodesep="0.5",
            ranksep="0.6",
        )

        graph.attr(
            "node",
            shape="box",
            style="rounded",
            fontname="Arial",
            fontsize="12",
            margin="0.2,0.12",
        )

        graph.attr(
            "edge",
            fontname="Arial",
            fontsize="10",
        )

        for node in nodes:
            node_id = str(
                node.get("id", "")
            ).strip()

            label = str(
                node.get("label", node_id)
            ).strip()

            if not node_id:
                continue

            graph.node(
                self._escape_id(node_id),
                label=label,
            )

        for relationship in relationships:
            source = str(
                relationship.get("source", "")
            ).strip()

            target = str(
                relationship.get("target", "")
            ).strip()

            if not source or not target:
                continue

            label = str(
                relationship.get(
                    "label",
                    "",
                )
            ).strip()

            graph.edge(
                self._escape_id(source),
                self._escape_id(target),
                label=label,
            )

        output_base = self.output_directory / safe_filename

        try:
            rendered_path = graph.render(
                filename=str(output_base),
                cleanup=True,
            )

            return {
                "success": True,
                "rendered": True,
                "provider": "graphviz",
                "path": str(
                    Path(rendered_path)
                ),
                "format": output_format,
                "title": title,
                "node_count": len(nodes),
                "relationship_count": len(
                    relationships
                ),
            }

        except Exception as exc:
            return {
                "success": False,
                "rendered": False,
                "provider": "graphviz",
                "error": str(exc),
                "diagram": self._build_description(
                    title,
                    nodes,
                    relationships,
                ),
            }

    def generate_flowchart(
        self,
        title: str,
        steps: List[str],
        output_format: str = "png",
        filename: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Generate a simple top-to-bottom flowchart.
        """

        if not steps:
            raise ValueError(
                "At least one step is required."
            )

        nodes = []

        for index, step in enumerate(steps):
            nodes.append(
                {
                    "id": f"step_{index}",
                    "label": str(step),
                }
            )

        relationships = []

        for index in range(len(steps) - 1):
            relationships.append(
                {
                    "source": f"step_{index}",
                    "target": f"step_{index + 1}",
                }
            )

        return self.generate(
            title=title,
            nodes=nodes,
            relationships=relationships,
            output_format=output_format,
            filename=filename,
            direction="TB",
        )

    def generate_process_diagram(
        self,
        title: str,
        process_steps: List[Dict[str, Any]],
        output_format: str = "png",
        filename: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Generate a process diagram from structured steps.
        """

        nodes = []

        for index, step in enumerate(process_steps):
            if isinstance(step, dict):
                label = step.get(
                    "label",
                    step.get(
                        "name",
                        f"Step {index + 1}",
                    ),
                )
            else:
                label = str(step)

            nodes.append(
                {
                    "id": f"process_{index}",
                    "label": str(label),
                }
            )

        relationships = [
            {
                "source": f"process_{index}",
                "target": f"process_{index + 1}",
            }
            for index in range(
                len(nodes) - 1
            )
        ]

        return self.generate(
            title=title,
            nodes=nodes,
            relationships=relationships,
            output_format=output_format,
            filename=filename,
            direction="LR",
        )

    def generate_concept_map(
        self,
        title: str,
        concepts: List[Dict[str, Any]],
        relationships: List[Dict[str, Any]],
        output_format: str = "png",
        filename: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Generate a concept map.

        `concepts` should contain dictionaries with at least
        an `id` and `label`.
        """

        return self.generate(
            title=title,
            nodes=concepts,
            relationships=relationships,
            output_format=output_format,
            filename=filename,
            direction="LR",
        )

    def generate_comparison(
        self,
        title: str,
        left_title: str,
        right_title: str,
        left_items: List[str],
        right_items: List[str],
        output_format: str = "png",
        filename: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Generate a simple comparison diagram.
        """

        nodes = [
            {
                "id": "left",
                "label": self._format_list_node(
                    left_title,
                    left_items,
                ),
            },
            {
                "id": "right",
                "label": self._format_list_node(
                    right_title,
                    right_items,
                ),
            },
        ]

        relationships = [
            {
                "source": "left",
                "target": "right",
                "label": "compare",
            }
        ]

        return self.generate(
            title=title,
            nodes=nodes,
            relationships=relationships,
            output_format=output_format,
            filename=filename,
            direction="LR",
        )

    def create_mermaid_definition(
        self,
        nodes: List[Dict[str, Any]],
        relationships: Optional[
            List[Dict[str, Any]]
        ] = None,
        direction: str = "TD",
    ) -> str:
        """
        Create a Mermaid diagram definition.

        This is useful when the frontend wants to render
        diagrams directly in the browser.
        """

        relationships = relationships or []

        if direction not in {
            "TB",
            "TD",
            "BT",
            "LR",
            "RL",
        }:
            direction = "TD"

        lines = [
            f"flowchart {direction}"
        ]

        for node in nodes:
            node_id = self._escape_mermaid_id(
                str(
                    node.get(
                        "id",
                        "",
                    )
                )
            )

            label = str(
                node.get(
                    "label",
                    node_id,
                )
            ).replace(
                '"',
                "'",
            )

            if node_id:
                lines.append(
                    f'    {node_id}["{label}"]'
                )

        for relationship in relationships:
            source = self._escape_mermaid_id(
                str(
                    relationship.get(
                        "source",
                        "",
                    )
                )
            )

            target = self._escape_mermaid_id(
                str(
                    relationship.get(
                        "target",
                        "",
                    )
                )
            )

            label = str(
                relationship.get(
                    "label",
                    "",
                )
            ).replace(
                '"',
                "'",
            )

            if not source or not target:
                continue

            if label:
                lines.append(
                    f'    {source} -->|{label}| {target}'
                )
            else:
                lines.append(
                    f"    {source} --> {target}"
                )

        return "\n".join(lines)

    def _build_description(
        self,
        title: str,
        nodes: List[Dict[str, Any]],
        relationships: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """
        Build a provider-independent diagram description.
        """

        return {
            "title": title,
            "nodes": nodes,
            "relationships": relationships,
        }

    @staticmethod
    def _safe_filename(
        filename: str,
    ) -> str:
        """
        Convert a filename into a safe filesystem name.
        """

        filename = Path(filename).stem

        filename = re.sub(
            r"[^a-zA-Z0-9_-]+",
            "_",
            filename,
        )

        filename = filename.strip("_")

        return filename or "educational_diagram"

    @staticmethod
    def _escape_id(
        value: str,
    ) -> str:
        """
        Make a safe Graphviz node identifier.
        """

        return re.sub(
            r"[^a-zA-Z0-9_]",
            "_",
            value,
        )

    @staticmethod
    def _escape_mermaid_id(
        value: str,
    ) -> str:
        """
        Make a safe Mermaid node identifier.
        """

        value = re.sub(
            r"[^a-zA-Z0-9_]",
            "_",
            value,
        )

        if not value:
            return "node"

        if value[0].isdigit():
            return f"node_{value}"

        return value

    @staticmethod
    def _format_list_node(
        title: str,
        items: List[str],
    ) -> str:
        """
        Format comparison items into a readable diagram label.
        """

        lines = [title]

        for item in items:
            lines.append(
                f"- {item}"
            )

        return "\n".join(lines)


# Default shared diagram generator.
diagram_generator = DiagramGenerator()