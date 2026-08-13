"""
프로젝트9 · 수집 단계
DART(전자공시시스템) Open API로 기업 코드 마스터를 내려받아 스텔라이브 관련 법인·
팬 커머스·비교 크리에이터사·플랫폼 비교군(SOOP·NAVER)의 존재 여부와 재무제표를 수집한다.

  python 09_dart_financials/collect.py [--years 2016-2025]

⚠ 이 프로젝트가 왜 다른가: 01~06·08은 조회수·구독자·동시시청자 같은 "인기" 프록시를 잰다.
09는 포트폴리오에서 유일하게 **감사받은 법정 공시 데이터**(재무제표)를 다룬다.

⚠ 알아둘 것: DART 기업코드 마스터에 이름이 있다고 재무제표가 나오는 게 아니다.
`fnlttSinglAcntAll.json`은 XBRL이 태깅된 **정기보고서**(사업보고서·반기·분기보고서)만
파싱한다. 비상장 소규모 법인은 「주식회사 등의 외부감사에 관한 법률」에 따라
**감사보고서**만 제출하면 되고, 이건 이 API로 조회되지 않는다(013 no data). 그래서 이
스크립트는 "찾았다/재무제표가 있다"를 분리해서 둘 다 기록한다 — 없다는 것도 결과다.
"""
from __future__ import annotations

import argparse
import io
import json
import os
import re
import sys
import time
import warnings
import zipfile
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import requests
from bs4 import BeautifulSoup, XMLParsedAsHTMLWarning

warnings.filterwarnings("ignore", category=XMLParsedAsHTMLWarning)

HERE = Path(__file__).resolve().parent
DATA = HERE / "data"

BASE = "https://opendart.fss.or.kr/api/"
STATUS_MSG = {
    "000": "정상", "013": "데이터 없음(013)", "020": "요청 제한 초과(020)",
    "100": "파라미터 오류(100)", "800": "시스템 점검", "900": "정의되지 않은 오류",
}

# ---------------------------------------------------------------------------
# 조사 대상. corp_code는 하드코딩하지 않고 매 실행마다 기업코드 마스터에서
# corp_name **완전 일치**로 검색해 검증한다(추측 금지, PRD 지시사항).
#   category: "핵심"=스텔라이브 계열, "비교군"=팬덤/크리에이터 비교, "플랫폼"=치지직/숲 운영사
# ---------------------------------------------------------------------------
TARGETS = [
    dict(query="스텔라이브", label="스텔라이브 (StelLive 운영법인)", category="핵심",
         context="브랜드명·법인명(주식회사 스텔라이브, 2023.4 설립, 언론 보도 기준) 둘 다 검색."),
    dict(query="브레이브그룹코리아", label="브레이브그룹코리아 (Brave group 한국법인)", category="핵심",
         context="2025.7 인수 발표 시 설립 보도된 한국 자회사명."),
    dict(query="브레이브그룹", label="Brave group (일본 모기업)", category="핵심",
         context="일본 법인. 한국 DART는 내국 신고의무자만 다루므로 원칙적으로 대상 아님 — 확인용."),
    dict(query="팬딩", label="팬딩 (Fanding, 팬 커머스)", category="비교군",
         context="PRD Phase2 11번(팬 커머스) 대상. (주)팬딩, 2018.9 설립."),
    dict(query="샌드박스네트워크", label="샌드박스네트워크 (국내 대형 MCN)", category="비교군",
         context="국내 최대급 MCN·크리에이터 매니지먼트. 규모 비교용."),
    dict(query="패러블엔터테인먼트", label="패러블엔터테인먼트 (이세계아이돌 소속사)", category="비교군",
         context="이세계아이돌(우왁굳/왁타버스) 실제 관리사 — 언론 보도 기준, DART 서류 자체에 표기 없음."),
    dict(query="브레이브엔터테인먼트", label="브레이브엔터테인먼트 (참고: 동명이인 주의)", category="동명이인",
         context="K-pop 걸그룹 '브레이브걸스' 소속사. VTuber Brave group과 무관 — 혼동 방지용으로만 기록."),
    dict(query="SOOP", label="SOOP (구 아프리카TV, 치지직 경쟁 플랫폼)", category="플랫폼",
         context="상장사(067160). 국내 라이브 스트리밍 플랫폼 비교군."),
    dict(query="NAVER", label="NAVER (치지직 운영사)", category="플랫폼",
         context="상장사(035420). 프로젝트3·8이 다루는 치지직의 모기업."),
]

