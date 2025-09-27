"""
RNet Metadata System
Comprehensive metadata management for RNet files with tracking, versioning, and custom fields
"""

import json
import uuid
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, field, asdict
from enum import Enum
import hashlib
import copy
from flask import current_app, g
from flask_login import current_user


class MetadataScope(Enum):
    """Scope of metadata field"""
    SYSTEM = "system"           # System-managed metadata
    USER = "user"               # User-editable metadata
    CUSTOM = "custom"           # Custom application metadata
    INTERNAL = "internal"       # Internal processing metadata


class MetadataType(Enum):
    """Type of metadata value"""
    STRING = "string"
    INTEGER = "integer"
    FLOAT = "float"
    BOOLEAN = "boolean"
    DATETIME = "datetime"
    LIST = "list"
    OBJECT = "object"
    FILE_REFERENCE = "file_ref"


class MetadataAccessLevel(Enum):
    """Access level for metadata fields"""
    PUBLIC = "public"           # Visible to all users
    PROTECTED = "protected"     # Visible to authorized users
    PRIVATE = "private"         # Visible to owner only
    SYSTEM = "system"           # System access only


@dataclass
class MetadataField:
    """Definition of a metadata field"""
    name: str
    display_name: str
    description: str
    field_type: MetadataType
    scope: MetadataScope
    access_level: MetadataAccessLevel
    required: bool = False
    default_value: Any = None
    validation_rules: Dict[str, Any] = field(default_factory=dict)
    indexable: bool = False
    versioned: bool = True
    
    def validate_value(self, value: Any) -> Tuple[bool, Optional[str]]:
        """Validate a value against this field definition"""
        if value is None:
            if self.required:
                return False, f"Field {self.name} is required"
            return True, None
        
        # Type validation
        if self.field_type == MetadataType.STRING and not isinstance(value, str):
            return False, f"Field {self.name} must be a string"
        elif self.field_type == MetadataType.INTEGER and not isinstance(value, int):
            return False, f"Field {self.name} must be an integer"
        elif self.field_type == MetadataType.FLOAT and not isinstance(value, (int, float)):
            return False, f"Field {self.name} must be a number"
        elif self.field_type == MetadataType.BOOLEAN and not isinstance(value, bool):
            return False, f"Field {self.name} must be a boolean"
        elif self.field_type == MetadataType.LIST and not isinstance(value, list):
            return False, f"Field {self.name} must be a list"
        elif self.field_type == MetadataType.OBJECT and not isinstance(value, dict):
            return False, f"Field {self.name} must be an object"
        
        # Custom validation rules
        rules = self.validation_rules
        
        if 'min_length' in rules and isinstance(value, str) and len(value) < rules['min_length']:
            return False, f"Field {self.name} must be at least {rules['min_length']} characters"
        
        if 'max_length' in rules and isinstance(value, str) and len(value) > rules['max_length']:
            return False, f"Field {self.name} must be no more than {rules['max_length']} characters"
        
        if 'pattern' in rules and isinstance(value, str):
            import re
            if not re.match(rules['pattern'], value):
                return False, f"Field {self.name} does not match required pattern"
        
        if 'allowed_values' in rules and value not in rules['allowed_values']:
            return False, f"Field {self.name} must be one of: {', '.join(map(str, rules['allowed_values']))}"
        
        return True, None


@dataclass
class MetadataVersion:
    """Version of metadata at a point in time"""
    version_id: str
    timestamp: str
    changed_by: str
    changes: Dict[str, Any]
    change_reason: Optional[str] = None
    checksum: Optional[str] = None


