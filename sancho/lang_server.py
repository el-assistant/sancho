def main():
    from pygls.server import LanguageServer
    from loguru import logger

    server = LanguageServer()
    host = "127.0.0.1"
    port = 8080
    logger.info(f"Starting language server on {host=} {port=}")
    server.start_tcp("127.0.0.1", 8080)