# 재무제표(fnlttSinglAcntAll)를 실제로 당겨올 회사 — 위 검색에서 corp_code가 잡히고
# 사업보고서 제출대상(주로 상장사)인 경우에만 값이 나온다는 걸 알고 있지만,
# "된다/안 된다"를 미리 판단하지 않고 **모든 매칭된 회사**에 대해 시도한 뒤 결과를 기록한다.


def get_api_key() -> str:
    key = os.environ.get("DART_API_KEY")
    if not key:
        raise RuntimeError(
            "환경변수 DART_API_KEY 가 설정되어 있지 않습니다.\n"
            "  setx DART_API_KEY 발급받은_키\n"
            "후 새 터미널에서 다시 실행하세요."
        )
    return key


def _get(path: str, key: str, **params) -> dict:
    """DART API 얇은 래퍼. 020(요청 제한)이면 잠깐 쉬고 1회 재시도."""
    for attempt in range(2):
        r = requests.get(BASE + path, params=dict(crtfc_key=key, **params), timeout=30)
        r.raise_for_status()
        j = r.json()
        if j.get("status") == "020" and attempt == 0:
            time.sleep(2.0)
            continue
        return j
    return j


def fetch_corp_master(key: str) -> list[dict]:
    """corpCode.xml(ZIP) 다운로드 → 메모리에서 압축 해제 → XML 파싱."""
    r = requests.get(BASE + "corpCode.xml", params=dict(crtfc_key=key), timeout=60)
    r.raise_for_status()
    z = zipfile.ZipFile(io.BytesIO(r.content))
    xml_bytes = z.read(z.namelist()[0])
    root = ET.fromstring(xml_bytes)
    rows = []
    for row in root.findall(".//list"):
        def t(tag):
            el = row.find(tag)
            return el.text.strip() if el is not None and el.text else None
        rows.append(dict(
            corp_code=t("corp_code"), corp_name=t("corp_name"),
            corp_eng_name=t("corp_eng_name"), stock_code=t("stock_code"),
            modify_date=t("modify_date"),
        ))
    return rows


def search_targets(master: list[dict]) -> pd.DataFrame:
    """TARGETS 각각을 corp_name **완전 일치**로 검색. 여러 후보가 있으면 전부 기록하되
    corp_code는 정확히 하나로 좁혀지는 경우에만 채운다(추측 금지)."""
    by_name: dict[str, list[dict]] = {}
    for row in master:
        by_name.setdefault(row["corp_name"], []).append(row)

    out = []
    for t in TARGETS:
        exact = by_name.get(t["query"], [])
        if len(exact) == 1:
            m = exact[0]
            out.append(dict(
                query=t["query"], label=t["label"], category=t["category"], context=t["context"],
                matched=True, n_candidates=1,
                corp_code=m["corp_code"], corp_name=m["corp_name"],
                corp_eng_name=m["corp_eng_name"], stock_code=(m["stock_code"] or "").strip() or None,
                note="완전 일치 1건",
            ))
        elif len(exact) > 1:
            codes = ",".join(m["corp_code"] for m in exact)
            out.append(dict(
                query=t["query"], label=t["label"], category=t["category"], context=t["context"],
                matched=False, n_candidates=len(exact),
                corp_code=None, corp_name=None, corp_eng_name=None, stock_code=None,
                note=f"완전 일치 {len(exact)}건이라 자동 선택 보류(수동 확인 필요): {codes}",
            ))
        else:
            out.append(dict(
                query=t["query"], label=t["label"], category=t["category"], context=t["context"],
                matched=False, n_candidates=0,
                corp_code=None, corp_name=None, corp_eng_name=None, stock_code=None,
                note="DART 기업코드 마스터에 없음(비상장·소규모 외부감사 미제출 또는 국내 미등록 가능)",
            ))
    return pd.DataFrame(out)


