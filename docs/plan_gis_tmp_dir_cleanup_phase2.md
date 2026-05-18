# Plan: GIS_TMP_DIR Cleanup — Phase 2

## Background

Phase 1 (committed to branch `working-cleanup-GIS_WORK_DIR`) addressed:
- `GIS_WORK_DIR` leaks: `work_dir` and `decompressed_dir` cleaned up inside all 5 conversion
  functions in `govapp/gis/conversions.py` via `try/finally`
- `GIS_TMP_DIR` leaks in `publish_azure()`, `publish_sharepoint()`, `publish_ftp()`:
  `final_dir` cleaned up in each method via `try/finally`

Phase 2 fixes the remaining 6 callers of the conversion functions that still leak `final_dir`
(a `tempfile.mkdtemp()` directory inside `_TMP_BASE` / `GIS_TMP_DIR`).

---

## What Leaks and Where

| # | File | Function | What leaks |
|---|---|---|---|
| A | `govapp/apps/publisher/models/publish_channels.py` | `publish_geoserver_layer()` | `final_dir` after `geoserver.upload_geopackage()` |
| B | `govapp/apps/publisher/geoserver_manager.py` | `_configure_geoserver_for_queue_item()` | `final_dir` after GeoServer configured (GEOPACKAGE only) |
| C | `govapp/apps/catalogue/directory_notifications.py` | `catalogue_entry_update_success()` | `final_dir` after `webhooks.post_geojson()` |
| D | `govapp/apps/catalogue/notifications.py` | `catalogue_entry_update_success()` | `final_dir` after `webhooks.post_geojson()` |
| E | `govapp/apps/catalogue/directory_absorber.py` | `convert_to_geojson()` | `final_dir` (empty after file moved) after `move_file_to_storage_with_uniquename()` |
| F | `govapp/apps/catalogue/postgres_scanner.py` | `run_postgres_to_shapefile()` | `final_dir` (empty after zip deleted) after `os.unlink(source_path)` |

---

## Implementation Steps

### Fix A — `publish_geoserver_layer()` in `publish_channels.py`

**Problem**: After `geoserver.upload_geopackage(filepath=geopackage['full_filepath'], ...)`,
`final_dir` (parent of `full_filepath`) is never deleted.

**Fix**: Record `geopackage_dir` before the upload and wrap the upload call in `try/finally`:

```python
# Before:
geopackage = gis.conversions.to_geopackage(...)
geoserver.upload_geopackage(
    workspace=...,
    filepath=geopackage['full_filepath'],
    ...
)

# After:
geopackage = gis.conversions.to_geopackage(...)
geopackage_dir = pathlib.Path(geopackage['full_filepath']).parent
try:
    geoserver.upload_geopackage(
        workspace=...,
        filepath=geopackage['full_filepath'],
        ...
    )
finally:
    shutil.rmtree(geopackage_dir, ignore_errors=True)
```

- Only the GEOPACKAGE branch is modified. GEOTIFF branch is left unchanged (no temp file is
  created for GEOTIFF).
- No new imports needed (`shutil` and `pathlib` are already imported in `publish_channels.py`).

---

### Fix B — `_configure_geoserver_for_queue_item()` in `geoserver_manager.py`

**Problem**: After all GeoServer channels are configured, `queue_item.converted_file_path`
(which points to `final_dir/<layer>.gpkg` inside `_TMP_BASE`) is never deleted. The file was
already downloaded to the shared Docker volume by `kb_geoserver_manager` and is no longer needed.

**GEOTIFF safety**: For GEOTIFF, `convert_layer()` returns the *original source file path*
(in `data_storage/`, NOT in `_TMP_BASE`). That file must NEVER be deleted here. The guard
`converted_path.parent.is_relative_to(_tmp_base)` ensures only temp dirs in `_TMP_BASE` are
removed.

**Fix**:

1. Add to the imports at the top of `geoserver_manager.py`:
   ```python
   import shutil
   import decouple
   ```

