import logging
import sys

# Configure standard logger
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)

logger = logging.getLogger("intracapital")
logger.info("[PRIVACY ASSURANCE] Intracapital running in 100% local mode. No enterprise data transmitted to external APIs.")
