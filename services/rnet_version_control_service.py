"""
RNet Version Control System
Advanced version control for RNet files with semantic versioning and change tracking
"""

import json
import uuid
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass, field, asdict
from enum import Enum
import difflib
import copy
import hashlib
import semver
from flask import current_app
from flask_login import current_user

from .rnet_metadata_service import RNetMetadata, RNetMetadataManager


class ChangeType(Enum):
    """Types of changes in version control"""
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    RESTORE = "restore"
    MERGE = "merge"
    BRANCH = "branch"
    TAG = "tag"


class VersionBumpType(Enum):
    """Types of version bumps following semantic versioning"""
    MAJOR = "major"     # Breaking changes
    MINOR = "minor"     # New features, backward compatible
    PATCH = "patch"     # Bug fixes, backward compatible
    PRERELEASE = "prerelease"  # Pre-release versions


class MergeStrategy(Enum):
    """Strategies for merging versions"""
    PREFER_NEWER = "prefer_newer"
    PREFER_OLDER = "prefer_older"
    MANUAL = "manual"
    THREE_WAY = "three_way"


@dataclass
class ChangeRecord:
    """Record of a specific change"""
    change_id: str
    timestamp: str
    change_type: ChangeType
    field_path: str
    old_value: Any
    new_value: Any
    changed_by: str
    change_reason: Optional[str] = None


@dataclass
class VersionInfo:
    """Information about a specific version"""
    version: str
    commit_id: str
    timestamp: str
    author: str
    message: str
    parent_versions: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    changes: List[ChangeRecord] = field(default_factory=list)
    checksum: str = ""
    metadata_checksum: str = ""
    is_stable: bool = False
    is_archived: bool = False


@dataclass
class VersionBranch:
    """A version control branch"""
    branch_name: str
    created_at: str
    created_by: str
    head_version: str
    base_version: str
    description: Optional[str] = None
    is_protected: bool = False
    merge_count: int = 0


@dataclass
class VersionGraph:
    """Complete version history graph"""
    file_id: str
    current_version: str
    versions: Dict[str, VersionInfo] = field(default_factory=dict)
    branches: Dict[str, VersionBranch] = field(default_factory=dict)
    tags: Dict[str, str] = field(default_factory=dict)  # tag_name -> version
    head_versions: Dict[str, str] = field(default_factory=dict)  # branch -> version


