import os
import json
import logging
import hashlib
from pathlib import Path
from typing import Dict, Any, Optional

from app.core.runtime_config import MINERU_ENABLED

logger = logging.getLogger(__name__)

# Prefer the pip-installed MinerU package (3.4.x). Do NOT prepend the old
# project-root vendor tree onto sys.path — it shadows the installed version.
MINERU_AVAILABLE = False
MINERU_VERSION = "unavailable"
pipeline_doc_analyze_streaming = None
FileBasedDataWriter = None
prepare_env = None
convert_pdf_bytes_to_bytes = None
validate_public_ocr_lang = None


def _stub_validate_public_ocr_lang(lang: str) -> str:
    return lang or "ch"


if MINERU_ENABLED:
    try:
        from importlib.metadata import version as _pkg_version

        from mineru.backend.pipeline.pipeline_analyze import (
            doc_analyze_streaming as pipeline_doc_analyze_streaming,
        )
        from mineru.data.data_reader_writer import FileBasedDataWriter
        from mineru.cli.common import prepare_env, convert_pdf_bytes_to_bytes
        from mineru.utils.ocr_language import validate_public_ocr_lang

        MINERU_AVAILABLE = True
        try:
            MINERU_VERSION = _pkg_version("mineru")
        except Exception:
            MINERU_VERSION = "unknown"
    except ImportError as exc:
        logger.warning("MinerU enabled but not installed: %s", exc)

        def pipeline_doc_analyze_streaming(*args, **kwargs):
            raise RuntimeError("MinerU not installed")

        class FileBasedDataWriter:  # type: ignore[no-redef]
            pass

        def prepare_env(*args, **kwargs):
            raise RuntimeError("MinerU not installed")

        def convert_pdf_bytes_to_bytes(*args, **kwargs):
            raise RuntimeError("MinerU not installed")

        validate_public_ocr_lang = _stub_validate_public_ocr_lang
else:
    logger.info("MinerU disabled (MINERU_ENABLED=false) — runtime-only mode")

    def pipeline_doc_analyze_streaming(*args, **kwargs):
        raise RuntimeError("MinerU disabled on this host")

    class FileBasedDataWriter:  # type: ignore[no-redef]
        pass

    def prepare_env(*args, **kwargs):
        raise RuntimeError("MinerU disabled on this host")

    def convert_pdf_bytes_to_bytes(*args, **kwargs):
        raise RuntimeError("MinerU disabled on this host")

    validate_public_ocr_lang = _stub_validate_public_ocr_lang


def is_mineru_ready() -> bool:
    """True only when this host is allowed and able to run scans."""
    return bool(MINERU_ENABLED and MINERU_AVAILABLE)


class MinerUService:
    """PDF → MinerU middle JSON via the pipeline backend (local OCR/layout)."""

    def __init__(self, upload_dir: str):
        self.upload_dir = upload_dir
        os.makedirs(upload_dir, exist_ok=True)

    def calculate_sha256(self, file_path: str) -> str:
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()

    def _normalize_lang(self, lang: str) -> str:
        # MinerU 3.4 maps "en"/latin aliases to the unified "ch" OCR model.
        try:
            return validate_public_ocr_lang(lang or "ch")
        except ValueError:
            logger.warning("Unsupported OCR lang %r — falling back to 'ch'", lang)
            return "ch"

    def parse_pdf(
        self,
        file_path: str,
        output_dir: str = "output",
        lang: str = "en",
        parse_method: str = "auto",
        formula_enable: bool = True,
        table_enable: bool = True,
    ) -> Dict[str, Any]:
        if not is_mineru_ready():
            return {
                "success": False,
                "error": (
                    "MinerU scanning is not available on this host. "
                    "Set MINERU_ENABLED=true and install mineru[pipeline] on the workstation."
                ),
                "mineru_version": MINERU_VERSION,
            }

        try:
            if not os.path.exists(file_path):
                return {"success": False, "error": f"File not found: {file_path}"}

            with open(file_path, "rb") as f:
                pdf_bytes = f.read()

            file_stem = Path(file_path).stem
            ocr_lang = self._normalize_lang(lang)
            processed_bytes = convert_pdf_bytes_to_bytes(pdf_bytes, 0, None)

            local_image_dir, local_md_dir = prepare_env(output_dir, file_stem, parse_method)
            image_writer = FileBasedDataWriter(local_image_dir)

            captured: Dict[str, Any] = {}

            def on_doc_ready(doc_index, model_list, middle_json, ocr_enable):
                captured["doc_index"] = doc_index
                captured["model_list"] = model_list
                captured["middle_json"] = middle_json
                captured["ocr_enable"] = ocr_enable

            pipeline_doc_analyze_streaming(
                [processed_bytes],
                [image_writer],
                [ocr_lang],
                on_doc_ready,
                parse_method=parse_method,
                formula_enable=formula_enable,
                table_enable=table_enable,
                client_side_output_generation=False,
            )

            middle_json: Optional[Dict[str, Any]] = captured.get("middle_json")
            if not middle_json:
                return {
                    "success": False,
                    "error": "MinerU finished without producing middle JSON.",
                    "mineru_version": MINERU_VERSION,
                }

            os.makedirs(output_dir, exist_ok=True)
            json_path = os.path.join(output_dir, f"{file_stem}_middle.json")
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(middle_json, f, indent=4, ensure_ascii=False)

            md_json_path = os.path.join(local_md_dir, f"{file_stem}_middle.json")
            try:
                with open(md_json_path, "w", encoding="utf-8") as f:
                    json.dump(middle_json, f, indent=4, ensure_ascii=False)
            except Exception:
                logger.debug("Could not write secondary middle JSON at %s", md_json_path)

            page_count = len(middle_json.get("pdf_info") or [])
            logger.info(
                "MinerU %s parsed %s (%d pages, ocr=%s, lang=%s)",
                MINERU_VERSION,
                file_stem,
                page_count,
                captured.get("ocr_enable"),
                ocr_lang,
            )

            return {
                "success": True,
                "middle_json": middle_json,
                "json_path": json_path,
                "images_dir": local_image_dir,
                "md_dir": local_md_dir,
                "mineru_version": MINERU_VERSION,
                "ocr_lang": ocr_lang,
                "ocr_enable": captured.get("ocr_enable"),
                "page_count": page_count,
            }

        except Exception as e:
            logger.exception("MinerU Parsing Failed")
            return {
                "success": False,
                "error": str(e),
                "mineru_version": MINERU_VERSION,
            }