def fetch_company_overview(key: str, corp_code: str) -> dict | None:
    j = _get("company.json", key, corp_code=corp_code)
    if j.get("status") != "000":
        return None
    return dict(
        corp_code=corp_code, corp_name=j.get("corp_name"), corp_name_eng=j.get("corp_name_eng"),
        ceo_nm=j.get("ceo_nm"), corp_cls=j.get("corp_cls"), est_dt=j.get("est_dt"),
        adres=j.get("adres"), induty_code=j.get("induty_code"), hm_url=j.get("hm_url"),
    )


def fetch_filings(key: str, corp_code: str, corp_name: str) -> list[dict]:
    j = _get("list.json", key, corp_code=corp_code, bgn_de="20190101",
             end_de=datetime.now().strftime("%Y%m%d"), page_count="100")
    if j.get("status") != "000":
        return []
    return [dict(corp_code=corp_code, corp_name=corp_name, rcept_dt=it.get("rcept_dt"),
                 report_nm=it.get("report_nm"), rcept_no=it.get("rcept_no"))
            for it in j.get("list", [])]


def fetch_financials(key: str, corp_code: str, corp_name: str, years: range) -> tuple[list[dict], list[dict]]:
    """fnlttSinglAcntAll.json 시도. status/결과를 전부 로그로 남기고,
    000(정상)일 때만 계정 데이터를 raw로 반환한다. 013은 정상적인 '자료 없음'으로 처리한다."""
    status_log, raw_rows = [], []
    for year in years:
        for fs_div in ("CFS", "OFS"):  # 연결 → 별도 순
            j = _get("fnlttSinglAcntAll.json", key, corp_code=corp_code, bsns_year=str(year),
                      reprt_code="11011", fs_div=fs_div)
            status = j.get("status")
            rows = j.get("list") or []
            status_log.append(dict(
                corp_code=corp_code, corp_name=corp_name, bsns_year=year, fs_div=fs_div,
                reprt_code="11011", status=status,
                status_msg=STATUS_MSG.get(status, j.get("message", status)),
                n_rows=len(rows),
            ))
            if status == "000":
                for r in rows:
                    raw_rows.append(dict(
                        corp_code=corp_code, corp_name=corp_name, bsns_year=year, fs_div=fs_div,
                        sj_div=r.get("sj_div"), sj_nm=r.get("sj_nm"),
                        account_id=r.get("account_id"), account_nm=r.get("account_nm"),
                        thstrm_amount=r.get("thstrm_amount"), frmtrm_amount=r.get("frmtrm_amount"),
                        ord=r.get("ord"), currency=r.get("currency"),
                    ))
            time.sleep(0.12)
    return status_log, raw_rows


