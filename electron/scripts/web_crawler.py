"""
建筑/景观/室内网站数据采集器

从以下网站自动采集项目数据:
- ArchDaily (全球建筑)
- 谷德设计网 (gooood.cn)
- 设计中国 (design.cn)

用法:
    python web_crawler.py --source archdaily --limit 20
    python web_crawler.py --source gooood --limit 20
    python web_crawler.py --all --limit 50
"""

import json
import re
import time
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Optional
from urllib.parse import urljoin

# 尝试导入 requests, BeautifulSoup
try:
    import requests
    from bs4 import BeautifulSoup
    DEPENDENCIES_AVAILABLE = True
except ImportError:
    DEPENDENCIES_AVAILABLE = False


@dataclass
class ProjectItem:
    """建筑/景观/室内项目数据"""
    title: str
    source: str
    url: str
    category: str
    architect: Optional[str] = None
    location: Optional[str] = None
    year: Optional[int] = None
    area: Optional[str] = None
    description: Optional[str] = None
    tags: list = None
    images: list = None
    scraped_at: str = None

    def __post_init__(self):
        if self.tags is None:
            self.tags = []
        if self.images is None:
            self.images = []
        if self.scraped_at is None:
            self.scraped_at = datetime.now().isoformat()


class ArchDailyCrawler:
    """ArchDaily 网站爬虫"""

    BASE_URL = "https://www.archdaily.com"
    SEARCH_URL = "https://www.archdaily.com/search/projects"

    def __init__(self, timeout: int = 30):
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        })

    def search(self, query: str = "", category: str = "", limit: int = 20) -> list[ProjectItem]:
        """搜索项目"""
        results = []

        # 构造搜索URL
        params = {"query": query}
        if category:
            params["types"] = category

        try:
            resp = self.session.get(self.SEARCH_URL, params=params, timeout=self.timeout)
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, "html.parser")

            # 解析项目卡片
            cards = soup.select("div.project-card")[:limit]

            for card in cards:
                try:
                    title_elem = card.select_one("h3 a")
                    if not title_elem:
                        continue

                    title = title_elem.get_text(strip=True)
                    url = urljoin(self.BASE_URL, title_elem.get("href", ""))

                    # 提取其他信息
                    architect = None
                    architect_elem = card.select_one("span.architect")
                    if architect_elem:
                        architect = architect_elem.get_text(strip=True)

                    location = None
                    location_elem = card.select_one("span.location")
                    if location_elem:
                        location = location_elem.get_text(strip=True)

                    # 提取分类
                    category_tags = [a.get_text(strip=True) for a in card.select("a[rel='tag']")]

                    results.append(ProjectItem(
                        title=title,
                        source="archdaily",
                        url=url,
                        category=category_tags[0] if category_tags else "Architecture",
                        architect=architect,
                        location=location,
                        tags=category_tags
                    ))
                except Exception as e:
                    print(f"  [WARN] 解析项目卡片失败: {e}")
                    continue

        except Exception as e:
            print(f"  [ERROR] ArchDaily 搜索失败: {e}")

        return results


class GoooodCrawler:
    """谷德设计网爬虫"""

    BASE_URL = "https://www.gooood.cn"
    API_URL = "https://www.gooood.cn/wp-json/gooood/v1"

    def __init__(self, timeout: int = 30):
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        })

    def get_latest(self, category: str = "architecture", limit: int = 20) -> list[ProjectItem]:
        """获取最新项目"""
        results = []

        # 分类映射
        category_map = {
            "architecture": "建筑",
            "landscape": "景观",
            "interior": "室内",
            "design": "设计"
        }

        try:
            # 尝试从分类页面获取
            url = f"{self.BASE_URL}/category/{category}"
            resp = self.session.get(url, timeout=self.timeout)
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, "html.parser")

            # 解析项目
            articles = soup.select("div.item-article")[:limit]

            for article in articles:
                try:
                    title_elem = article.select_one("h2 a")
                    if not title_elem:
                        continue

                    title = title_elem.get_text(strip=True)
                    url = urljoin(self.BASE_URL, title_elem.get("href", ""))

                    # 提取描述
                    desc_elem = article.select_one("div.excerpt")
                    description = desc_elem.get_text(strip=True) if desc_elem else None

                    # 提取分类标签
                    tags = [a.get_text(strip=True) for a in article.select("a[rel='category tag]")]

                    results.append(ProjectItem(
                        title=title,
                        source="gooood",
                        url=url,
                        category=category_map.get(category, "建筑"),
                        description=description,
                        tags=tags
                    ))
                except Exception as e:
                    print(f"  [WARN] 解析项目失败: {e}")
                    continue

        except Exception as e:
            print(f"  [ERROR] Gooood 抓取失败: {e}")

        return results


