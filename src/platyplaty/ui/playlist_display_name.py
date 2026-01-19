"""Display name computation for playlist entries."""

from pathlib import Path


def compute_display_names(presets: list[Path]) -> list[str]:
    """Compute display names for all presets in a playlist.

    For entries with the same basename but different full paths,
    parent directories up to the first difference are shown.
    Entries with identical full paths show just the filename.
    """
    if not presets:
        return []
    basenames = [p.name for p in presets]
    basename_counts = _count_basenames(basenames)
    return [
        _compute_single_name(presets, i, basenames[i], basename_counts)
        for i in range(len(presets))
    ]


def _count_basenames(basenames: list[str]) -> dict[str, int]:
    """Count occurrences of each basename."""
    counts: dict[str, int] = {}
    for name in basenames:
        counts[name] = counts.get(name, 0) + 1
    return counts


def _compute_single_name(
    presets: list[Path],
    index: int,
    basename: str,
    counts: dict[str, int],
) -> str:
    """Compute display name for a single preset."""
    if counts.get(basename, 0) <= 1:
        return basename
    return _disambiguate_name(presets, index, basename)


def _disambiguate_name(presets: list[Path], index: int, basename: str) -> str:
    """Find minimum path prefix to disambiguate this preset."""
    current_path = presets[index]
    same_basename_paths = [p for p in presets if p.name == basename]
    if len(set(same_basename_paths)) == 1:
        return basename
    return _find_unique_suffix(current_path, same_basename_paths)


def _find_unique_suffix(current: Path, others: list[Path]) -> str:
    """Find the shortest suffix that makes current unique among others."""
    parts = current.parts
    for depth in range(1, len(parts)):
        suffix = "/".join(parts[-depth - 1 :])
        if _is_unique_suffix(suffix, current, others):
            return suffix
    return str(current)


def _is_unique_suffix(suffix: str, current: Path, others: list[Path]) -> bool:
    """Check if suffix uniquely identifies current among others."""
    return sum(1 for p in others if str(p).endswith(suffix)) == 1