2. In `_configure_geoserver_for_queue_item()`:
   - Replace `filename = pathlib.Path(queue_item.converted_file_path).name` with:
     ```python
     converted_path = pathlib.Path(queue_item.converted_file_path)
     filename = converted_path.name
     ```
   - Wrap everything **after** the `if not queue_item.converted_file_path: return` guard in a
     `try/finally`:
     ```python
     try:
         # ... all existing channel-loop code ...
         if publish_succeeded_for_any:
             queue_item.publish_entry.published_at = timezone.now()
             queue_item.publish_entry.save(update_fields=['published_at'])
     finally:
         _tmp_base = pathlib.Path(decouple.config("GIS_TMP_DIR", default="/app/tmp"))
         if converted_path.parent.is_relative_to(_tmp_base):
             shutil.rmtree(converted_path.parent, ignore_errors=True)
     ```
   - The `finally` block runs even when the early `return` (no channels found) is hit, ensuring
     the temp dir is cleaned up in that edge case too.

---

### Fix C — `catalogue_entry_update_success()` in `directory_notifications.py`

**Problem**: After `webhooks.post_geojson(geojson=output_filepath['full_filepath'], ...)`,
`output_filepath['uncompressed_filepath']` (= `final_dir`) is never deleted.
The commented-out `shutil.rmtree(filepath.parent, ...)` at the bottom targets the wrong path
(source file parent) and is not the fix.

**Fix**: Wrap the webhook call in `try/finally`:

```python
# Before:
output_filepath = gis.conversions.to_geojson(
    filepath=filepath,
    layer=entry.metadata.name
)
if settings.WEBHOOK_ENABLED:
    webhooks.post_geojson(
        *entry.webhook_notifications(manager="on_new_data").all(),
        geojson=output_filepath['full_filepath'],
    )

# After:
output_filepath = gis.conversions.to_geojson(
    filepath=filepath,
    layer=entry.metadata.name
)
try:
    if settings.WEBHOOK_ENABLED:
        webhooks.post_geojson(
            *entry.webhook_notifications(manager="on_new_data").all(),
            geojson=output_filepath['full_filepath'],
        )
finally:
    shutil.rmtree(output_filepath['uncompressed_filepath'], ignore_errors=True)
```

- No new imports needed (`shutil` and `pathlib` are already imported).

---

### Fix D — `catalogue_entry_update_success()` in `notifications.py`

**Problem**: Same as Fix C. The existing `shutil.rmtree(filepath.parent, ignore_errors=True)`
at the bottom deletes the SharePoint temporary copy of the source file (correct), but
`geojson['uncompressed_filepath']` (= `final_dir`) is never deleted.

**Fix**: Wrap the webhook call in `try/finally` and add cleanup of `final_dir`:

```python
# Before:
geojson = gis.conversions.to_geojson(
    filepath=filepath,
    layer=entry.metadata.name
)
if settings.WEBHOOK_ENABLED:
    webhooks.post_geojson(
        *entry.webhook_notifications(manager="on_new_data").all(),
        geojson=geojson['full_filepath'],
    )
# Delete local temporary copy of file if we can
shutil.rmtree(filepath.parent, ignore_errors=True)

# After:
geojson = gis.conversions.to_geojson(
    filepath=filepath,
    layer=entry.metadata.name
)
try:
    if settings.WEBHOOK_ENABLED:
        webhooks.post_geojson(
            *entry.webhook_notifications(manager="on_new_data").all(),
            geojson=geojson['full_filepath'],
        )
finally:
    shutil.rmtree(geojson['uncompressed_filepath'], ignore_errors=True)
# Delete local temporary copy of file if we can
shutil.rmtree(filepath.parent, ignore_errors=True)
```

- No new imports needed (`shutil` is already imported; `pathlib` is not needed as
  `uncompressed_filepath` is already a `pathlib.Path`).

---

### Fix E — `convert_to_geojson()` in `directory_absorber.py`

**Problem**: `move_file_to_storage_with_uniquename(path_from['full_filepath'])` moves the
`.geojson` file out of `final_dir` into `data_storage/`. After the move, `final_dir` is empty
but never deleted.

