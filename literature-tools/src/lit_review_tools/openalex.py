from __future__ import annotations

import math
import re
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from typing import Any

import pandas as pd
import requests
from tqdm.auto import tqdm

from .common import normalize_doi, normalize_pmid

OPENALEX_WORKS_URL = "https://api.openalex.org/works"


@dataclass(frozen=True)
class OpenAlexClient:
    email: str | None = None
    batch_size: int = 50
    timeout: int = 30
    retries: int = 3
    sleep_seconds: float = 0.1

    def _params(self, extra: dict[str, Any]) -> dict[str, Any]:
        params = dict(extra)
        if self.email:
            params["mailto"] = self.email
        return params

    def get_json(self, params: dict[str, Any]) -> dict[str, Any] | None:
        for attempt in range(1, self.retries + 1):
            try:
                response = requests.get(OPENALEX_WORKS_URL, params=self._params(params), timeout=self.timeout)
                if response.status_code == 200:
                    return response.json()
                time.sleep(attempt)
            except requests.RequestException:
                time.sleep(attempt)
        return None

    def fetch_batch(self, ids: list[str], id_type: str) -> dict[str, dict]:
        if not ids:
            return {}
        data = self.get_json({"filter": f"{id_type}:{'|'.join(ids)}", "per-page": 100})
        output: dict[str, dict] = {}
        for work in (data or {}).get("results", []):
            ids_obj = work.get("ids") or {}
            if id_type == "doi":
                key = normalize_doi(work.get("doi") or ids_obj.get("doi"))
            elif id_type == "pmid":
                key = normalize_pmid(ids_obj.get("pmid"))
            else:
                key = None
            if key:
                output[key] = work
        return output

    def fetch_many(self, ids: list[str], id_type: str) -> dict[str, dict]:
        unique_ids = sorted({item for item in ids if item})
        output: dict[str, dict] = {}
        chunks = math.ceil(len(unique_ids) / self.batch_size) if unique_ids else 0
        for index in tqdm(range(chunks), desc=f"OpenAlex {id_type} batches"):
            batch = unique_ids[index * self.batch_size : (index + 1) * self.batch_size]
            output.update(self.fetch_batch(batch, id_type))
            time.sleep(self.sleep_seconds)
        return output

    def search_title(self, title: str) -> dict | None:
        if not title:
            return None
        data = self.get_json({"search": f'"{title}"', "per-page": 1})
        results = (data or {}).get("results", [])
        return results[0] if results else None


def publication_month(work: dict[str, Any]) -> str | None:
    value = work.get("publication_date")
    if not isinstance(value, str):
        return None
    match = re.match(r"^(\d{4})-(\d{2})", value)
    return f"{match.group(1)}-{match.group(2)}" if match else None


def doi_from_work(work: dict[str, Any]) -> str | None:
    ids = work.get("ids") or {}
    return normalize_doi(work.get("doi") or ids.get("doi"))


def add_doi_from_openalex(
    df: pd.DataFrame,
    client: OpenAlexClient,
    pmid_col: str = "PMID",
    doi_col: str = "DI",
    output_col: str = "returned_doi",
) -> pd.DataFrame:
    result = df.copy()
    result[output_col] = None

    if pmid_col in result.columns:
        pmids = [normalize_pmid(value) for value in result[pmid_col]]
        pmid_map = client.fetch_many([value for value in pmids if value], "pmid")
        for idx, pmid in enumerate(pmids):
            work = pmid_map.get(pmid or "")
            if work:
                result.at[idx, output_col] = doi_from_work(work)

    if doi_col in result.columns:
        missing = result[output_col].isna()
        dois = [normalize_doi(value) for value in result.loc[missing, doi_col]]
        doi_map = client.fetch_many([value for value in dois if value], "doi")
        for idx, doi in zip(result.loc[missing].index, dois):
            work = doi_map.get(doi or "")
            if work:
                result.at[idx, output_col] = doi_from_work(work)

    return result


def enrich_with_openalex(
    df: pd.DataFrame,
    client: OpenAlexClient,
    title_col: str = "TI",
    doi_col: str = "DI",
    pmid_col: str = "PMID",
    max_workers: int = 8,
) -> pd.DataFrame:
    result = df.copy()
    for column in ["match_source", "match_query", "publication_month", "cited_by_count", "openalex_id", "issue_flag"]:
        result[column] = None

    if doi_col in result.columns:
        clean_dois = result[doi_col].map(normalize_doi)
        doi_map = client.fetch_many([value for value in clean_dois if value], "doi")
        for idx, doi in clean_dois.items():
            work = doi_map.get(doi or "")
            if work:
                _apply_work(result, idx, work, "DI", f"doi:{doi}")

    if pmid_col in result.columns:
        mask = result["match_source"].isna()
        clean_pmids = result.loc[mask, pmid_col].map(normalize_pmid)
        pmid_map = client.fetch_many([value for value in clean_pmids if value], "pmid")
        for idx, pmid in clean_pmids.items():
            work = pmid_map.get(pmid or "")
            if work:
                _apply_work(result, idx, work, "PMID", f"pmid:{pmid}")

    if title_col in result.columns:
        pending = result.index[result["match_source"].isna() & result[title_col].notna()].tolist()
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {executor.submit(client.search_title, str(result.at[idx, title_col]).strip()): idx for idx in pending}
            for future in tqdm(as_completed(futures), total=len(futures), desc="OpenAlex title search"):
                idx = futures[future]
                work = future.result()
                if work:
                    _apply_work(result, idx, work, "TI", "title_search")
                else:
                    result.at[idx, "match_source"] = "miss"
                    result.at[idx, "issue_flag"] = "no_match"

    hit = result["match_source"].isin(["DI", "PMID", "TI"])
    result.loc[hit & result["cited_by_count"].isna(), "issue_flag"] = "cited_by_count_missing"
    result.loc[hit, "issue_flag"] = result.loc[hit, "issue_flag"].fillna("hit")
    return result


def _apply_work(df: pd.DataFrame, idx: int, work: dict, source: str, query: str) -> None:
    df.at[idx, "match_source"] = source
    df.at[idx, "match_query"] = query
    df.at[idx, "openalex_id"] = work.get("id")
    df.at[idx, "cited_by_count"] = work.get("cited_by_count")
    df.at[idx, "publication_month"] = publication_month(work)