# ---------------------------------------------------------------------------
# 감사보고서(document.xml) 경로 — fnlttSinglAcntAll이 013(데이터 없음)을 반환하는 비상장
# 법인용 대안 경로. list.json(pblntf_ty=F)으로 감사보고서/연결감사보고서를 찾고,
# document.xml(ZIP)을 내려받아 DART 자체 DTD(dart3.xsd/dart4.xsd)의 재무제표 표를 직접
# 파싱한다. XBRL과 달리 account_id가 없는 대신 계정과목이 ACODE(표준 계정코드, TE 셀) 또는
# 순수 텍스트 라벨(TD 셀, 연결재무제표에서 관찰됨)로만 나온다. 두 형태 모두 지원한다.
#
# ⚠ 알아둘 것 (검증 과정에서 확인):
#   - 오래된 필링(~2021년 이전)은 XML 선언이 encoding="utf-8"라고 적어놓고 실제로는
#     EUC-KR 바이트인 경우가 있다(선언을 신뢰하지 않고 순서대로 디코딩 시도).
#   - 별도(OFS) 재무제표는 TABLE-GROUP에 <TITLE> + ACODE 태그가 붙은 TE 셀,
#     연결(CFS) 재무제표는 <TITLE> 없이 일반 TD 셀 + "과목/주석/당기/전기" 헤더만 있다.
#   - "영업이익(손실)"처럼 이익/손실을 한 라벨에 합쳐 부호로 표시하는 경우와,
#     "영업손실"처럼 별도 라벨로 나오되 값은 부호 없이 양수(손실 크기)로 찍히는 경우가
#     둘 다 있다 — 손실 전용 라벨은 항상 음수로 강제한다(-abs).
#   - 재무제표 본표(재무상태표/손익계산서)는 전부 "(단위 : 원)"이고, 주석(Notes) 표는
#     종종 "(단위: 천원)"이다 — 주석 표까지 스캔하지 않도록 각 재무제표 타이틀 뒤 첫
#     데이터 표만 사용한다(그 다음 표까지 안 감).
# ---------------------------------------------------------------------------

_AUDIT_BS_TITLES = {"재무상태표", "연결재무상태표", "대차대조표", "연결대차대조표"}
_AUDIT_IS_TITLES = {"손익계산서", "연결손익계산서", "포괄손익계산서", "연결포괄손익계산서"}

_AUDIT_REVENUE_LABELS = {"매출액", "영업수익", "매출", "수익(매출액)"}
_AUDIT_OP_INCOME_LABELS = {"영업이익", "영업이익(손실)"}
_AUDIT_OP_LOSS_LABELS = {"영업손실"}
_AUDIT_NET_INCOME_LABELS = {"당기순이익", "당기순이익(손실)", "반기순이익", "분기순이익"}
_AUDIT_NET_LOSS_LABELS = {"당기순손실", "반기순손실", "분기순손실"}
_AUDIT_ASSETS_LABELS = {"자산총계"}
_AUDIT_LIAB_LABELS = {"부채총계"}
_AUDIT_EQUITY_LABELS = {"자본총계"}

# (account_id 접미사, sj_div, sj_nm, account_nm 기본값) — analyze.py의 KEY_ACCOUNTS가 찾는
# localname/sj_nm과 정확히 일치시켜서 XBRL 경로와 같은 파이프라인(build_metrics)을 탄다.
_AUDIT_CONCEPTS = {
    "assets_total": ("Assets", "BS", "재무상태표"),
    "liabilities_total": ("Liabilities", "BS", "재무상태표"),
    "equity_total": ("Equity", "BS", "재무상태표"),
    "revenue": ("Revenue", "CIS", "포괄손익계산서"),
    "operating_income": ("OperatingIncomeLoss", "CIS", "포괄손익계산서"),
    "net_income": ("ProfitLoss", "CIS", "포괄손익계산서"),
}

_AUDIT_ROMAN_PREFIX = re.compile(r"^[IVXLCⅠ-ⅩA-Z0-9\.\)\(]+\s*")


def _audit_nows(s: str) -> str:
    return re.sub(r"\s+", "", s or "")


def _audit_clean_label(s: str) -> str:
    return _AUDIT_ROMAN_PREFIX.sub("", _audit_nows(s))


def _audit_parse_num(s: str):
    s = (s or "").strip()
    if not s or s in ("-", "‐", "―"):
        return None
    neg = s.startswith("(") and s.endswith(")")
    s2 = s.strip("()").replace(",", "").replace(" ", "")
    if not re.match(r"^-?\d+(\.\d+)?$", s2):
        return None
    val = float(s2)
    return -abs(val) if neg else val


