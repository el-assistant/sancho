"""
Function main is exposed as a command in project.toml.
"""
from pygls.server import LanguageServer
import pygls.lsp.types as t
import pygls.lsp.methods as feat
from loguru import logger
from sancho.parsing import get_python_parser

parser = get_python_parser()
server = LanguageServer()
parsed_files = dict()


def parse_string(text: str):
    text = bytes(text, "utf-8")
    return parser.parse(text)


@server.feature("workspace/didChangeConfiguration")
def didChangeConfiguration(ls, params):
    logger.info(params)


@server.feature("textDocument/completion")
def completion(ls, params):
    logger.info(params)


@server.feature("textDocument/didOpen")
def didopen(ls, params: t.DidOpenTextDocumentParams):
    logger.info(params)

    parsed_files[params.text_document.uri] = parse_string(params.text_document.text)


@server.feature(feat.TEXT_DOCUMENT_DID_CHANGE)
def didchange(ls, params: t.DidChangeTextDocumentParams):
    logger.info(params)
    parsed = parsed_files[params.text_document.uri]
    changes = params.content_changes
    for c in changes:
        c: t.TextDocumentContentChangeEvent
        c.text, c.range
        # NOTE: LSP use line and col starting at 0


def main():
    """Run Language Server as http"""

    host = "127.0.0.1"
    port = 8080
    logger.info(f"Starting language server on {host=} {port=}")
    server.start_tcp(host, port)
