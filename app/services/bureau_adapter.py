from typing import Optional
import logging

logger = logging.getLogger(__name__)


class BureauAdapter:
    async def fetch_credit_score(self, pan: str) -> Optional[int]:
        logger.info(f"Bureau adapter: Fetching credit score for PAN: {pan}")
        return 750


bureau_adapter = BureauAdapter()
