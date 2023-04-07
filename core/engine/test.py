import logging

FORMAT = '%(asctime)s %(clientip)-15s %(user)-8s %(message)s'
logging.basicConfig(level=logging.NOTSET)
logger = logging.getLogger('tcpserver')
logger.debug('Protocol problem: %s', 'connection reset')
component_logger = logger.getChild("component-a")
component_logger.info("this will get printed with the prefix `my-app.component-a`")