class RNetVersionControl:
    """Advanced version control system for RNet files"""
    
    def __init__(self):
        self.metadata_manager = RNetMetadataManager()
        
    def initialize_version_control(
        self,
        rnet_data: Dict[str, Any],
        initial_message: str = "Initial version",
        author: Optional[str] = None
    ) -> VersionGraph:
        """
        Initialize version control for a new RNet file
        
        Args:
            rnet_data: RNet file data
            initial_message: Commit message for initial version
            author: Author of initial version
        
        Returns:
            VersionGraph with initial version
        """
        author = author or self._get_current_user()
        file_id = rnet_data.get('metadata', {}).get('file_id', str(uuid.uuid4()))
        
        # Create initial version info
        commit_id = str(uuid.uuid4())
        timestamp = datetime.now(timezone.utc).isoformat()
        
        initial_version = VersionInfo(
            version="1.0.0",
            commit_id=commit_id,
            timestamp=timestamp,
            author=author,
            message=initial_message,
            parent_versions=[],
            tags=["initial"],
            changes=[],
            checksum=self._calculate_content_checksum(rnet_data),
            metadata_checksum=self._calculate_metadata_checksum(rnet_data.get('metadata', {})),
            is_stable=True
        )
        
        # Create main branch
        main_branch = VersionBranch(
            branch_name="main",
            created_at=timestamp,
            created_by=author,
            head_version="1.0.0",
            base_version="1.0.0",
            description="Main development branch",
            is_protected=True
        )
        
        # Create version graph
        version_graph = VersionGraph(
            file_id=file_id,
            current_version="1.0.0",
            versions={"1.0.0": initial_version},
            branches={"main": main_branch},
            tags={"initial": "1.0.0", "v1.0.0": "1.0.0"},
            head_versions={"main": "1.0.0"}
        )
        
        return version_graph
    
    def create_version(
        self,
        version_graph: VersionGraph,
        rnet_data: Dict[str, Any],
        previous_data: Dict[str, Any],
        bump_type: VersionBumpType = VersionBumpType.PATCH,
        message: str = "Version update",
        author: Optional[str] = None,
        branch_name: str = "main"
    ) -> Tuple[VersionGraph, str]:
        """
        Create a new version with change tracking
        
        Args:
            version_graph: Current version graph
            rnet_data: New RNet file data
            previous_data: Previous RNet file data for comparison
            bump_type: Type of version bump
            message: Commit message
            author: Author of changes
            branch_name: Branch to commit to
        
        Returns:
            Updated version graph and new version string
        """
        author = author or self._get_current_user()
        
        # Calculate new version number
        current_version = version_graph.head_versions.get(branch_name, "1.0.0")
        new_version = self._bump_version(current_version, bump_type)
        
        # Detect changes
        changes = self._detect_changes(previous_data, rnet_data, author)
        
        # Create new version info
        commit_id = str(uuid.uuid4())
        timestamp = datetime.now(timezone.utc).isoformat()
        
        version_info = VersionInfo(
            version=new_version,
            commit_id=commit_id,
            timestamp=timestamp,
            author=author,
            message=message,
            parent_versions=[current_version],
            tags=[],
            changes=changes,
            checksum=self._calculate_content_checksum(rnet_data),
            metadata_checksum=self._calculate_metadata_checksum(rnet_data.get('metadata', {})),
            is_stable=bump_type != VersionBumpType.PRERELEASE
        )
        
        # Update version graph
        version_graph.versions[new_version] = version_info
        version_graph.head_versions[branch_name] = new_version
        version_graph.current_version = new_version
        
        # Update branch head
        if branch_name in version_graph.branches:
            version_graph.branches[branch_name].head_version = new_version
        
        return version_graph, new_version
    
    def create_branch(
        self,
        version_graph: VersionGraph,
        branch_name: str,
        base_version: Optional[str] = None,
        description: Optional[str] = None,
        author: Optional[str] = None
    ) -> VersionGraph:
        """
        Create a new branch from a specific version
        
        Args:
            version_graph: Current version graph
            branch_name: Name of new branch
            base_version: Version to branch from (defaults to current)
            description: Branch description
            author: Author creating the branch
        
        Returns:
            Updated version graph
        """
        author = author or self._get_current_user()
        base_version = base_version or version_graph.current_version
        
        if branch_name in version_graph.branches:
            raise ValueError(f"Branch '{branch_name}' already exists")
        
        if base_version not in version_graph.versions:
            raise ValueError(f"Base version '{base_version}' not found")
        
        timestamp = datetime.now(timezone.utc).isoformat()
        
        branch = VersionBranch(
            branch_name=branch_name,
            created_at=timestamp,
            created_by=author,
            head_version=base_version,
            base_version=base_version,
            description=description
        )
        
        version_graph.branches[branch_name] = branch
        version_graph.head_versions[branch_name] = base_version
        
        return version_graph
    
    def merge_branches(
        self,
        version_graph: VersionGraph,
        source_branch: str,
        target_branch: str,
        rnet_data: Dict[str, Any],
        source_data: Dict[str, Any],
        target_data: Dict[str, Any],
        merge_strategy: MergeStrategy = MergeStrategy.THREE_WAY,
        message: str = None,
        author: Optional[str] = None
    ) -> Tuple[VersionGraph, str, Dict[str, Any]]:
        """
        Merge two branches
        
        Args:
            version_graph: Current version graph
            source_branch: Source branch to merge from
            target_branch: Target branch to merge into
            rnet_data: Merged RNet data
            source_data: Source branch data
            target_data: Target branch data
            merge_strategy: Strategy for handling conflicts
            message: Merge commit message
            author: Author of merge
        
        Returns:
            Updated version graph, merge version, and merged data
        """
        author = author or self._get_current_user()
        message = message or f"Merge {source_branch} into {target_branch}"
        
        if source_branch not in version_graph.branches:
            raise ValueError(f"Source branch '{source_branch}' not found")
        
        if target_branch not in version_graph.branches:
            raise ValueError(f"Target branch '{target_branch}' not found")
        
        source_version = version_graph.head_versions[source_branch]
        target_version = version_graph.head_versions[target_branch]
        
        # Create merge version
        new_version = self._bump_version(target_version, VersionBumpType.MINOR)
        
        # Detect merge changes
        merge_changes = self._detect_merge_changes(source_data, target_data, rnet_data, author)
        
        # Create merge commit
        commit_id = str(uuid.uuid4())
        timestamp = datetime.now(timezone.utc).isoformat()
        
        merge_version_info = VersionInfo(
            version=new_version,
            commit_id=commit_id,
            timestamp=timestamp,
            author=author,
            message=message,
            parent_versions=[source_version, target_version],
            tags=["merge"],
            changes=merge_changes,
            checksum=self._calculate_content_checksum(rnet_data),
            metadata_checksum=self._calculate_metadata_checksum(rnet_data.get('metadata', {})),
            is_stable=True
        )
        
        # Update version graph
        version_graph.versions[new_version] = merge_version_info
        version_graph.head_versions[target_branch] = new_version
        version_graph.current_version = new_version
        
        # Update target branch
        version_graph.branches[target_branch].head_version = new_version
        version_graph.branches[target_branch].merge_count += 1
        
        return version_graph, new_version, rnet_data
    
    def create_tag(
        self,
        version_graph: VersionGraph,
        tag_name: str,
        version: Optional[str] = None,
        author: Optional[str] = None
    ) -> VersionGraph:
        """
        Create a tag for a specific version
        
        Args:
            version_graph: Current version graph
            tag_name: Name of the tag
            version: Version to tag (defaults to current)
            author: Author creating the tag
        
        Returns:
            Updated version graph
        """
        author = author or self._get_current_user()
        version = version or version_graph.current_version
        
        if tag_name in version_graph.tags:
            raise ValueError(f"Tag '{tag_name}' already exists")
        
        if version not in version_graph.versions:
            raise ValueError(f"Version '{version}' not found")
        
        version_graph.tags[tag_name] = version
        version_graph.versions[version].tags.append(tag_name)
        
        return version_graph
    
    def get_version_history(
        self,
        version_graph: VersionGraph,
        branch_name: Optional[str] = None,
        max_count: Optional[int] = None
    ) -> List[VersionInfo]:
        """
        Get version history for a branch or entire graph
        
        Args:
            version_graph: Version graph
            branch_name: Branch to get history for (None for all)
            max_count: Maximum number of versions to return
        
        Returns:
            List of version info sorted by timestamp
        """
        if branch_name and branch_name in version_graph.head_versions:
            # Get history for specific branch
            versions = self._get_branch_history(version_graph, branch_name)
        else:
            # Get all versions
            versions = list(version_graph.versions.values())
        
        # Sort by timestamp (newest first)
        versions.sort(key=lambda v: v.timestamp, reverse=True)
        
        if max_count:
            versions = versions[:max_count]
        
        return versions
    
    def get_version_diff(
        self,
        version_graph: VersionGraph,
        version1: str,
        version2: str
    ) -> Dict[str, Any]:
        """
        Get differences between two versions
        
        Args:
            version_graph: Version graph
            version1: First version
            version2: Second version
        
        Returns:
            Dictionary containing diff information
        """
        if version1 not in version_graph.versions:
            raise ValueError(f"Version '{version1}' not found")
        
        if version2 not in version_graph.versions:
            raise ValueError(f"Version '{version2}' not found")
        
        v1_info = version_graph.versions[version1]
        v2_info = version_graph.versions[version2]
        
        # Collect changes between versions
        changes_between = []
        
        # Find path from version1 to version2
        path = self._find_version_path(version_graph, version1, version2)
        
        for version in path[1:]:  # Skip first version
            version_info = version_graph.versions[version]
            changes_between.extend(version_info.changes)
        
        return {
            'version1': version1,
            'version2': version2,
            'timestamp1': v1_info.timestamp,
            'timestamp2': v2_info.timestamp,
            'author1': v1_info.author,
            'author2': v2_info.author,
            'changes': changes_between,
            'checksum_diff': v1_info.checksum != v2_info.checksum,
            'version_path': path
        }
    
    def rollback_to_version(
        self,
        version_graph: VersionGraph,
        target_version: str,
        author: Optional[str] = None
    ) -> Tuple[VersionGraph, str]:
        """
        Rollback to a specific version
        
        Args:
            version_graph: Current version graph
            target_version: Version to rollback to
            author: Author performing rollback
        
        Returns:
            Updated version graph and new rollback version
        """
        author = author or self._get_current_user()
        
        if target_version not in version_graph.versions:
            raise ValueError(f"Target version '{target_version}' not found")
        
        current_version = version_graph.current_version
        new_version = self._bump_version(current_version, VersionBumpType.PATCH)
        
        # Create rollback commit
        commit_id = str(uuid.uuid4())
        timestamp = datetime.now(timezone.utc).isoformat()
        
        rollback_change = ChangeRecord(
            change_id=str(uuid.uuid4()),
            timestamp=timestamp,
            change_type=ChangeType.RESTORE,
            field_path="*",
            old_value=current_version,
            new_value=target_version,
            changed_by=author,
            change_reason=f"Rollback to version {target_version}"
        )
        
        rollback_version_info = VersionInfo(
            version=new_version,
            commit_id=commit_id,
            timestamp=timestamp,
            author=author,
            message=f"Rollback to version {target_version}",
            parent_versions=[current_version],
            tags=["rollback"],
            changes=[rollback_change],
            checksum=version_graph.versions[target_version].checksum,
            metadata_checksum=version_graph.versions[target_version].metadata_checksum,
            is_stable=True
        )
        
        # Update version graph
        version_graph.versions[new_version] = rollback_version_info
        version_graph.current_version = new_version
        
        return version_graph, new_version
    
    def get_version_statistics(self, version_graph: VersionGraph) -> Dict[str, Any]:
        """Get statistics about the version graph"""
        total_versions = len(version_graph.versions)
        total_branches = len(version_graph.branches)
        total_tags = len(version_graph.tags)
        
        # Count change types
        change_counts = {}
        total_changes = 0
        
        for version_info in version_graph.versions.values():
            total_changes += len(version_info.changes)
            for change in version_info.changes:
                change_type = change.change_type.value
                change_counts[change_type] = change_counts.get(change_type, 0) + 1
        
        # Get authors
        authors = set()
        for version_info in version_graph.versions.values():
            authors.add(version_info.author)
        
        # Find oldest and newest versions
        versions_by_time = sorted(version_graph.versions.values(), key=lambda v: v.timestamp)
        oldest_version = versions_by_time[0] if versions_by_time else None
        newest_version = versions_by_time[-1] if versions_by_time else None
        
        return {
            'file_id': version_graph.file_id,
            'current_version': version_graph.current_version,
            'total_versions': total_versions,
            'total_branches': total_branches,
            'total_tags': total_tags,
            'total_changes': total_changes,
            'change_type_counts': change_counts,
            'unique_authors': len(authors),
            'authors': list(authors),
            'oldest_version': oldest_version.version if oldest_version else None,
            'oldest_timestamp': oldest_version.timestamp if oldest_version else None,
            'newest_version': newest_version.version if newest_version else None,
            'newest_timestamp': newest_version.timestamp if newest_version else None,
            'branches': list(version_graph.branches.keys()),
            'tags': list(version_graph.tags.keys())
        }
    
    def _get_current_user(self) -> str:
        """Get current user or fallback"""
        try:
            if hasattr(current_user, 'username'):
                return current_user.username
        except:
            pass
        return "system"
    
    def _bump_version(self, current_version: str, bump_type: VersionBumpType) -> str:
        """Bump version using semantic versioning"""
        try:
            if bump_type == VersionBumpType.MAJOR:
                return semver.bump_major(current_version)
            elif bump_type == VersionBumpType.MINOR:
                return semver.bump_minor(current_version)
            elif bump_type == VersionBumpType.PATCH:
                return semver.bump_patch(current_version)
            elif bump_type == VersionBumpType.PRERELEASE:
                return semver.bump_prerelease(current_version)
        except:
            # Fallback if semver parsing fails
            parts = current_version.split('.')
            if len(parts) < 3:
                parts.extend(['0'] * (3 - len(parts)))
            
            major, minor, patch = int(parts[0]), int(parts[1]), int(parts[2])
            
            if bump_type == VersionBumpType.MAJOR:
                return f"{major + 1}.0.0"
            elif bump_type == VersionBumpType.MINOR:
                return f"{major}.{minor + 1}.0"
            else:  # PATCH
                return f"{major}.{minor}.{patch + 1}"
    
    def _detect_changes(
        self,
        old_data: Dict[str, Any],
        new_data: Dict[str, Any],
        author: str
    ) -> List[ChangeRecord]:
        """Detect changes between two data structures"""
        changes = []
        timestamp = datetime.now(timezone.utc).isoformat()
        
        # Deep comparison function
        def compare_values(old_val: Any, new_val: Any, path: str):
            if old_val != new_val:
                change_id = str(uuid.uuid4())
                
                # Determine change type
                if old_val is None and new_val is not None:
                    change_type = ChangeType.CREATE
                elif old_val is not None and new_val is None:
                    change_type = ChangeType.DELETE
                else:
                    change_type = ChangeType.UPDATE
                
                change = ChangeRecord(
                    change_id=change_id,
                    timestamp=timestamp,
                    change_type=change_type,
                    field_path=path,
                    old_value=old_val,
                    new_value=new_val,
                    changed_by=author
                )
                changes.append(change)
        
        # Compare recursively
        self._deep_compare(old_data, new_data, "", compare_values)
        
        return changes
    
    def _detect_merge_changes(
        self,
        source_data: Dict[str, Any],
        target_data: Dict[str, Any],
        merged_data: Dict[str, Any],
        author: str
    ) -> List[ChangeRecord]:
        """Detect changes from a merge operation"""
        # For merge changes, we compare the merged result with both sources
        source_changes = self._detect_changes(target_data, merged_data, author)
        
        # Mark all changes as merge type
        for change in source_changes:
            change.change_type = ChangeType.MERGE
            change.change_reason = "Merge operation"
        
        return source_changes
    
    def _deep_compare(self, old_obj: Any, new_obj: Any, path: str, callback):
        """Deep compare two objects and call callback for differences"""
        if isinstance(old_obj, dict) and isinstance(new_obj, dict):
            # Compare dictionaries
            all_keys = set(old_obj.keys()) | set(new_obj.keys())
            
            for key in all_keys:
                new_path = f"{path}.{key}" if path else key
                old_val = old_obj.get(key)
                new_val = new_obj.get(key)
                
                if isinstance(old_val, (dict, list)) and isinstance(new_val, (dict, list)):
                    self._deep_compare(old_val, new_val, new_path, callback)
                else:
                    callback(old_val, new_val, new_path)
        
        elif isinstance(old_obj, list) and isinstance(new_obj, list):
            # Compare lists
            max_len = max(len(old_obj), len(new_obj))
            
            for i in range(max_len):
                new_path = f"{path}[{i}]"
                old_val = old_obj[i] if i < len(old_obj) else None
                new_val = new_obj[i] if i < len(new_obj) else None
                
                if isinstance(old_val, (dict, list)) and isinstance(new_val, (dict, list)):
                    self._deep_compare(old_val, new_val, new_path, callback)
                else:
                    callback(old_val, new_val, new_path)
        
        else:
            # Direct comparison
            callback(old_obj, new_obj, path)
    
    def _calculate_content_checksum(self, data: Dict[str, Any]) -> str:
        """Calculate checksum for content"""
        # Remove metadata and version control info for content checksum
        content_data = data.get('content', data)
        content_str = json.dumps(content_data, sort_keys=True, ensure_ascii=False)
        return hashlib.sha256(content_str.encode('utf-8')).hexdigest()
    
    def _calculate_metadata_checksum(self, metadata: Dict[str, Any]) -> str:
        """Calculate checksum for metadata"""
        metadata_str = json.dumps(metadata, sort_keys=True, ensure_ascii=False)
        return hashlib.sha256(metadata_str.encode('utf-8')).hexdigest()
    
    def _get_branch_history(self, version_graph: VersionGraph, branch_name: str) -> List[VersionInfo]:
        """Get version history for a specific branch"""
        versions = []
        current_version = version_graph.head_versions.get(branch_name)
        
        while current_version:
            if current_version in version_graph.versions:
                version_info = version_graph.versions[current_version]
                versions.append(version_info)
                
                # Get parent version (first parent for linear history)
                if version_info.parent_versions:
                    current_version = version_info.parent_versions[0]
                else:
                    current_version = None
            else:
                break
        
        return versions
    
    def _find_version_path(
        self,
        version_graph: VersionGraph,
        start_version: str,
        end_version: str
    ) -> List[str]:
        """Find path between two versions"""
        # Simple implementation - find common ancestor and build path
        # This is a simplified version; a full implementation would use graph algorithms
        
        # For now, return direct path if one is parent of the other
        start_info = version_graph.versions.get(start_version)
        end_info = version_graph.versions.get(end_version)
        
        if not start_info or not end_info:
            return [start_version, end_version]
        
        # Check if end is descendant of start
        current = end_version
        path = [current]
        
        while current and current != start_version:
            current_info = version_graph.versions.get(current)
            if current_info and current_info.parent_versions:
                current = current_info.parent_versions[0]  # Follow first parent
                path.append(current)
            else:
                break
        
        if current == start_version:
            path.reverse()
            return path
        
        # If no direct path found, return both versions
        return [start_version, end_version]


# Utility functions
def initialize_rnet_version_control(rnet_data: Dict[str, Any], **kwargs) -> VersionGraph:
    """Convenience function for initializing version control"""
    vc = RNetVersionControl()
    return vc.initialize_version_control(rnet_data, **kwargs)


def create_rnet_version(version_graph: VersionGraph, rnet_data: Dict[str, Any], previous_data: Dict[str, Any], **kwargs) -> Tuple[VersionGraph, str]:
    """Convenience function for creating versions"""
    vc = RNetVersionControl()
    return vc.create_version(version_graph, rnet_data, previous_data, **kwargs)