def _audit_note_col_index(table) -> int | None:
    """연결재무제표(plain TD) 표는 '과목/주석/당기/전기' 4열이라 '주석' 열(콤마로 묶인
    소액 정수라 금액처럼 보일 수 있다, 예: "4,5,6,11,36")을 반드시 빼야 한다."""
    thead = table.find("thead")
    if not thead:
        return None
    for idx, th in enumerate(thead.find_all("th")):
        if _audit_nows(th.get_text()) == "주석":
            return idx
    return None


def _audit_parse_row(tr, drop_idx):
    cells = tr.find_all(["te", "td"])
    if not cells:
        return None, []
    label = cells[0].get_text()
    rest = cells[1:]
    if drop_idx is not None and 0 <= drop_idx - 1 < len(rest):
        rest = [c for k, c in enumerate(rest) if k != drop_idx - 1]
    vals = [v for v in (_audit_parse_num(c.get_text()) for c in rest) if v is not None]
    return label, vals


def _audit_extract_statement(table, wanted, found):
    drop_idx = _audit_note_col_index(table)
    for tr in table.find_all("tr"):
        label_raw, vals = _audit_parse_row(tr, drop_idx)
        if label_raw is None or not vals:
            continue
        cl = _audit_clean_label(label_raw)
        for concept_key, label_set, force_negative in wanted:
            if cl in label_set and concept_key not in found:
                current = vals[0]
                prior = vals[1] if len(vals) > 1 else None
                if force_negative:
                    current = -abs(current) if current is not None else None
                    prior = -abs(prior) if prior is not None else None
                found[concept_key] = dict(current=current, prior=prior, raw_label=label_raw.strip())


def _audit_find_data_table_after(flat, start_idx):
    for j in range(start_idx + 1, min(start_idx + 6, len(flat))):
        el = flat[j]
        if el.name == "table":
            thead = el.find("thead")
            if thead and "과목" in _audit_nows(thead.get_text()):
                return el
    return None


def parse_audit_document(text: str) -> dict:
    """DART document.xml(감사보고서) 본문에서 재무상태표·손익계산서(또는 포괄손익계산서)의
    첫 등장 표만 파싱한다. 각 재무제표는 문서당 딱 한 번만(주석의 재언급은 무시)."""
    soup = BeautifulSoup(text, "html.parser")
    flat = soup.find_all(["title", "table"])
    result = {}
    bs_done = is_done = False

    def handle(title_text, idx):
        nonlocal bs_done, is_done
        if not bs_done and title_text in _AUDIT_BS_TITLES:
            dt = _audit_find_data_table_after(flat, idx)
            if dt is not None:
                found = {}
                _audit_extract_statement(dt, [
                    ("assets_total", _AUDIT_ASSETS_LABELS, False),
                    ("liabilities_total", _AUDIT_LIAB_LABELS, False),
                    ("equity_total", _AUDIT_EQUITY_LABELS, False),
                ], found)
                result["balance_sheet"] = dict(title=title_text, data=found)
                bs_done = True
        elif not is_done and title_text in _AUDIT_IS_TITLES:
            dt = _audit_find_data_table_after(flat, idx)
            if dt is not None:
                found = {}
                _audit_extract_statement(dt, [
                    ("revenue", _AUDIT_REVENUE_LABELS, False),
                    ("operating_income", _AUDIT_OP_INCOME_LABELS, False),
                    ("operating_income", _AUDIT_OP_LOSS_LABELS, True),
                    ("net_income", _AUDIT_NET_INCOME_LABELS, False),
                    ("net_income", _AUDIT_NET_LOSS_LABELS, True),
                ], found)
                result["income_statement"] = dict(title=title_text, data=found)
                is_done = True

    for i, el in enumerate(flat):
        if bs_done and is_done:
            break
        if el.name == "title":
            handle(_audit_nows(el.get_text()), i)
        elif el.name == "table":
            cell_texts = {_audit_nows(c.get_text()) for c in el.find_all(["td", "te"], limit=8)}
            hit = (cell_texts & _AUDIT_BS_TITLES) or (cell_texts & _AUDIT_IS_TITLES)
            if hit:
                handle(next(iter(hit)), i)
    return result


