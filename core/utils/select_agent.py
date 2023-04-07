import sys
from logging import getLogger
logger = getLogger(__name__)

def select_agent():
    if len(sys.argv) > 1:
        agent = sys.argv[1]
    else: agent = "ab"

    if agent not in {"ab", "az", "abz"}:
        logger.error(f"Unknown agent '{agent}'. Selected Agent must be in 'ab', 'az', 'abz'.")
        logger.info("Using Alpha-Beta agent as default.")
        agent = "ab"

    logger.info(f"You selected agent '{agent}'.")
    
    return agent