@dataclass
class RNetMetadata:
    """Complete metadata structure for RNet files"""
    # Core identification
    file_id: str
    filename: str
    file_type: str
    format_version: str
    
    # Timestamps
    created_at: str
    modified_at: str
    accessed_at: Optional[str] = None
    
    # Authorship
    created_by: str
    modified_by: str
    
    # Content metadata
    title: Optional[str] = None
    description: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    categories: List[str] = field(default_factory=list)
    keywords: List[str] = field(default_factory=list)
    
    # File properties
    file_size: Optional[int] = None
    checksum: Optional[str] = None
    encoding: str = "utf-8"
    compression: Optional[str] = None
    
    # Version tracking
    version: str = "1.0.0"
    version_history: List[MetadataVersion] = field(default_factory=list)
    
    # Relations
    parent_file_id: Optional[str] = None
    derived_from: List[str] = field(default_factory=list)
    related_files: List[str] = field(default_factory=list)
    
    # Usage tracking
    access_count: int = 0
    download_count: int = 0
    share_count: int = 0
    
    # Custom metadata
    custom_fields: Dict[str, Any] = field(default_factory=dict)
    
    # System metadata
    system_metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Access control
    permissions: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'RNetMetadata':
        """Create from dictionary"""
        # Handle version_history conversion
        version_history = []
        for vh_data in data.get('version_history', []):
            if isinstance(vh_data, dict):
                version_history.append(MetadataVersion(**vh_data))
            else:
                version_history.append(vh_data)
        
        data_copy = data.copy()
        data_copy['version_history'] = version_history
        
        return cls(**data_copy)