def _decode_dart_bytes(raw: bytes) -> str:
    """document.xml의 XML 선언은 encoding="utf-8"이라고 적혀 있어도 오래된 필링은 실제로
    EUC-KR 바이트인 경우가 있다 — 선언을 믿지 않고 순서대로 디코딩을 시도한다."""
    for enc in ("utf-8", "euc-kr"):
        try:
            return raw.decode(enc)
        except UnicodeDecodeError:
            continue
    return raw.decode("cp949", errors="replace")


def fetch_audit_filings(key: str, corp_code: str, corp_name: str) -> list[dict]:
    """list.json(pblntf_ty=F, 외부감사관련)으로 감사보고서/연결감사보고서 이력을 전체
    기간(제한 없음)으로 조회한다. fnlttSinglAcntAll이 못 보는 필링들이 여기 있다."""
    j = _get("list.json", key, corp_code=corp_code, bgn_de="19990101",
             end_de=datetime.now().strftime("%Y%m%d"), pblntf_ty="F", page_count="100")
    if j.get("status") != "000":
        return []
    out = []
    for it in j.get("list", []):
        report_nm = it.get("report_nm") or ""
        clean_nm = re.sub(r"^\[기재정정\]", "", report_nm).strip()
        if not (clean_nm.startswith("감사보고서") or clean_nm.startswith("연결감사보고서")):
            continue
        m = re.search(r"\((\d{4})\.\d{2}\)", clean_nm)
        if not m:
            continue
        out.append(dict(
            corp_code=corp_code, corp_name=corp_name, rcept_no=it.get("rcept_no"),
            rcept_dt=it.get("rcept_dt"), report_nm=report_nm,
            fs_div="CFS" if clean_nm.startswith("연결") else "OFS",
            bsns_year=int(m.group(1)),
        ))
    return out


def _pick_latest_filings(filings: list[dict]) -> list[dict]:
    """같은 (fs_div, bsns_year)에 여러 건([기재정정] 포함)이 있으면 접수일자가 가장 늦은
    것(최종본)을 쓴다."""
    best: dict[tuple, dict] = {}
    for f in sorted(filings, key=lambda x: x["rcept_dt"]):
        best[(f["fs_div"], f["bsns_year"])] = f
    return list(best.values())


def _audit_rows_from_parsed(parsed: dict, corp_code: str, corp_name: str, filing: dict) -> list[dict]:
    """파싱 결과(당기/전기)를 XBRL과 같은 롱포맷 행으로 펼친다. 전기(비교) 값은
    is_comparative=True로 표시 — 자체 필링이 없는 연도를 메꾸는 용도로만 쓰고,
    자체 필링이 있으면 그쪽을 우선한다(뒤에서 dedup)."""
    rows = []
    for stmt_key in ("balance_sheet", "income_statement"):
        stmt = parsed.get(stmt_key)
        if not stmt:
            continue
        for concept_key, vals in stmt["data"].items():
            local, sj_div, sj_nm = _AUDIT_CONCEPTS[concept_key]
            account_id = f"dart-audit_{local}"
            if vals.get("current") is not None:
                rows.append(dict(
                    corp_code=corp_code, corp_name=corp_name, bsns_year=filing["bsns_year"],
                    fs_div=filing["fs_div"], sj_div=sj_div, sj_nm=sj_nm, account_id=account_id,
                    account_nm=vals["raw_label"], thstrm_amount=vals["current"], frmtrm_amount=vals.get("prior"),
                    ord=None, currency="KRW", source="audit_report", rcept_no=filing["rcept_no"],
                    is_comparative=False,
                ))
            if vals.get("prior") is not None:
                rows.append(dict(
                    corp_code=corp_code, corp_name=corp_name, bsns_year=filing["bsns_year"] - 1,
                    fs_div=filing["fs_div"], sj_div=sj_div, sj_nm=sj_nm, account_id=account_id,
                    account_nm=vals["raw_label"] + "(전기 비교치)", thstrm_amount=vals["prior"], frmtrm_amount=None,
                    ord=None, currency="KRW", source="audit_report", rcept_no=filing["rcept_no"],
                    is_comparative=True,
                ))
    return rows


