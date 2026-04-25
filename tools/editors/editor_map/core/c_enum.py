"""
Parse C enum definitions from header files.

Supports:
- typedef enum Name { ... } Name;
- Sequential and explicit value assignments
- Alias assignments (Foo = Bar)
- GEN-LOGIC-BEGIN/END, GEN-NO-LOGIC-BEGIN/END, GEN-BEGIN/END markers
- Single-line // and multi-line /* */ comments
- Enum member names that do not match the typedef name
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Tuple


@dataclass
class CEnumMember:
    """A single member of a C enum."""
    name: str
    value: int
    # Which GEN region this member belongs to, if any
    gen_region: Optional[str] = None


@dataclass
class CEnum:
    """A parsed C enum."""
    name: str
    members: List[CEnumMember] = field(default_factory=list)
    # Map member name -> value for quick lookup
    member_map: Dict[str, int] = field(default_factory=dict)

    def get_value(self, member_name: str) -> Optional[int]:
        return self.member_map.get(member_name)

    def get_member(self, member_name: str) -> Optional[CEnumMember]:
        for m in self.members:
            if m.name == member_name:
                return m
        return None

    def get_members_in_region(self, region: str) -> List[CEnumMember]:
        return [m for m in self.members if m.gen_region == region]


def _strip_comments(source: str) -> str:
    """Remove C-style single-line and multi-line comments."""
    # Remove multi-line comments first
    source = re.sub(r'/\*.*?\*/', '', source, flags=re.DOTALL)
    # Remove single-line comments but preserve GEN markers
    lines = []
    for line in source.split('\n'):
        # Check if line has a GEN marker in a comment
        gen_match = re.search(
            r'//\s*(GEN(?:-\w+)?(?:-BEGIN|-END))', line)
        if gen_match:
            # Keep the GEN marker as a special token
            code_part = line[:line.index('//')]
            lines.append(code_part + '/*GEN:' + gen_match.group(1) + '*/')
        else:
            # Strip the comment entirely
            comment_idx = line.find('//')
            if comment_idx >= 0:
                line = line[:comment_idx]
            lines.append(line)
    return '\n'.join(lines)


def _extract_enum_body(source: str) -> List[Tuple[str, str]]:
    """
    Extract all typedef enum blocks from source.
    Returns list of (enum_name, enum_body) tuples.
    """
    results = []
    # Match: typedef enum OptionalTag { body } Name;
    pattern = re.compile(
        r'typedef\s+enum\s+\w*\s*\{([^}]*)\}\s*(\w+)\s*;',
        re.DOTALL
    )
    for match in pattern.finditer(source):
        body = match.group(1)
        name = match.group(2)
        results.append((name, body))
    return results


def _parse_enum_body(body: str) -> List[CEnumMember]:
    """Parse the body of an enum into members."""
    members: List[CEnumMember] = []
    member_values: Dict[str, int] = {}
    next_value = 0
    current_gen_region: Optional[str] = None

    # Split by commas, but handle the last entry which may not have a comma
    # First, extract GEN markers and interleave them
    tokens: List[str] = []
    for part in re.split(r',', body):
        part = part.strip()
        if part:
            tokens.append(part)

    for token in tokens:
        token = token.strip()
        if not token:
            continue

        # Check for GEN markers embedded as /*GEN:...*/ 
        gen_markers = re.findall(r'/\*GEN:([\w-]+)\*/', token)
        for marker in gen_markers:
            if marker.endswith('-BEGIN'):
                current_gen_region = marker
            elif marker.endswith('-END'):
                current_gen_region = None

        # Remove GEN marker tokens from the actual enum text
        token = re.sub(r'/\*GEN:[\w-]+\*/', '', token).strip()
        if not token:
            continue

        # Parse: NAME = VALUE  or  NAME = OTHER_NAME  or  NAME
        assign_match = re.match(
            r'(\w+)\s*=\s*(.+)', token)
        plain_match = re.match(r'(\w+)\s*$', token)

        if assign_match:
            name = assign_match.group(1).strip()
            value_expr = assign_match.group(2).strip()

            # Try as integer literal
            resolved = _try_resolve_value(value_expr, member_values)
            if resolved is not None:
                value = resolved
            else:
                # Skip unparseable entries
                continue

            members.append(CEnumMember(
                name=name, value=value,
                gen_region=current_gen_region))
            member_values[name] = value
            next_value = value + 1

        elif plain_match:
            name = plain_match.group(1).strip()
            # Skip if it looks like a type keyword
            if name in ('enum', 'typedef', 'struct'):
                continue
            value = next_value
            members.append(CEnumMember(
                name=name, value=value,
                gen_region=current_gen_region))
            member_values[name] = value
            next_value = value + 1

    return members


def _try_resolve_value(
        expr: str,
        known: Dict[str, int]) -> Optional[int]:
    """Try to resolve a value expression to an integer."""
    expr = expr.strip().rstrip(',').strip()

    # Direct integer literal (decimal)
    if re.match(r'^-?\d+$', expr):
        return int(expr)

    # Hex literal
    if re.match(r'^0[xX][0-9a-fA-F]+$', expr):
        return int(expr, 16)

    # Binary literal
    if re.match(r'^0[bB][01]+$', expr):
        return int(expr, 2)

    # BIT(n)
    bit_match = re.match(r'^BIT\((\d+)\)$', expr)
    if bit_match:
        return 1 << int(bit_match.group(1))

    # Reference to another enum member
    if expr in known:
        return known[expr]

    # Simple arithmetic: MEMBER + N or MEMBER - N
    arith_match = re.match(r'^(\w+)\s*([+-])\s*(\d+)$', expr)
    if arith_match:
        ref_name = arith_match.group(1)
        op = arith_match.group(2)
        operand = int(arith_match.group(3))
        if ref_name in known:
            if op == '+':
                return known[ref_name] + operand
            else:
                return known[ref_name] - operand

    return None


def parse_c_enum(source: str) -> List[CEnum]:
    """
    Parse all typedef enum declarations from C source text.
    Returns a list of CEnum objects.
    """
    cleaned = _strip_comments(source)
    raw_enums = _extract_enum_body(cleaned)

    results = []
    for name, body in raw_enums:
        members = _parse_enum_body(body)
        member_map = {m.name: m.value for m in members}
        results.append(CEnum(
            name=name,
            members=members,
            member_map=member_map))
    return results


def parse_c_enum_from_file(filepath: Path) -> List[CEnum]:
    """Parse all enums from a C header file."""
    source = filepath.read_text(encoding='utf-8', errors='replace')
    return parse_c_enum(source)


def find_enum_by_name(
        enums: List[CEnum],
        name: str) -> Optional[CEnum]:
    """Find an enum by its typedef name."""
    for e in enums:
        if e.name == name:
            return e
    return None
