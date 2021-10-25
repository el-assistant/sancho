"""
Function main is exposed as a command in project.toml.
"""
from sancho.defaults import *
from pygls.server import LanguageServer
import pygls.lsp.types as t
import pygls.lsp.methods as feat
from loguru import logger
from sancho.parsing import get_python_parser, tree_sitter

Text = list[str]
# TODO: change Text to array of chars
raw_texts: dict[str, Text] = dict()
parsed_files: dict[str, tree_sitter.Parser] = dict()


server = LanguageServer()
parser = get_python_parser()


@server.feature("workspace/didChangeConfiguration")
def didChangeConfiguration(ls, params):
    logger.info(params)


@server.feature("textDocument/completion")
def completion(ls, params):
    logger.info(params)


@server.feature("textDocument/didOpen")
def didopen(ls, params: t.DidOpenTextDocumentParams):
    logger.debug(params)

    uri = params.text_document.uri
    text = params.text_document.text
    parsed_files[uri] = parser.parse(bytes(text, "utf-8"))
    raw_texts[uri] = list(text)
    logger.debug(raw_texts[uri])


def _find_position(text: Text, position: t.Position):
    line_starts = locate(text, lambda c: c == "\n")
    line_starts = chain([-1], line_starts)
    logger.debug(f"{''.join(text)}")
    logger.debug(f"{position=}")
    line_index = nth(line_starts, position.line)
    logger.debug(f"{line_index=}")

    return line_index + position.character + 1


def _applychange(raw_text: Text, content_change: t.TextDocumentContentChangeEvent):
    """Apply changes in-place"""
    # Remove chars
    start = content_change.range.start
    range_length = content_change.range_length
    index = _find_position(raw_text, start)
    for _ in range(range_length):
        raw_text.pop(index)

    # Add chars
    new_text = content_change.text
    for char in reversed(new_text):
        raw_text.insert(index, char)

    return raw_text


@server.thread()
@server.feature(feat.TEXT_DOCUMENT_DID_CHANGE)
def didchange(ls, params: t.DidChangeTextDocumentParams):
    logger.info(params)

    uri = params.text_document.uri
    changes = params.content_changes
    parsed = parsed_files[uri]
    raw_text = raw_texts[uri]
    logger.info("".join(raw_text))
    for c in changes:
        raw_text = _applychange(raw_text, c)
    raw_texts[uri] = raw_text
    logger.info("".join(raw_text))
    parsed_files[uri] = parser.parse(bytes("".join(raw_text), encoding="utf-8"))

    # TODO:Implement incremental parsing here


def main():
    """Run Language Server as http"""

    host = "127.0.0.1"
    port = 8080
    logger.info(f"Starting language server on {host=} {port=}")
    server.start_tcp(host, port)
