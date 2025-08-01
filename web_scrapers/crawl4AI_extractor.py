from crawl4ai import AsyncWebCrawler, CrawlerRunConfig
from crawl4ai.markdown_generation_strategy import DefaultMarkdownGenerator
from crawl4ai.content_filter_strategy import PruningContentFilter
from web_scrapers import WebScraperUtils
import asyncio
from asyncio import TimeoutError, sleep
from config import get_service_logger


class Crawl4AIExtractor:
    def __init__(self):
        self.logger = get_service_logger("Crawl4AIExtractor")

    async def crawl4ai_scrape(
        self, url: str, max_retries: int = 3, timeout_sec: int = 30
    ):
        prune_filter = PruningContentFilter(
            threshold=0.4,
            threshold_type="dynamic",
            min_word_threshold=20,
        )
        md_generator = DefaultMarkdownGenerator(
            content_filter=prune_filter, options={"ignore_links": True}
        )
        config = CrawlerRunConfig(markdown_generator=md_generator)

        for attempt in range(1, max_retries + 1):
            try:
                async with AsyncWebCrawler() as crawler:
                    result = await crawler.arun(
                        url=url, config=config, timeout=timeout_sec
                    )
                if not result:
                    raise RuntimeError("Crawler returned no result")

                if not result.success:
                    raise RuntimeError(
                        f"Crawl failed with error: {result.error_message or 'unknown error'}"
                    )

                markdown_obj = result.markdown
                fit_md = getattr(markdown_obj, "fit_markdown", None)
                raw_md = getattr(markdown_obj, "raw_markdown", "")

                self.logger.debug(
                    f"Attempt {attempt}: raw_md length = {len(raw_md)}, fit_md length = {len(fit_md) if fit_md else 'None'}"
                )

                selected_md = fit_md if fit_md and len(fit_md) >= 100 else raw_md
                cleaned = WebScraperUtils.remove_links_images_ui_junk(selected_md)
                return cleaned

            except TimeoutError:
                self.logger.warning(
                    f"Attempt {attempt} timed out after {timeout_sec}s for URL: {url}"
                )
            except Exception as e:
                self.logger.error(f"Attempt {attempt} failed for URL {url}: {e}")

            # after last attempt
            if attempt < max_retries:
                await asyncio.sleep(2**attempt)  # exponential back-off

        self.logger.error(f"All {max_retries} crawl attempts failed for URL: {url}")
        return None
