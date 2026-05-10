"""农历计算工具 - 基于 lunarcalendar 库"""
from datetime import date, timedelta
from functools import lru_cache

try:
    from lunarcalendar import Converter, Lunar, Solar
    _LUNAR_AVAILABLE = True
except ImportError:
    _LUNAR_AVAILABLE = False

# Fallback lookup for when lunarcalendar is not installed
# Covers 2024-2027 major lunar festivals
_FALLBACK_FESTIVALS = {
    "2024-02-10": "春节（正月初一）",
    "2024-02-24": "元宵节（正月十五）",
    "2024-04-04": "清明节",
    "2024-06-10": "端午节（五月初五）",
    "2024-08-10": "七夕节（七月初七）",
    "2024-09-17": "中秋节（八月十五）",
    "2024-10-11": "重阳节（九月初九）",
    "2025-01-29": "春节（正月初一）",
    "2025-02-12": "元宵节（正月十五）",
    "2025-04-04": "清明节",
    "2025-05-31": "端午节（五月初五）",
    "2025-08-29": "七夕节（七月初七）",
    "2025-10-06": "中秋节（八月十五）",
    "2025-10-29": "重阳节（九月初九）",
    "2026-02-17": "春节（正月初一）",
    "2026-03-03": "元宵节（正月十五）",
    "2026-04-05": "清明节",
    "2026-05-31": "端午节（五月初五）",
    "2026-08-19": "七夕节（七月初七）",
    "2026-09-27": "中秋节（八月十五）",
    "2026-10-18": "重阳节（九月初九）",
    "2027-01-06": "腊八节（腊月初八）",
    "2027-02-06": "春节（正月初一）",
    "2027-02-20": "元宵节（正月十五）",
    "2027-04-05": "清明节",
    "2027-05-19": "端午节（五月初五）",
    "2027-08-08": "七夕节（七月初七）",
    "2027-09-15": "中秋节（八月十五）",
    "2027-10-07": "重阳节（九月初九）",
}

_LUNAR_MONTH_NAMES = [
    "", "正月", "二月", "三月", "四月", "五月", "六月",
    "七月", "八月", "九月", "十月", "冬月", "腊月",
]

_LUNAR_DAY_NAMES = {
    1: "初一", 2: "初二", 3: "初三", 4: "初四", 5: "初五",
    6: "初六", 7: "初七", 8: "初八", 9: "初九", 10: "初十",
    11: "十一", 12: "十二", 13: "十三", 14: "十四", 15: "十五",
    16: "十六", 17: "十七", 18: "十八", 19: "十九", 20: "二十",
    21: "廿一", 22: "廿二", 23: "廿三", 24: "廿四", 25: "廿五",
    26: "廿六", 27: "廿七", 28: "廿八", 29: "廿九", 30: "三十",
}

_ANIMALS = ["鼠", "牛", "虎", "兔", "龙", "蛇", "马", "羊", "猴", "鸡", "狗", "猪"]


def _lunar_day_name(day: int) -> str:
    return _LUNAR_DAY_NAMES.get(day, str(day))


def _lunar_month_name(month: int, is_leap: bool = False) -> str:
    prefix = "闰" if is_leap else ""
    return f"{prefix}{_LUNAR_MONTH_NAMES[month]}"


def _year_name(lunar_year: int) -> str:
    return f"{_ANIMALS[(lunar_year - 4) % 12]}年"


def solar_to_lunar(solar_date: date) -> dict | None:
    """公历转农历，返回结构化农历信息"""
    if _LUNAR_AVAILABLE:
        try:
            solar = Solar(solar_date.year, solar_date.month, solar_date.day)
            lunar = Converter.Solar2Lunar(solar)
            is_leap = lunar.isleap
            month_name = _lunar_month_name(lunar.month, is_leap)
            day_name = _lunar_day_name(lunar.day)
            return {
                "solar_date": solar_date.isoformat(),
                "lunar_year": lunar.year,
                "lunar_year_name": _year_name(lunar.year),
                "lunar_month": lunar.month,
                "lunar_month_name": month_name,
                "lunar_day": lunar.day,
                "lunar_day_name": day_name,
                "is_leap": is_leap,
                "full_name": f"{_year_name(lunar.year)}{month_name}{day_name}",
            }
        except Exception:
            return None

    # Pure-Python fallback: approximate calculation
    # Based on the known lunar date 1900-01-31 = 正月初一 (1900年)
    # Using simplified lookup for 2024-2030 range
    return _fallback_lunar(solar_date)


