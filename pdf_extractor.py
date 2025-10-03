import re
from io import BytesIO
import pdfplumber
import PyPDF2


class PDFExtractor:
    def __init__(self) -> None:
        self.parameter_patterns = {
            'viscosidade_40c': [
                r'viscosidade\s*[:=]?\s*40\s*°?c[^\d]*(\d+[,.]?\d*)',
                r'viscosidade[^\d]*(\d+[,.]?\d*)\s*cst',
                r'viscosity\s*[:=]?\s*40\s*°?c[^\d]*(\d+[,.]?\d*)',
            ],
            'teor_agua': [
                r'(?:teor\s*de\s*|conteúdo\s*de\s*|água\s*[:=]?\s*)(\d+[,.]?\d*)\s*ppm',
                r'water\s*content[^\d]*(\d+[,.]?\d*)\s*ppm',
            ],
            'particulas_4um': [
                r'(?:part[ií]culas|particles)[^\n>]*?>\s*4\s*µ?m[^\d]*(\d+[,.]?\d*)',
                r'>\s*4\s*µ?m[^\d]*(\d+[,.]?\d*)',
            ],
            'particulas_6um': [
                r'(?:part[ií]culas|particles)[^\n>]*?>\s*6\s*µ?m[^\d]*(\d+[,.]?\d*)',
                r'>\s*6\s*µ?m[^\d]*(\d+[,.]?\d*)',
            ],
            'particulas_14um': [
                r'(?:part[ií]culas|particles)[^\n≥]*?≥\s*14\s*µ?m[^\d]*(\d+[,.]?\d*)',
                r'≥\s*14\s*µ?m[^\d]*(\d+[,.]?\d*)',
            ],
        }

    def extract_parameters(self, uploaded_file) -> dict | None:
        text = self._extract_with_pdfplumber(uploaded_file)
        if not text:
            text = self._extract_with_pypdf2(uploaded_file)
        if not text:
            return None
        return self._parse_parameters(text)

    def _extract_with_pdfplumber(self, uploaded_file) -> str | None:
        try:
            uploaded_file.seek(0)
            with pdfplumber.open(BytesIO(uploaded_file.read())) as pdf:
                parts = []
                for p in pdf.pages:
                    t = p.extract_text() or ""
                    parts.append(t)
            return "\n".join(parts).lower()
        except Exception:
            return None

    def _extract_with_pypdf2(self, uploaded_file) -> str | None:
        try:
            uploaded_file.seek(0)
            reader = PyPDF2.PdfReader(BytesIO(uploaded_file.read()))
            parts = []
            for page in reader.pages:
                parts.append(page.extract_text() or "")
            return "\n".join(parts).lower()
        except Exception:
            return None

    def _parse_parameters(self, text: str) -> dict | None:
        out: dict[str, float] = {}
        for key, patterns in self.parameter_patterns.items():
            value = self._extract_first_number(text, patterns)
            if value is not None:
                out[key] = value
        return out if len(out) >= 3 else None

    def _extract_first_number(self, text: str, patterns: list[str]) -> float | None:
        for pat in patterns:
            for m in re.finditer(pat, text, re.IGNORECASE | re.DOTALL):
                try:
                    v = float(m.group(1).replace(',', '.'))
                    return v
                except Exception:
                    continue
        return None