def _dedup_audit_rows(rows: list[dict]) -> list[dict]:
    """(corp_code, fs_div, bsns_year, account_id) 중복이면 자체 필링(is_comparative=False)을
    비교치보다 우선한다."""
    best: dict[tuple, dict] = {}
    for r in rows:
        key = (r["corp_code"], r["fs_div"], r["bsns_year"], r["account_id"])
        cur = best.get(key)
        if cur is None or (cur["is_comparative"] and not r["is_comparative"]):
            best[key] = r
    return list(best.values())


def fetch_audit_report_financials(key: str, corp_code: str, corp_name: str) -> tuple[list[dict], list[dict]]:
    """감사보고서 경로 전체: 필링 목록 -> 최신본만 -> document.xml 다운로드·파싱 -> dedup.
    document.xml은 JSON 엔드포인트보다 무거우므로 호출 사이 1.5초씩 쉰다."""
    filings = _pick_latest_filings(fetch_audit_filings(key, corp_code, corp_name))
    status_log: list[dict] = []
    if not filings:
        status_log.append(dict(corp_code=corp_code, corp_name=corp_name, bsns_year=None, fs_div=None,
                                rcept_no=None, report_nm=None, status="NO_FILINGS", n_rows=0))
        return status_log, []

    raw_rows: list[dict] = []
    for f in sorted(filings, key=lambda x: (x["bsns_year"], x["fs_div"])):
        try:
            r = requests.get(BASE + "document.xml", params=dict(crtfc_key=key, rcept_no=f["rcept_no"]), timeout=60)
            r.raise_for_status()
            z = zipfile.ZipFile(io.BytesIO(r.content))
            text = "\n".join(_decode_dart_bytes(z.read(name)) for name in z.namelist())
            parsed = parse_audit_document(text)
            rows = _audit_rows_from_parsed(parsed, corp_code, corp_name, f)
            raw_rows.extend(rows)
            status_log.append(dict(corp_code=corp_code, corp_name=corp_name, bsns_year=f["bsns_year"],
                                    fs_div=f["fs_div"], rcept_no=f["rcept_no"], report_nm=f["report_nm"],
                                    status="000" if rows else "PARSE_EMPTY", n_rows=len(rows)))
        except (zipfile.BadZipFile, requests.RequestException) as e:
            status_log.append(dict(corp_code=corp_code, corp_name=corp_name, bsns_year=f["bsns_year"],
                                    fs_div=f["fs_div"], rcept_no=f["rcept_no"], report_nm=f["report_nm"],
                                    status=f"ERROR:{e}", n_rows=0))
        time.sleep(1.5)
    return status_log, _dedup_audit_rows(raw_rows)


