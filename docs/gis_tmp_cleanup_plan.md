# GIS_WORK_DIR / GIS_TMP_DIR Cleanup Plan (Phase 1)

## Problem Summary

Temporary directories created under `GIS_WORK_DIR` (default `/tmp`) and
decompressed archive directories under `GIS_WORK_DIR/gis_processing/` are
never deleted after use.  Over time this causes disk space exhaustion.

## Safety Analysis

All conversion functions' return values are consumed **synchronously** by
their callers within the same call stack.  No Celery tasks, background
threads, or deferred execution touches these paths.  Cleanup is therefore
safe to perform immediately after use.

---

## Files to Modify

- `govapp/gis/conversions.py`
- `govapp/apps/publisher/models/publish_channels.py`

---

## Phase 1-A  —  conversions.py  (cleanup inside the conversion function)

### Rule applied

| Condition | Cleanup where |
|---|---|
| `work_dir` path is NOT in the return dict (caller cannot access it) | `finally` block inside the conversion function |
| `decompressed_dir` path is NOT in the return dict | `finally` block inside the conversion function |
| Path IS in the return dict AND caller uses it | cleanup deferred to Phase 1-B (caller) |
| Exception raised (return dict never reaches caller) | cleanup in each `except` block |

### to_geopackage() and to_geojson()  — both paths safe to cleanup in finally

Changes:
1. Add `work_dir = None` and `decompressed_dir = None` BEFORE the `try` block.
2. After `compression.decompress()`, detect and record the extracted directory:
   ```python
   _before_decompress = filepath
   filepath = compression.decompress(filepath)
   if filepath != _before_decompress and filepath.is_dir():
       decompressed_dir = filepath
   filepath = compression.flatten(filepath)
   ```
3. After the last `except` block, add:
   ```python
   finally:
       if work_dir:
           shutil.rmtree(work_dir, ignore_errors=True)
       if decompressed_dir and decompressed_dir.is_dir():
           shutil.rmtree(decompressed_dir, ignore_errors=True)
   ```

Why safe: the return dict's `uncompressed_filepath` points to `final_dir`
(inside `_TMP_BASE`), NOT inside `work_dir`.  `orignal_filepath` is returned
but no caller ever reads it.

### to_shapefile()  — decompressed_dir safe in finally; work_dir cleanup on exception only

Changes:
1. Add `work_dir = None` and `decompressed_dir = None` BEFORE the `try` block.
2. Detect `decompressed_dir` after `compression.decompress()` (same as above).
3. In EACH `except` block (TimeoutExpired, CalledProcessError, FileNotFoundError,
   Exception), add BEFORE the log/raise:
   ```python
   if work_dir:
       shutil.rmtree(work_dir, ignore_errors=True)
   ```
4. After the last `except`, add:
   ```python
   finally:
       if decompressed_dir and decompressed_dir.is_dir():
           shutil.rmtree(decompressed_dir, ignore_errors=True)
   ```

Why partial: on success, `uncompressed_filepath` = `work_dir/<layer>.shp/`
which the caller (publish_azure / publish_sharepoint / publish_ftp) uses to
read files.  work_dir cleanup on success is deferred to Phase 1-B.

### to_geodatabase()  — exception cleanup only (both paths returned to caller)

Changes:
1. Add `work_dir = None` and `decompressed_dir = None` BEFORE the `try` block.
2. Detect `decompressed_dir` after `compression.decompress()`.
3. In EACH `except` block, add BEFORE the log/raise:
   ```python
   if work_dir:
       shutil.rmtree(work_dir, ignore_errors=True)
   if decompressed_dir and decompressed_dir.is_dir():
       shutil.rmtree(decompressed_dir, ignore_errors=True)
   ```
4. NO `finally` block — on success both paths are returned and used by caller.

Why: `uncompressed_filepath` = `work_dir/<layer>.gdb/` AND
`filepath_before_flatten` = the extracted directory; both used by callers.

### postgres_to_shapefile()  — work_dir safe in finally (output_dir never used by caller)

Changes:
1. Move `work_dir = None` BEFORE the outer `try` block.
2. Keep `work_dir = tempfile.mkdtemp(...)` at its existing location inside `try`.
3. After the last `except` block, add:
   ```python
   finally:
       if work_dir:
           shutil.rmtree(work_dir, ignore_errors=True)
   ```

Why safe: `output_dir` is in the return dict for backward compat but the only
two callers (`postgres_scanner.py` and `views.py`) only access
`compressed_filepath`.  The `return None` and `return False` paths inside the
inner except are also covered by `finally`.

---

## Phase 1-B  —  publish_channels.py  (caller-side cleanup for shapefile / geodatabase)

Applies to: `publish_azure()`, `publish_sharepoint()`, `publish_ftp()`

Pattern for each method — wrap the conversion call and file-operations in
try/finally:

```python
publish_directory = None
try:
    publish_directory = function(
        filepath=filepath,
        layer=...,
        catalogue_name=...,
        export_method=...,
    )
    # ... existing file operations unchanged ...
finally:
    if publish_directory is not None:
        # Cleanup work_dir for SHAPEFILE and GEODATABASE
        if self.format in (CDDPPublishChannelFormat.SHAPEFILE,
                           CDDPPublishChannelFormat.GEODATABASE):
            shutil.rmtree(
                pathlib.Path(publish_directory['uncompressed_filepath']).parent,
                ignore_errors=True,
            )
        # Cleanup extracted archive dir for GEODATABASE only
        # (guard: is_dir() is False when no decompression occurred)
        if self.format == CDDPPublishChannelFormat.GEODATABASE:
            fb = pathlib.Path(publish_directory['filepath_before_flatten'])
            if fb.is_dir():
                shutil.rmtree(fb, ignore_errors=True)
```

Key points:
- `publish_directory = None` before `try` → if conversion function raises,
  `publish_directory` stays None and `finally` is a no-op (conversion function
  already cleaned up in its own `except` blocks).
- `ignore_errors=True` → a cleanup failure never masks the real error.
- `shutil` and `pathlib` are already imported in publish_channels.py.

---

## Status

- [ ] to_geopackage()
- [ ] to_geojson()
- [ ] to_shapefile()
- [ ] to_geodatabase()
- [ ] postgres_to_shapefile()
- [ ] publish_azure()
- [ ] publish_sharepoint()
- [ ] publish_ftp()