**`move_to_storage` internals** (verified in `govapp/common/local_storage.py`):
`shutil.copyfile(src, dst)` then `os.unlink(src)`. If the copy succeeds but unlink fails,
`move_to_storage` returns `False`, and `move_file_to_storage_with_uniquename` raises an
exception. In that case the source file is still in `final_dir`. Using `try/finally` ensures
cleanup runs in both success and error paths.

**Fix**: Wrap the move call in `try/finally`:

```python
# Before:
def convert_to_geojson(self, filepath: str, catalogue_entry: ...) -> pathlib.Path:
    path_from = to_geojson(
        filepath=pathlib.Path(filepath),
        layer=catalogue_entry.name
    )
    return self.move_file_to_storage_with_uniquename(path_from['full_filepath'])

# After:
def convert_to_geojson(self, filepath: str, catalogue_entry: ...) -> pathlib.Path:
    path_from = to_geojson(
        filepath=pathlib.Path(filepath),
        layer=catalogue_entry.name
    )
    try:
        return self.move_file_to_storage_with_uniquename(path_from['full_filepath'])
    finally:
        shutil.rmtree(path_from['uncompressed_filepath'], ignore_errors=True)
```

- `return` inside `try` triggers `finally` before returning, so cleanup runs on the success path. ✓
- If `move_file_to_storage_with_uniquename` raises, `finally` still runs and cleans up `final_dir`. ✓
- Add `import shutil` to the imports in `directory_absorber.py` (currently missing).
- `pathlib` is already imported.

---

### Fix F — `run_postgres_to_shapefile()` in `postgres_scanner.py`

**Problem**: `co["compressed_filepath"]` = `final_dir/layer.zip`. The zip file is copied to
`pending_imports/` and then deleted with `os.unlink(source_path)`. After the unlink, `final_dir`
is empty but never deleted.

**Fix**: Add one line after `os.unlink(source_path)`:

```python
# Before:
shutil.copyfile(source_path, destination_path)
os.unlink(source_path)
log.info(...)

# After:
shutil.copyfile(source_path, destination_path)
os.unlink(source_path)
shutil.rmtree(os.path.dirname(source_path), ignore_errors=True)
log.info(...)
```

- No new imports needed (`shutil` and `os` are already imported).

---

## Verification Checklist

After implementing all fixes:

1. Run `get_errors` on all 6 modified files and confirm zero compile errors.
2. **Fix A (GEOTIFF safety)**: Confirm only the `StoreType.GEOPACKAGE` branch contains the
   new cleanup code. The `StoreType.GEOTIFF` branch must be unchanged.
3. **Fix B (GEOTIFF safety)**: Confirm that for a GEOTIFF `converted_file_path` (which lives in
   `data_storage/`, not `_TMP_BASE`), `is_relative_to(_tmp_base)` returns `False` → no deletion.
4. **Fix E**: Confirm `move_file_to_storage_with_uniquename()` moves (not copies) the `.geojson`
   file out of `final_dir` before `rmtree` is called, so no data is lost.
5. **Fix F**: Confirm `os.path.dirname(source_path)` returns `final_dir` (the direct parent of
   the zip file, not a higher-level directory).

---

## Design Decisions

- **`is_relative_to` guard in Fix B** (rather than checking `channel.store_type`): More robust
  against future changes where the store_type might not be directly accessible.
- **`ignore_errors=True` on all `shutil.rmtree` calls**: Cleanup failures must never break the
  main processing flow. A leak is always preferable to a crash.
- **`try/finally` for webhook callers (Fix C, D)**: Ensures cleanup runs even if
  `webhooks.post_geojson()` raises an exception.
- **Fix A wraps only `upload_geopackage()`**: The `set_default_style_to_layer()` call that
  follows does not need the file; it is fine to have already cleaned up before that call.
  However, to keep the scope minimal and avoid refactoring, only the upload call is wrapped.
  (`set_default_style_to_layer` is after the if/elif block, so it runs after cleanup.)
- **Fix B uses `decouple.config()`** to read `GIS_TMP_DIR` rather than importing the private
  `_TMP_BASE` from `conversions.py`, keeping modules loosely coupled.
