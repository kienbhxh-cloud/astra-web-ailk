"""Read-only Google Drive lister with a per-project folder allowlist.

DRIVE FIRST: Drive stays the system of record. This module never writes or
deletes on Drive. It only reports which files exist so the store can prune,
and it reports ``listing_complete=False`` whenever it cannot PROVE the listing
is whole (API error, pagination loop, page cap, ``incompleteSearch``), so a
partial listing can never delete knowledge.

The Drive client is injected (``googleapiclient`` ``files()`` resource, or any
object with the same ``list(...).execute()`` shape). Credentials are never
read from or stored in this repository.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Iterable, List, Set

FOLDER_MIME = "application/vnd.google-apps.folder"


@dataclass
class Listing:
    listing_complete: bool
    status: str
    files: List[Dict[str, Any]] = field(default_factory=list)

    @property
    def source_keys(self) -> Set[str]:
        return {f["source_key"] for f in self.files}


class ReadOnlyDriveConnector:
    def __init__(self, folder_allowlist: Dict[str, Iterable[str]], files_api: Any = None,
                 max_pages: int = 200, page_size: int = 100):
        self._allow = {k: frozenset(v) for k, v in folder_allowlist.items()}
        self._api = files_api
        self.max_pages = max_pages
        self.page_size = page_size

    def is_folder_allowed(self, project_id: str, folder_id: str) -> bool:
        return folder_id in self._allow.get(project_id, frozenset())

    def list_project(self, project_id: str, folder_id: str) -> Listing:
        if not self.is_folder_allowed(project_id, folder_id):
            return Listing(False, "FOLDER_NOT_IN_ALLOWLIST")
        if self._api is None:
            return Listing(False, "DRIVE_CLIENT_NOT_CONFIGURED")
        if "'" in folder_id or "\\" in folder_id:
            return Listing(False, "INVALID_FOLDER_ID")
        out: List[Dict[str, Any]] = []
        token, seen_tokens = None, set()
        try:
            for _ in range(self.max_pages):
                resp = self._api.list(
                    q=f"'{folder_id}' in parents and trashed = false",
                    fields="nextPageToken, incompleteSearch, files(id, name, mimeType, md5Checksum, modifiedTime, version)",
                    pageSize=self.page_size, pageToken=token,
                    supportsAllDrives=True, includeItemsFromAllDrives=True,
                ).execute()
                if resp.get("incompleteSearch"):
                    return Listing(False, "DRIVE_INCOMPLETE_SEARCH")
                for f in resp.get("files", []):
                    if not f.get("id"):
                        return Listing(False, "DRIVE_ITEM_WITHOUT_ID")
                    if f.get("mimeType") == FOLDER_MIME:
                        continue  # subfolders need their own allowlist entry
                    out.append({
                        "id": f["id"], "name": f.get("name", ""), "mimeType": f.get("mimeType", ""),
                        "version": f.get("version") or f.get("md5Checksum") or f.get("modifiedTime"),
                        "source_key": f"{project_id}|drive:{f['id']}",
                        "url": f"https://drive.google.com/file/d/{f['id']}/view",
                    })
                token = resp.get("nextPageToken")
                if not token:
                    return Listing(True, "OK", out)
                if token in seen_tokens:
                    return Listing(False, "PAGINATION_LOOP")
                seen_tokens.add(token)
            return Listing(False, "PAGE_CAP_REACHED")
        except Exception as exc:  # network, quota, auth — never treat as "empty folder"
            return Listing(False, f"LISTING_ERROR:{type(exc).__name__}")