class RNetMetadataManager:
    """Manager for RNet file metadata operations"""
    
    def __init__(self):
        self.field_definitions = self._initialize_field_definitions()
        self.indexable_fields = [name for name, field_def in self.field_definitions.items() if field_def.indexable]
    
    def create_metadata(
        self,
        filename: str,
        file_type: str = "simulation",
        created_by: Optional[str] = None,
        title: Optional[str] = None,
        description: Optional[str] = None,
        tags: Optional[List[str]] = None,
        custom_fields: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> RNetMetadata:
        """
        Create new metadata instance
        
        Args:
            filename: Name of the file
            file_type: Type of RNet file
            created_by: User who created the file
            title: Display title
            description: File description
            tags: List of tags
            custom_fields: Custom metadata fields
            **kwargs: Additional metadata fields
        
        Returns:
            RNetMetadata instance
        """
        # Get current user if available
        if not created_by and hasattr(current_user, 'username'):
            created_by = current_user.username
        elif not created_by:
            created_by = "system"
        
        now = datetime.now(timezone.utc).isoformat()
        file_id = str(uuid.uuid4())
        
        metadata = RNetMetadata(
            file_id=file_id,
            filename=filename,
            file_type=file_type,
            format_version="2.0",
            created_at=now,
            modified_at=now,
            created_by=created_by,
            modified_by=created_by,
            title=title,
            description=description,
            tags=tags or [],
            custom_fields=custom_fields or {},
            **kwargs
        )
        
        # Add initial version
        self._add_version_entry(metadata, "created", created_by, "Initial file creation")
        
        return metadata
    
    def update_metadata(
        self,
        metadata: RNetMetadata,
        updates: Dict[str, Any],
        modified_by: Optional[str] = None,
        change_reason: Optional[str] = None
    ) -> RNetMetadata:
        """
        Update metadata with change tracking
        
        Args:
            metadata: Current metadata
            updates: Dictionary of fields to update
            modified_by: User making the change
            change_reason: Reason for the change
        
        Returns:
            Updated metadata
        """
        # Get current user if available
        if not modified_by and hasattr(current_user, 'username'):
            modified_by = current_user.username
        elif not modified_by:
            modified_by = "system"
        
        # Validate updates
        validation_errors = self.validate_metadata_updates(updates)
        if validation_errors:
            raise ValueError(f"Validation failed: {'; '.join(validation_errors)}")
        
        # Track changes
        changes = {}
        old_values = {}
        
        for field, new_value in updates.items():
            if hasattr(metadata, field):
                old_value = getattr(metadata, field)
                if old_value != new_value:
                    old_values[field] = old_value
                    changes[field] = {
                        'old': old_value,
                        'new': new_value
                    }
                    setattr(metadata, field, new_value)
            elif field in ['custom_fields', 'system_metadata']:
                # Handle nested updates
                target_dict = getattr(metadata, field)
                for sub_field, sub_value in new_value.items():
                    if target_dict.get(sub_field) != sub_value:
                        old_values[f"{field}.{sub_field}"] = target_dict.get(sub_field)
                        changes[f"{field}.{sub_field}"] = {
                            'old': target_dict.get(sub_field),
                            'new': sub_value
                        }
                        target_dict[sub_field] = sub_value
        
        if changes:
            # Update modification timestamp
            metadata.modified_at = datetime.now(timezone.utc).isoformat()
            metadata.modified_by = modified_by
            
            # Add version entry
            self._add_version_entry(metadata, changes, modified_by, change_reason)
        
        return metadata
    
    def validate_metadata(self, metadata: RNetMetadata) -> Tuple[bool, List[str]]:
        """
        Validate complete metadata against field definitions
        
        Args:
            metadata: Metadata to validate
        
        Returns:
            Tuple of (is_valid, error_messages)
        """
        errors = []
        metadata_dict = metadata.to_dict()
        
        # Validate defined fields
        for field_name, field_def in self.field_definitions.items():
            value = metadata_dict.get(field_name)
            
            is_valid, error = field_def.validate_value(value)
            if not is_valid:
                errors.append(error)
        
        # Validate custom fields if they have definitions
        custom_fields = metadata.custom_fields
        for field_name, value in custom_fields.items():
            if field_name in self.field_definitions:
                field_def = self.field_definitions[field_name]
                is_valid, error = field_def.validate_value(value)
                if not is_valid:
                    errors.append(f"Custom field validation: {error}")
        
        return len(errors) == 0, errors
    
    def validate_metadata_updates(self, updates: Dict[str, Any]) -> List[str]:
        """Validate metadata updates before applying"""
        errors = []
        
        for field_name, value in updates.items():
            if field_name in self.field_definitions:
                field_def = self.field_definitions[field_name]
                is_valid, error = field_def.validate_value(value)
                if not is_valid:
                    errors.append(error)
        
        return errors
    
    def search_metadata(
        self,
        metadata_list: List[RNetMetadata],
        query: str = None,
        filters: Dict[str, Any] = None,
        sort_by: str = "modified_at",
        sort_desc: bool = True,
        limit: Optional[int] = None
    ) -> List[RNetMetadata]:
        """
        Search and filter metadata
        
        Args:
            metadata_list: List of metadata to search
            query: Text query to search in searchable fields
            filters: Filters to apply (field_name: value)
            sort_by: Field to sort by
            sort_desc: Sort in descending order
            limit: Maximum number of results
        
        Returns:
            Filtered and sorted metadata list
        """
        results = metadata_list.copy()
        
        # Apply text query
        if query:
            query_lower = query.lower()
            searchable_fields = ['title', 'description', 'filename', 'tags', 'keywords']
            
            filtered_results = []
            for metadata in results:
                metadata_dict = metadata.to_dict()
                found = False
                
                for field in searchable_fields:
                    value = metadata_dict.get(field)
                    if value:
                        if isinstance(value, str) and query_lower in value.lower():
                            found = True
                            break
                        elif isinstance(value, list):
                            for item in value:
                                if isinstance(item, str) and query_lower in item.lower():
                                    found = True
                                    break
                            if found:
                                break
                
                if found:
                    filtered_results.append(metadata)
            
            results = filtered_results
        
        # Apply filters
        if filters:
            for filter_field, filter_value in filters.items():
                filtered_results = []
                
                for metadata in results:
                    metadata_dict = metadata.to_dict()
                    
                    # Handle nested field access
                    if '.' in filter_field:
                        field_parts = filter_field.split('.')
                        current_value = metadata_dict
                        
                        try:
                            for part in field_parts:
                                current_value = current_value[part]
                            
                            if current_value == filter_value:
                                filtered_results.append(metadata)
                        except (KeyError, TypeError):
                            # Field not found or wrong type
                            pass
                    else:
                        # Direct field access
                        if metadata_dict.get(filter_field) == filter_value:
                            filtered_results.append(metadata)
                
                results = filtered_results
        
        # Sort results
        if sort_by:
            try:
                results.sort(
                    key=lambda m: getattr(m, sort_by) or '',
                    reverse=sort_desc
                )
            except AttributeError:
                # Fallback to dict access for custom fields
                results.sort(
                    key=lambda m: m.to_dict().get(sort_by, ''),
                    reverse=sort_desc
                )
        
        # Apply limit
        if limit and limit > 0:
            results = results[:limit]
        
        return results
    
    def get_metadata_summary(self, metadata: RNetMetadata) -> Dict[str, Any]:
        """Get summary information about metadata"""
        return {
            'file_id': metadata.file_id,
            'filename': metadata.filename,
            'file_type': metadata.file_type,
            'title': metadata.title,
            'created_at': metadata.created_at,
            'modified_at': metadata.modified_at,
            'created_by': metadata.created_by,
            'version': metadata.version,
            'tags_count': len(metadata.tags),
            'custom_fields_count': len(metadata.custom_fields),
            'version_history_count': len(metadata.version_history),
            'file_size': metadata.file_size,
            'access_count': metadata.access_count
        }
    
    def calculate_metadata_checksum(self, metadata: RNetMetadata) -> str:
        """Calculate checksum for metadata"""
        # Create a deterministic representation for checksumming
        checksum_data = {
            'file_id': metadata.file_id,
            'filename': metadata.filename,
            'created_at': metadata.created_at,
            'created_by': metadata.created_by,
            'title': metadata.title,
            'description': metadata.description,
            'tags': sorted(metadata.tags) if metadata.tags else [],
            'custom_fields': metadata.custom_fields
        }
        
        content_str = json.dumps(checksum_data, sort_keys=True, ensure_ascii=False)
        return hashlib.sha256(content_str.encode('utf-8')).hexdigest()
    
    def increment_access_count(self, metadata: RNetMetadata, access_type: str = "view") -> RNetMetadata:
        """Increment access counter"""
        now = datetime.now(timezone.utc).isoformat()
        metadata.accessed_at = now
        
        if access_type == "view":
            metadata.access_count += 1
        elif access_type == "download":
            metadata.download_count += 1
        elif access_type == "share":
            metadata.share_count += 1
        
        return metadata
    
    def merge_metadata(
        self,
        base_metadata: RNetMetadata,
        incoming_metadata: RNetMetadata,
        merge_strategy: str = "prefer_incoming"
    ) -> RNetMetadata:
        """
        Merge two metadata objects
        
        Args:
            base_metadata: Base metadata object
            incoming_metadata: Incoming metadata to merge
            merge_strategy: Strategy for handling conflicts
        
        Returns:
            Merged metadata
        """
        merged = copy.deepcopy(base_metadata)
        incoming_dict = incoming_metadata.to_dict()
        
        merge_fields = ['title', 'description', 'tags', 'categories', 'keywords']
        
        for field in merge_fields:
            incoming_value = getattr(incoming_metadata, field, None)
            base_value = getattr(base_metadata, field, None)
            
            if incoming_value is not None:
                if merge_strategy == "prefer_incoming":
                    setattr(merged, field, incoming_value)
                elif merge_strategy == "merge_lists" and isinstance(incoming_value, list):
                    # Merge lists and remove duplicates
                    combined = list(base_value or [])
                    for item in incoming_value:
                        if item not in combined:
                            combined.append(item)
                    setattr(merged, field, combined)
        
        # Merge custom fields
        if incoming_metadata.custom_fields:
            merged.custom_fields.update(incoming_metadata.custom_fields)
        
        return merged
    
    def _initialize_field_definitions(self) -> Dict[str, MetadataField]:
        """Initialize standard metadata field definitions"""
        return {
            'file_id': MetadataField(
                name='file_id',
                display_name='File ID',
                description='Unique identifier for the file',
                field_type=MetadataType.STRING,
                scope=MetadataScope.SYSTEM,
                access_level=MetadataAccessLevel.PROTECTED,
                required=True,
                indexable=True
            ),
            'filename': MetadataField(
                name='filename',
                display_name='File Name',
                description='Name of the file',
                field_type=MetadataType.STRING,
                scope=MetadataScope.USER,
                access_level=MetadataAccessLevel.PUBLIC,
                required=True,
                validation_rules={'min_length': 1, 'max_length': 255},
                indexable=True
            ),
            'title': MetadataField(
                name='title',
                display_name='Title',
                description='Display title for the file',
                field_type=MetadataType.STRING,
                scope=MetadataScope.USER,
                access_level=MetadataAccessLevel.PUBLIC,
                validation_rules={'max_length': 200},
                indexable=True
            ),
            'description': MetadataField(
                name='description',
                display_name='Description',
                description='Detailed description of the file',
                field_type=MetadataType.STRING,
                scope=MetadataScope.USER,
                access_level=MetadataAccessLevel.PUBLIC,
                validation_rules={'max_length': 2000},
                indexable=True
            ),
            'tags': MetadataField(
                name='tags',
                display_name='Tags',
                description='List of tags for categorization',
                field_type=MetadataType.LIST,
                scope=MetadataScope.USER,
                access_level=MetadataAccessLevel.PUBLIC,
                indexable=True
            ),
            'created_by': MetadataField(
                name='created_by',
                display_name='Created By',
                description='User who created the file',
                field_type=MetadataType.STRING,
                scope=MetadataScope.SYSTEM,
                access_level=MetadataAccessLevel.PROTECTED,
                required=True,
                indexable=True
            ),
            'file_type': MetadataField(
                name='file_type',
                display_name='File Type',
                description='Type of RNet file',
                field_type=MetadataType.STRING,
                scope=MetadataScope.SYSTEM,
                access_level=MetadataAccessLevel.PUBLIC,
                required=True,
                validation_rules={'allowed_values': ['simulation', 'topology', 'scenario', 'template']},
                indexable=True
            ),
            'version': MetadataField(
                name='version',
                display_name='Version',
                description='File version using semantic versioning',
                field_type=MetadataType.STRING,
                scope=MetadataScope.SYSTEM,
                access_level=MetadataAccessLevel.PROTECTED,
                validation_rules={'pattern': r'^\d+\.\d+\.\d+.*$'},
                indexable=True
            )
        }
    
    def _add_version_entry(
        self,
        metadata: RNetMetadata,
        changes: Union[str, Dict[str, Any]],
        changed_by: str,
        change_reason: Optional[str] = None
    ):
        """Add a version entry to metadata history"""
        version_id = str(uuid.uuid4())
        timestamp = datetime.now(timezone.utc).isoformat()
        
        if isinstance(changes, str):
            # Simple string change type (like "created")
            changes_dict = {'action': changes}
        else:
            changes_dict = changes
        
        version_entry = MetadataVersion(
            version_id=version_id,
            timestamp=timestamp,
            changed_by=changed_by,
            changes=changes_dict,
            change_reason=change_reason,
            checksum=self.calculate_metadata_checksum(metadata)
        )
        
        metadata.version_history.append(version_entry)


# Utility functions
def create_rnet_metadata(filename: str, **kwargs) -> RNetMetadata:
    """Convenience function for creating metadata"""
    manager = RNetMetadataManager()
    return manager.create_metadata(filename, **kwargs)


def update_rnet_metadata(metadata: RNetMetadata, updates: Dict[str, Any], **kwargs) -> RNetMetadata:
    """Convenience function for updating metadata"""
    manager = RNetMetadataManager()
    return manager.update_metadata(metadata, updates, **kwargs)


def validate_rnet_metadata(metadata: RNetMetadata) -> Tuple[bool, List[str]]:
    """Convenience function for metadata validation"""
    manager = RNetMetadataManager()
    return manager.validate_metadata(metadata)