class DesignCNNewsCrawler:
    """设计中国资讯爬虫"""

    BASE_URL = "https://www.design.cn"
    NEWS_URL = "https://www.design.cn/info"

    def __init__(self, timeout: int = 30):
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        })

    def get_news(self, limit: int = 20) -> list[ProjectItem]:
        """获取最新资讯"""
        results = []

        try:
            resp = self.session.get(self.NEWS_URL, timeout=self.timeout)
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, "html.parser")

            items = soup.select("ul.news-list li")[:limit]

            for item in items:
                try:
                    title_elem = item.select_one("a")
                    if not title_elem:
                        continue

                    title = title_elem.get_text(strip=True)
                    url = urljoin(self.BASE_URL, title_elem.get("href", ""))

                    # 提取日期
                    date_elem = item.select_one("span.date")
                    date_str = date_elem.get_text(strip=True) if date_elem else None

                    results.append(ProjectItem(
                        title=title,
                        source="design.cn",
                        url=url,
                        category="资讯",
                        year=self._parse_year(date_str)
                    ))
                except Exception as e:
                    print(f"  [WARN] 解析资讯失败: {e}")
                    continue

        except Exception as e:
            print(f"  [ERROR] DesignCN 抓取失败: {e}")

        return results

    def _parse_year(self, date_str: str) -> Optional[int]:
        """从日期字符串提取年份"""
        if not date_str:
            return None
        match = re.search(r"(20\d{2})", date_str)
        return int(match.group(1)) if match else None


def save_results(items: list[ProjectItem], output_dir: Path):
    """保存采集结果"""
    output_dir.mkdir(parents=True, exist_ok=True)

    # 保存 JSON
    json_path = output_dir / f"scraped_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump([asdict(item) for item in items], f, ensure_ascii=False, indent=2)

    print(f"  [OK] 保存到: {json_path}")

    # 追加到总库
    all_path = output_dir / "all_scraped.json"
    if all_path.exists():
        with open(all_path, "r", encoding="utf-8") as f:
            existing = json.load(f)
    else:
        existing = []

    existing.extend([asdict(item) for item in items])

    with open(all_path, "w", encoding="utf-8") as f:
        json.dump(existing, f, ensure_ascii=False, indent=2)

    print(f"  [OK] 累计: {len(existing)} 条")


def main():
    import argparse

    parser = argparse.ArgumentParser(description="建筑景观室内网站数据采集器")
    parser.add_argument("--source", choices=["archdaily", "gooood", "designcn", "all"], default="all")
    parser.add_argument("--category", default="architecture", help="分类 (architecture/landscape/interior)")
    parser.add_argument("--limit", type=int, default=20, help="采集数量")
    parser.add_argument("--output", default="data/raw/web_scraped", help="输出目录")

    args = parser.parse_args()

    if not DEPENDENCIES_AVAILABLE:
        print("[ERROR] 需要安装依赖: pip install requests beautifulsoup4")
        return

    output_dir = Path(__file__).parent.parent / args.output
    items = []

    if args.source in ["archdaily", "all"]:
        print("[INFO] 采集 ArchDaily...")
        crawler = ArchDailyCrawler()
        items.extend(crawler.search(limit=args.limit))

    if args.source in ["gooood", "all"]:
        print("[INFO] 采集 Gooood...")
        crawler = GoooodCrawler()
        items.extend(crawler.get_latest(category=args.category, limit=args.limit))

    if args.source in ["designcn", "all"]:
        print("[INFO] 采集 DesignCN...")
        crawler = DesignCNNewsCrawler()
        items.extend(crawler.get_news(limit=args.limit))

    print(f"\n[INFO] 共采集 {len(items)} 条数据")

    if items:
        save_results(items, output_dir)


if __name__ == "__main__":
    main()