@lru_cache(maxsize=512)
def _fallback_lunar(solar_date: date) -> dict | None:
    """Simplified lunar calendar for ~2024-2030 range using lookup + offset"""
    # Known anchor: 2026-02-17 = 正月初一 (lunar year 2026=丙午/马年)
    anchor_date = date(2026, 2, 17)
    anchor_lunar_year = 2026
    anchor_lunar_month = 1
    anchor_lunar_day = 1

    # Approximate lunar months as 29.53 days average
    delta_days = (solar_date - anchor_date).days
    LUNAR_MONTH_DAYS = 29.53

    total_months = round(delta_days / LUNAR_MONTH_DAYS)
    total_days = delta_days

    # Compute approximate lunar year/month/day by stepping from anchor
    days_remaining = total_days
    year_offset = 0
    # Step by years
    for y_offset in range(0, 10):
        year_days = _lunar_year_days(anchor_lunar_year + y_offset)
        if days_remaining >= 0 and y_offset > 0:
            # Forward
            if days_remaining >= year_days:
                days_remaining -= year_days
                year_offset = y_offset + 1
        elif days_remaining < 0:
            # Backward
            prev_year_days = _lunar_year_days(anchor_lunar_year - 1)
            days_remaining += prev_year_days
            year_offset = -1

    lunar_year = anchor_lunar_year + year_offset

    # Step through months (simplified: assume 29 or 30 day months alternating)
    month = 1
    remain = total_days
    while remain > 0:
        month_days = 30 if month % 2 == 1 else 29
        if remain >= month_days:
            remain -= month_days
            month += 1
        else:
            break
    day = remain + 1

    if month > 12:
        month -= 12
        lunar_year += 1

    # Handle negative (backward from anchor)
    if total_days < 0:
        remain = -total_days
        month = 12
        lunar_year = anchor_lunar_year - 1
        while remain > 0:
            month_days = 30 if month % 2 == 1 else 29
            if remain >= month_days:
                remain -= month_days
                month -= 1
            else:
                break
            if month < 1:
                month = 12
                lunar_year -= 1
        day = month_days - remain

    month_name = _lunar_month_name(month)
    day_name = _lunar_day_name(day)
    return {
        "solar_date": solar_date.isoformat(),
        "lunar_year": lunar_year,
        "lunar_year_name": _year_name(lunar_year),
        "lunar_month": month,
        "lunar_month_name": month_name,
        "lunar_day": day,
        "lunar_day_name": day_name,
        "is_leap": False,
        "full_name": f"{_year_name(lunar_year)}{month_name}{day_name}",
    }


def _lunar_year_days(year: int) -> int:
    """Approximate days in a lunar year"""
    # A lunar year has 12 or 13 (leap) months
    # Leap years approximately every 3 years
    leap = (year % 19) in (0, 3, 6, 9, 11, 14, 17)
    return 384 if leap else 354


def get_lunar_festival(d: date) -> str | None:
    """Returns lunar festival name if the given date is a known lunar festival"""
    return _FALLBACK_FESTIVALS.get(d.isoformat())


def get_major_lunar_festivals(year: int) -> list[dict]:
    """Get all major lunar festivals for a given year"""
    festivals = []
    start = date(year - 1, 12, 1)
    end = date(year + 1, 2, 1)
    d = start
    while d <= end:
        name = get_lunar_festival(d)
        if name:
            festivals.append({"date": d.isoformat(), "name": name})
        d += timedelta(days=1)
    return festivals
