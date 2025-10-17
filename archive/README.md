# RiddleNet Archive Directory

This directory contains **693 files** that were moved from the root workspace during the October 15, 2025 cleanup. All files are preserved for historical reference and potential future use.

## Directory Structure

### 📄 documentation/
Contains ~650 Markdown files documenting features, fixes, and implementations:
- Implementation guides
- Fix summaries
- Testing checklists
- Visual references
- Quick start guides
- Before/after comparisons

**Naming Patterns:**
- `ACHIEVEMENT_*` - Achievement system docs
- `CHALLENGE_*` - Challenge feature docs  
- `COLLABORATION_*` - Collaboration system docs
- `DASHBOARD_*` - Dashboard implementation docs
- `MVP_*` - MVP implementation notes (300+ files)
- And many more...

### 🔄 migration_scripts/
Database migration and setup scripts (~20 files):
- `create_challenge_progress_table.py`
- `create_lobby_tables.py`
- `migrate_challenge_badges.py`
- `migrate_challenge_progress.py`
- `migrate_lobbies_to_db.py`
- `migrate_unlock_system.py`

**Note:** These scripts were used during initial development and deployment. They may need modification if used again.

### 🐛 debug_scripts/
Development and diagnostic scripts (~15 files):
- `check_production_blueprint.py` - Blueprint verification
- `check_user_progress.py` - User progress diagnostics
- `debug_stats.py` - Statistics debugging
- `diagnose_unlock_issue.py` - Unlock system diagnostics
- `verify_blueprint.py` - Blueprint validation
- `verify_route_fixes.py` - Route verification

**Note:** These scripts are standalone and can be run independently for debugging.

### 🧪 test_files/
Test HTML, JavaScript, and debug files (~8 files):
- `test_api_endpoint.py` - API testing
- `test_collaboration.html` - Collaboration feature tests
- `test_db_connection.py` - Database connection tests
- `test_session_security.py` - Session security tests
- `fix_data_sync.html` - Data sync debugging
- `temp_validate.js` - Temporary validation script
- `*_debug.txt` - Debug log files

**Note:** Test files may require setup/configuration to run.

## Why Were These Files Archived?

1. **Documentation Overload**: 650+ MD files cluttered the root directory
2. **Development Artifacts**: Migration and debug scripts no longer needed in root
3. **Better Organization**: Easier to navigate core application code
4. **Faster Performance**: Reduced IDE indexing time
5. **Cleaner Deployments**: Smaller deployment packages

## When to Reference These Files

### Documentation Files
- Understanding implementation decisions
- Learning about feature evolution
- Finding testing procedures
- Reviewing visual design changes

### Migration Scripts
- Rolling back database changes
- Understanding schema evolution
- Setting up new environments from scratch

### Debug Scripts
- Troubleshooting production issues
- Analyzing user data
- Verifying system integrity
- Performance diagnostics

### Test Files
- Setting up integration tests
- Understanding API contracts
- Debugging collaboration features
- Session security testing

## How to Use Archived Files

### Viewing Documentation
```bash
# Search for specific topic
cd archive/documentation
dir *CHALLENGE* /b

# Open in editor
code MVP_IMPLEMENTATION_SUMMARY.md
```

### Running Migration Scripts
```bash
# Copy to project root if needed
copy archive\migration_scripts\migrate_lobbies_to_db.py .

# Run with caution (may modify database)
python migrate_lobbies_to_db.py
```

### Using Debug Scripts
```bash
# Run debug scripts from archive
python archive\debug_scripts\check_user_progress.py

# Or copy to root first
copy archive\debug_scripts\* .
```

### Accessing Test Files
```bash
# Open test HTML files
start archive\test_files\test_collaboration.html

# Run test scripts
python archive\test_files\test_api_endpoint.py
```

## Important Notes

### ⚠️ Warnings

1. **Database Migrations**: Migration scripts may modify your database. Always backup first.
2. **Dependencies**: Some scripts may require specific environment setup or dependencies.
3. **Outdated Code**: Some files may reference code that has been refactored or removed.
4. **Path Issues**: Scripts may need path adjustments to work from archive location.

### ✅ Safe to Use

- Documentation files (read-only reference)
- Debug scripts (diagnostic only, don't modify data)
- Test HTML files (for manual testing)

### ⚠️ Use with Caution

- Migration scripts (can modify database)
- Test Python scripts (may need configuration)
- Scripts that write to database or files

## File Naming Conventions

### Documentation
- `*_IMPLEMENTATION.md` - Implementation guides
- `*_FIX.md` / `*_FIX_SUMMARY.md` - Bug fixes
- `*_QUICK_REFERENCE.md` - Quick reference guides
- `*_TESTING_GUIDE.md` - Testing procedures
- `*_VISUAL_*.md` - Visual diagrams and references
- `*_BEFORE_AFTER.md` - Before/after comparisons
- `MVP_*.md` - Minimum viable product implementations

### Scripts
- `create_*.py` - Table creation scripts
- `migrate_*.py` - Data migration scripts
- `check_*.py` - Verification scripts
- `debug_*.py` - Debugging utilities
- `diagnose_*.py` - Diagnostic tools
- `verify_*.py` - Validation scripts
- `test_*.py` - Test scripts

## Statistics

| Category | Count | Total Size |
|----------|-------|------------|
| Documentation | ~650 files | ~25 MB |
| Migration Scripts | ~20 files | ~500 KB |
| Debug Scripts | ~15 files | ~300 KB |
| Test Files | ~8 files | ~200 KB |
| **Total** | **693 files** | **~26 MB** |

## Search Tips

### Find Documentation by Topic
```bash
# Windows Command Prompt
cd archive\documentation
dir *TOPOLOGY* /b
dir *SIMULATION* /b
dir *CHALLENGE* /b

# PowerShell
Get-ChildItem archive\documentation -Filter "*TOPOLOGY*"
```

### Find All MVP Files
```bash
dir archive\documentation\MVP_*.md /b
# Returns ~300 MVP implementation files
```

### Search File Contents
```bash
# Windows findstr
findstr /s /i "lobby" archive\documentation\*.md

# PowerShell
Select-String -Path archive\documentation\*.md -Pattern "lobby"
```

## Restoration

If you need to restore files to root:

```bash
# Restore specific file
copy archive\documentation\SPECIFIC_FILE.md .

# Restore category
copy archive\migration_scripts\*.py .

# Restore all (not recommended)
xcopy archive\* . /s /y
```

## Contact

For questions about archived files:
1. Check `WORKSPACE_CLEANUP_SUMMARY.md` in root directory
2. Review Git commit history for when file was active
3. Contact development team if file is needed for active development

---

**Archive Created:** October 15, 2025  
**Total Files:** 693  
**Purpose:** Workspace organization and cleanup  
**Safe to Delete:** No - keep for reference