def collect(years: range) -> None:
    DATA.mkdir(parents=True, exist_ok=True)
    key = get_api_key()

    print("DART 기업코드 마스터 다운로드 중...")
    master = fetch_corp_master(key)
    print(f"  전체 {len(master):,}개 법인 로드")

    search_df = search_targets(master)
    search_df.to_csv(DATA / "corp_search.csv", index=False)
    print("\n=== 대상 법인 검색 결과 ===")
    for _, r in search_df.iterrows():
        mark = "찾음" if r["matched"] else "없음"
        print(f"  [{mark}] {r['label']:38s} {r['note']}")

    matched = search_df[search_df["matched"]].copy()

    overview_rows, filing_rows = [], []
    status_rows, financial_rows = [], []
    audit_status_rows, audit_financial_rows = [], []
    for _, r in matched.iterrows():
        cc, name = r["corp_code"], r["corp_name"]
        ov = fetch_company_overview(key, cc)
        if ov:
            overview_rows.append(ov)
        time.sleep(0.12)
        filing_rows.extend(fetch_filings(key, cc, name))
        time.sleep(0.12)
        print(f"\n재무제표 조회: {name} ({cc}) {years.start}~{years.stop - 1}년...")
        slog, frows = fetch_financials(key, cc, name, years)
        status_rows.extend(slog)
        financial_rows.extend(frows)
        ok_years = sorted({s["bsns_year"] for s in slog if s["status"] == "000"})
        print(f"  -> 재무제표 확보 연도: {ok_years if ok_years else '없음(013 등 — 감사보고서만 제출했을 가능성)'}")

        if not ok_years:
            # XBRL(정기보고서)이 비어 있으면 감사보고서 경로로 대체 시도한다. corp_code가
            # 있어도 필링 자체가 없는 법인(예: 팬딩)은 여기서도 그대로 0건으로 끝난다 —
            # "없다"는 것 자체가 정직한 결과다.
            print(f"  -> 감사보고서(document.xml) 경로 시도...")
            aslog, arows = fetch_audit_report_financials(key, cc, name)
            audit_status_rows.extend(aslog)
            audit_financial_rows.extend(arows)
            audit_years = sorted({row["bsns_year"] for row in arows})
            print(f"  -> 감사보고서에서 확보한 연도: {audit_years if audit_years else '없음(필링 자체가 없거나 파싱 실패)'}")

    overview_df = pd.DataFrame(overview_rows)
    filings_df = pd.DataFrame(filing_rows)
    status_df = pd.DataFrame(status_rows)
    financial_df = pd.DataFrame(financial_rows)
    audit_status_df = pd.DataFrame(audit_status_rows)
    audit_financial_df = pd.DataFrame(audit_financial_rows)

    overview_df.to_csv(DATA / "company_overview.csv", index=False)
    filings_df.to_csv(DATA / "filings.csv", index=False)
    status_df.to_csv(DATA / "financials_status.csv", index=False)
    financial_df.to_csv(DATA / "financials_raw.csv", index=False)
    audit_status_df.to_csv(DATA / "financials_audit_status.csv", index=False)
    audit_financial_df.to_csv(DATA / "financials_audit_raw.csv", index=False)

    n_ok_companies = status_df[status_df["status"] == "000"]["corp_code"].nunique() if len(status_df) else 0
    n_audit_companies = (audit_financial_df["corp_code"].nunique()
                          if len(audit_financial_df) else 0)
    meta = dict(
        fetched_at=datetime.now(timezone.utc).isoformat(),
        source="Open DART(전자공시시스템) Open API — corpCode.xml, company.json, list.json, "
               "fnlttSinglAcntAll.json, document.xml",
        corp_master_total=len(master),
        n_targets=len(TARGETS), n_matched=int(matched.shape[0]),
        n_with_financials=int(n_ok_companies),
        n_with_audit_report_financials=int(n_audit_companies),
        years=[years.start, years.stop - 1],
        note="fnlttSinglAcntAll은 XBRL 태깅된 정기보고서(사업/반기/분기보고서)만 파싱한다. "
             "감사보고서만 제출하는 비상장 법인은 corp_code가 있어도 013(데이터 없음)이 정상 결과다. "
             "이 경우 document.xml(감사보고서 원문 ZIP)을 직접 파싱하는 대체 경로를 시도한다 "
             "(fetch_audit_report_financials) — 그래도 필링 자체가 아예 없는 법인(예: 팬딩)은 "
             "이 경로로도 데이터가 나오지 않는다.",
    )
    (DATA / "_meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"\n완료: 대상 {len(TARGETS)}곳 중 {matched.shape[0]}곳 매칭, "
          f"XBRL 재무제표 확보 {n_ok_companies}곳, 감사보고서 경로로 추가 확보 {n_audit_companies}곳 -> {DATA}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--years", default="2016-2025", help="예: 2016-2025 (사업연도 범위, 양끝 포함)")
    args = ap.parse_args()
    a, b = args.years.split("-")
    collect(range(int(a), int(b) + 1))
