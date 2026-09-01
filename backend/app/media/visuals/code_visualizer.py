# code_visualizer.py
"""
Code visualization utilities for the AI Teacher.

This module converts source code into educational visual
representations that help students understand:

- Code structure
- Execution flow
- Functions
- Conditions
- Loops
- Variables
- Algorithms

The implementation is intentionally local and lightweight.
It can produce Mermaid flowcharts and structured analysis
without requiring a paid API.
"""

from __future__ import annotations

import ast
import re
from dataclasses import dataclass, asdict
from typing import Any, Dict, List, Optional


@dataclass
class CodeNode:
    """
    Represents one element in a code visualization.
    """

    id: str
    label: str
    node_type: str
    line: Optional[int] = None


@dataclass
class CodeEdge:
    """
    Represents a relationship between code elements.
    """

    source: str
    target: str
    label: str = ""


class CodeVisualizer:
    """
    Analyze source code and create educational visualizations.

    Python code receives deeper AST-based analysis.
    Other languages receive a lightweight text-based analysis.
    """

    SUPPORTED_LANGUAGES = {
        "python",
        "javascript",
        "typescript",
        "java",
        "cpp",
        "c",
        "c++",
        "javascriptreact",
        "typescriptreact",
    }

    def analyze(
        self,
        code: str,
        language: str = "python",
    ) -> Dict[str, Any]:
        """
        Analyze source code and return a structured representation.
        """

        if not code or not code.strip():
            raise ValueError("Code cannot be empty.")

        language = self._normalize_language(language)

        if language == "python":
            return self._analyze_python(code)

        return self._analyze_generic(
            code,
            language,
        )

    def visualize(
        self,
        code: str,
        language: str = "python",
        direction: str = "TD",
    ) -> Dict[str, Any]:
        """
        Analyze code and return a Mermaid-compatible flowchart.
        """

        analysis = self.analyze(
            code,
            language,
        )

        nodes = analysis["nodes"]
        edges = analysis["edges"]

        mermaid = self._build_mermaid(
            nodes,
            edges,
            direction=direction,
        )

        return {
            "language": language,
            "mermaid": mermaid,
            "nodes": nodes,
            "edges": edges,
            "summary": analysis["summary"],
            "constructs": analysis["constructs"],
        }

    def explain_structure(
        self,
        code: str,
        language: str = "python",
    ) -> Dict[str, Any]:
        """
        Return a simplified explanation of the code structure.
        """

        analysis = self.analyze(
            code,
            language,
        )

        explanation = []

        for node in analysis["nodes"]:
            node_type = node["node_type"]
            label = node["label"]

            if node_type == "function":
                explanation.append(
                    f"Function: {label}"
                )

            elif node_type == "class":
                explanation.append(
                    f"Class: {label}"
                )

            elif node_type == "condition":
                explanation.append(
                    f"Condition: {label}"
                )

            elif node_type == "loop":
                explanation.append(
                    f"Loop: {label}"
                )

            elif node_type == "return":
                explanation.append(
                    f"Return: {label}"
                )

            elif node_type == "assignment":
                explanation.append(
                    f"Variable assignment: {label}"
                )

            elif node_type == "call":
                explanation.append(
                    f"Function call: {label}"
                )

            else:
                explanation.append(label)

        return {
            "language": language,
            "summary": analysis["summary"],
            "constructs": analysis["constructs"],
            "explanation": explanation,
        }

    def create_execution_flow(
        self,
        code: str,
        language: str = "python",
    ) -> Dict[str, Any]:
        """
        Create a simplified execution-flow representation.
        """

        analysis = self.analyze(
            code,
            language,
        )

        nodes = analysis["nodes"]
        edges = analysis["edges"]

        return {
            "nodes": nodes,
            "edges": edges,
            "mermaid": self._build_mermaid(
                nodes,
                edges,
                direction="TD",
            ),
        }

    def _analyze_python(
        self,
        code: str,
    ) -> Dict[str, Any]:
        """
        Analyze Python source code using the AST module.
        """

        try:
            tree = ast.parse(code)
        except SyntaxError as exc:
            return {
                "nodes": [],
                "edges": [],
                "summary": (
                    f"Python syntax error on line "
                    f"{exc.lineno}: {exc.msg}"
                ),
                "constructs": {
                    "functions": 0,
                    "classes": 0,
                    "conditions": 0,
                    "loops": 0,
                    "assignments": 0,
                    "calls": 0,
                    "returns": 0,
                },
                "syntax_error": {
                    "line": exc.lineno,
                    "column": exc.offset,
                    "message": exc.msg,
                },
            }

        nodes: List[CodeNode] = []
        edges: List[CodeEdge] = []

        constructs = {
            "functions": 0,
            "classes": 0,
            "conditions": 0,
            "loops": 0,
            "assignments": 0,
            "calls": 0,
            "returns": 0,
        }

        counter = 0

        def new_id(prefix: str) -> str:
            nonlocal counter

            counter += 1
            return f"{prefix}_{counter}"

        previous_id: Optional[str] = None

        for statement in tree.body:
            node_id = self._python_statement_node(
                statement,
                nodes,
                constructs,
                new_id,
            )

            if node_id:
                if previous_id:
                    edges.append(
                        CodeEdge(
                            source=previous_id,
                            target=node_id,
                        )
                    )

                previous_id = node_id

        self._add_nested_python_nodes(
            tree,
            nodes,
            edges,
            constructs,
            new_id,
        )

        summary = self._python_summary(
            constructs,
            len(nodes),
        )

        return {
            "nodes": [
                asdict(node)
                for node in nodes
            ],
            "edges": [
                asdict(edge)
                for edge in edges
            ],
            "summary": summary,
            "constructs": constructs,
        }

    def _python_statement_node(
        self,
        statement: ast.stmt,
        nodes: List[CodeNode],
        constructs: Dict[str, int],
        new_id,
    ) -> Optional[str]:
        """
        Convert a top-level Python statement into a visualization node.
        """

        line = getattr(
            statement,
            "lineno",
            None,
        )

        if isinstance(
            statement,
            (
                ast.FunctionDef,
                ast.AsyncFunctionDef,
            ),
        ):
            constructs["functions"] += 1

            node_id = new_id("function")

            nodes.append(
                CodeNode(
                    id=node_id,
                    label=f"Function: {statement.name}",
                    node_type="function",
                    line=line,
                )
            )

            return node_id

        if isinstance(statement, ast.ClassDef):
            constructs["classes"] += 1

            node_id = new_id("class")

            nodes.append(
                CodeNode(
                    id=node_id,
                    label=f"Class: {statement.name}",
                    node_type="class",
                    line=line,
                )
            )

            return node_id

        if isinstance(statement, ast.If):
            constructs["conditions"] += 1

            node_id = new_id("condition")

            nodes.append(
                CodeNode(
                    id=node_id,
                    label="Condition: if",
                    node_type="condition",
                    line=line,
                )
            )

            return node_id

        if isinstance(
            statement,
            (
                ast.For,
                ast.While,
            ),
        ):
            constructs["loops"] += 1

            node_id = new_id("loop")

            loop_type = (
                "for"
                if isinstance(statement, ast.For)
                else "while"
            )

            nodes.append(
                CodeNode(
                    id=node_id,
                    label=f"Loop: {loop_type}",
                    node_type="loop",
                    line=line,
                )
            )

            return node_id

        if isinstance(statement, ast.Assign):
            constructs["assignments"] += 1

            node_id = new_id("assignment")

            target_names = []

            for target in statement.targets:
                target_names.extend(
                    self._extract_target_names(target)
                )

            label = (
                "Assignment: "
                + ", ".join(target_names)
                if target_names
                else "Assignment"
            )

            nodes.append(
                CodeNode(
                    id=node_id,
                    label=label,
                    node_type="assignment",
                    line=line,
                )
            )

            return node_id

        if isinstance(statement, ast.AnnAssign):
            constructs["assignments"] += 1

            node_id = new_id("assignment")

            target = self._extract_target_names(
                statement.target
            )

            label = (
                "Assignment: "
                + ", ".join(target)
                if target
                else "Assignment"
            )

            nodes.append(
                CodeNode(
                    id=node_id,
                    label=label,
                    node_type="assignment",
                    line=line,
                )
            )

            return node_id

        if isinstance(statement, ast.Return):
            constructs["returns"] += 1

            node_id = new_id("return")

            nodes.append(
                CodeNode(
                    id=node_id,
                    label="Return",
                    node_type="return",
                    line=line,
                )
            )

            return node_id

        if isinstance(statement, ast.Expr):
            if isinstance(
                statement.value,
                ast.Call,
            ):
                constructs["calls"] += 1

                node_id = new_id("call")

                call_name = self._get_call_name(
                    statement.value
                )

                nodes.append(
                    CodeNode(
                        id=node_id,
                        label=f"Call: {call_name}",
                        node_type="call",
                        line=line,
                    )
                )

                return node_id

        node_id = new_id("statement")

        nodes.append(
            CodeNode(
                id=node_id,
                label=type(statement).__name__,
                node_type="statement",
                line=line,
            )
        )

        return node_id

    def _add_nested_python_nodes(
        self,
        tree: ast.AST,
        nodes: List[CodeNode],
        edges: List[CodeEdge],
        constructs: Dict[str, int],
        new_id,
    ) -> None:
        """
        Add important nested Python constructs.

        Nested nodes are connected to their containing
        function/class/condition where possible.
        """

        parent_stack: List[str] = []

        for parent in ast.walk(tree):
            if not isinstance(
                parent,
                (
                    ast.FunctionDef,
                    ast.AsyncFunctionDef,
                    ast.ClassDef,
                ),
            ):
                continue

            parent_name = getattr(
                parent,
                "name",
                type(parent).__name__,
            )

            parent_node = next(
                (
                    node
                    for node in nodes
                    if node.label.endswith(
                        f": {parent_name}"
                    )
                ),
                None,
            )

            if parent_node:
                parent_stack.append(
                    parent_node.id
                )

            for child in getattr(
                parent,
                "body",
                [],
            ):
                if isinstance(
                    child,
                    (
                        ast.If,
                        ast.For,
                        ast.While,
                    ),
                ):
                    node_id = new_id("nested")

                    if isinstance(
                        child,
                        ast.If,
                    ):
                        node_type = "condition"
                        label = "Condition: if"
                        constructs["conditions"] += 1

                    else:
                        node_type = "loop"
                        loop_name = (
                            "for"
                            if isinstance(
                                child,
                                ast.For,
                            )
                            else "while"
                        )
                        label = f"Loop: {loop_name}"
                        constructs["loops"] += 1

                    nodes.append(
                        CodeNode(
                            id=node_id,
                            label=label,
                            node_type=node_type,
                            line=getattr(
                                child,
                                "lineno",
                                None,
                            ),
                        )
                    )

                    if parent_node:
                        edges.append(
                            CodeEdge(
                                source=parent_node.id,
                                target=node_id,
                                label="contains",
                            )
                        )

            if parent_node and parent_stack:
                parent_stack.pop()

    def _analyze_generic(
        self,
        code: str,
        language: str,
    ) -> Dict[str, Any]:
        """
        Lightweight analyzer for non-Python languages.
        """

        nodes: List[Dict[str, Any]] = []
        edges: List[Dict[str, Any]] = []

        lines = code.splitlines()

        constructs = {
            "functions": 0,
            "classes": 0,
            "conditions": 0,
            "loops": 0,
            "assignments": 0,
            "calls": 0,
            "returns": 0,
        }

        previous_id: Optional[str] = None
        counter = 0

        for line_number, line in enumerate(
            lines,
            start=1,
        ):
            stripped = line.strip()

            if not stripped:
                continue

            node_type = "statement"
            label = stripped[:80]

            if self._looks_like_function(
                stripped,
                language,
            ):
                node_type = "function"
                constructs["functions"] += 1

            elif self._looks_like_class(
                stripped,
                language,
            ):
                node_type = "class"
                constructs["classes"] += 1

            elif self._looks_like_condition(
                stripped,
            ):
                node_type = "condition"
                constructs["conditions"] += 1

            elif self._looks_like_loop(
                stripped,
            ):
                node_type = "loop"
                constructs["loops"] += 1

            elif self._looks_like_return(
                stripped,
            ):
                node_type = "return"
                constructs["returns"] += 1

            elif self._looks_like_assignment(
                stripped,
            ):
                node_type = "assignment"
                constructs["assignments"] += 1

            counter += 1
            node_id = f"node_{counter}"

            nodes.append(
                {
                    "id": node_id,
                    "label": label,
                    "node_type": node_type,
                    "line": line_number,
                }
            )

            if previous_id:
                edges.append(
                    {
                        "source": previous_id,
                        "target": node_id,
                        "label": "",
                    }
                )

            previous_id = node_id

        return {
            "nodes": nodes,
            "edges": edges,
            "summary": (
                f"Analyzed {len(nodes)} significant "
                f"code statements in {language}."
            ),
            "constructs": constructs,
        }

    def _build_mermaid(
        self,
        nodes: List[Dict[str, Any]],
        edges: List[Dict[str, Any]],
        direction: str = "TD",
    ) -> str:
        """
        Convert visualization data into Mermaid flowchart syntax.
        """

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
            node_id = self._safe_id(
                node["id"]
            )

            label = str(
                node.get(
                    "label",
                    "",
                )
            ).replace(
                '"',
                "'",
            )

            node_type = node.get(
                "node_type",
                "statement",
            )

            if node_type == "condition":
                lines.append(
                    f'    {node_id}{{"{label}"}}'
                )

            elif node_type == "function":
                lines.append(
                    f'    {node_id}(["{label}"])'
                )

            elif node_type == "return":
                lines.append(
                    f'    {node_id}(["{label}"])'
                )

            else:
                lines.append(
                    f'    {node_id}["{label}"]'
                )

        for edge in edges:
            source = self._safe_id(
                edge.get(
                    "source",
                    "",
                )
            )

            target = self._safe_id(
                edge.get(
                    "target",
                    "",
                )
            )

            label = str(
                edge.get(
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
                    f"    {source} -->|{label}| {target}"
                )
            else:
                lines.append(
                    f"    {source} --> {target}"
                )

        return "\n".join(lines)

    @staticmethod
    def _extract_target_names(
        target: ast.AST,
    ) -> List[str]:
        """
        Extract variable names from Python assignment targets.
        """

        if isinstance(
            target,
            ast.Name,
        ):
            return [target.id]

        if isinstance(
            target,
            (ast.Tuple, ast.List),
        ):
            names = []

            for element in target.elts:
                names.extend(
                    CodeVisualizer._extract_target_names(
                        element
                    )
                )

            return names

        return []

    @staticmethod
    def _get_call_name(
        node: ast.Call,
    ) -> str:
        """
        Get a readable function-call name.
        """

        function = node.func

        if isinstance(
            function,
            ast.Name,
        ):
            return function.id

        if isinstance(
            function,
            ast.Attribute,
        ):
            return function.attr

        return "function"

    @staticmethod
    def _python_summary(
        constructs: Dict[str, int],
        node_count: int,
    ) -> str:
        """
        Create a concise Python code summary.
        """

        parts = []

        if constructs["classes"]:
            parts.append(
                f"{constructs['classes']} class(es)"
            )

        if constructs["functions"]:
            parts.append(
                f"{constructs['functions']} function(s)"
            )

        if constructs["conditions"]:
            parts.append(
                f"{constructs['conditions']} condition(s)"
            )

        if constructs["loops"]:
            parts.append(
                f"{constructs['loops']} loop(s)"
            )

        if constructs["assignments"]:
            parts.append(
                f"{constructs['assignments']} assignment(s)"
            )

        if constructs["returns"]:
            parts.append(
                f"{constructs['returns']} return(s)"
            )

        if not parts:
            return (
                f"Analyzed {node_count} Python statement(s)."
            )

        return (
            "Python code contains "
            + ", ".join(parts)
            + "."
        )

    @staticmethod
    def _normalize_language(
        language: str,
    ) -> str:
        """
        Normalize language names.
        """

        language = (
            language
            .strip()
            .lower()
        )

        aliases = {
            "py": "python",
            "js": "javascript",
            "ts": "typescript",
            "jsx": "javascriptreact",
            "tsx": "typescriptreact",
            "cxx": "cpp",
        }

        return aliases.get(
            language,
            language,
        )

    @staticmethod
    def _safe_id(
        value: str,
    ) -> str:
        """
        Create a Mermaid-safe identifier.
        """

        value = re.sub(
            r"[^a-zA-Z0-9_]",
            "_",
            str(value),
        )

        if not value:
            return "node"

        if value[0].isdigit():
            return f"node_{value}"

        return value

    @staticmethod
    def _looks_like_function(
        line: str,
        language: str,
    ) -> bool:
        """
        Detect common function declarations.
        """

        if language == "javascript":
            return bool(
                re.search(
                    r"\bfunction\s+\w+\s*\(",
                    line,
                )
            ) or "=>" in line

        if language == "typescript":
            return bool(
                re.search(
                    r"\bfunction\s+\w+\s*\(",
                    line,
                )
            ) or "=>" in line

        if language in {
            "java",
            "c",
            "cpp",
            "c++",
        }:
            return bool(
                re.search(
                    r"\w+\s+\w+\s*\([^)]*\)\s*\{?",
                    line,
                )
            )

        return False

    @staticmethod
    def _looks_like_class(
        line: str,
        language: str,
    ) -> bool:
        """
        Detect common class declarations.
        """

        if language in {
            "javascript",
            "typescript",
            "javascriptreact",
            "typescriptreact",
            "java",
            "c",
            "cpp",
            "c++",
        }:
            return bool(
                re.search(
                    r"\bclass\s+\w+",
                    line,
                )
            )

        return False

    @staticmethod
    def _looks_like_condition(
        line: str,
    ) -> bool:
        """
        Detect common conditional statements.
        """

        return bool(
            re.match(
                r"^(if|else\s+if|elif|else)\b",
                line,
                flags=re.IGNORECASE,
            )
        )

    @staticmethod
    def _looks_like_loop(
        line: str,
    ) -> bool:
        """
        Detect common loop statements.
        """

        return bool(
            re.match(
                r"^(for|while|do)\b",
                line,
                flags=re.IGNORECASE,
            )
        )

    @staticmethod
    def _looks_like_return(
        line: str,
    ) -> bool:
        """
        Detect return statements.
        """

        return bool(
            re.match(
                r"^return\b",
                line,
                flags=re.IGNORECASE,
            )
        )

    @staticmethod
    def _looks_like_assignment(
        line: str,
    ) -> bool:
        """
        Detect basic variable assignments.
        """

        return bool(
            re.match(
                r"^[A-Za-z_]\w*\s*=",
                line,
            )
        )


# Default shared code visualizer.
code_visualizer = CodeVisualizer()