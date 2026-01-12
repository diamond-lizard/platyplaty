"""Tests for indicator caching behavior."""

import tempfile
from pathlib import Path

import cachetools
import pytest

from platyplaty.ui.directory_types import EntryType
from platyplaty.ui.indicator_cache import refresh_indicator_cache
from platyplaty.ui.indicators import count_directory_contents, directory_count_cache
from platyplaty.ui.size_format import (
    file_size_cache,
    get_file_size,
    get_symlink_size,
    symlink_size_cache,
)


class TestCacheDecoratorsApplied:
    """Verify cachetools.cached decorators are properly applied."""

    def test_count_directory_contents_is_cached(self) -> None:
        """count_directory_contents should use directory_count_cache."""
        assert hasattr(count_directory_contents, "__wrapped__")
        # Check the cache type
        assert isinstance(directory_count_cache, cachetools.LRUCache)
        assert directory_count_cache.maxsize == 10000

    def test_get_file_size_is_cached(self) -> None:
        """get_file_size should use file_size_cache."""
        assert hasattr(get_file_size, "__wrapped__")
        assert isinstance(file_size_cache, cachetools.LRUCache)
        assert file_size_cache.maxsize == 10000

    def test_get_symlink_size_is_cached(self) -> None:
        """get_symlink_size should use symlink_size_cache."""
        assert hasattr(get_symlink_size, "__wrapped__")
        assert isinstance(symlink_size_cache, cachetools.LRUCache)
        assert symlink_size_cache.maxsize == 10000


class TestRefreshIndicatorCache:
    """Test refresh_indicator_cache invalidates and recalculates."""

    def test_refresh_directory_invalidates_and_recalculates(
        self, tmp_path: Path
    ) -> None:
        """Refreshing directory should clear cache and recalculate count."""
        # Create a directory with files
        subdir = tmp_path / "subdir"
        subdir.mkdir()
        (subdir / "file.milk").touch()

        # First call caches the result
        count1 = count_directory_contents(subdir)
        assert count1 == 1

        # Add another file
        (subdir / "file2.milk").touch()

        # Cached result should still be 1
        count2 = count_directory_contents(subdir)
        assert count2 == 1

        # Refresh should invalidate and recalculate
        refresh_indicator_cache(EntryType.DIRECTORY, subdir)

        # Now should see updated count
        count3 = count_directory_contents(subdir)
        assert count3 == 2

    def test_refresh_file_invalidates_file_size_cache(
        self, tmp_path: Path
    ) -> None:
        """Refreshing file should clear file_size_cache."""
        test_file = tmp_path / "test.milk"
        test_file.write_text("hello")

        # First call caches the size
        size1 = get_file_size(test_file)
        assert size1 == 5

        # Modify the file
        test_file.write_text("hello world")

        # Cached result should still be 5
        size2 = get_file_size(test_file)
        assert size2 == 5

        # Refresh should invalidate and recalculate
        refresh_indicator_cache(EntryType.FILE, test_file)

        # Now should see updated size
        size3 = get_file_size(test_file)
        assert size3 == 11
