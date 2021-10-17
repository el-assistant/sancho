from tree_sitter import Language, Parser


def main():
    Language.build_library("languages.so", ["./resources/tree-sitter-python"])
