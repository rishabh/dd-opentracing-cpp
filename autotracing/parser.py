import argparse
import clang.cindex as cindex
import os
import re
import subprocess
import sys

from instrumentation import Instrumenter


class Parser(object):

    ws_regex = re.compile(r"\s*")
    init = False

    def __init__(self, filename, lib_path=None, args=None):
        if not self.init and lib_path is not None:
            cindex.Config.set_library_path(lib_path)
            self.__class__.init = True

        self.filename = filename
        self.index = cindex.Index.create()
        self.func_calls = {}
        self.args = args or []
        self.span_num = 0

    def parse(self):
        tu = self.index.parse(self.filename, self.args)
        node = tu.cursor
        self.visit(node)

    def visit(self, node):
        if node.kind == cindex.CursorKind.CALL_EXPR:
            args = self.visit_args(node)

            # clang 1-indexes the source files
            self.func_calls[node.location.line - 1] = args

        for child in node.get_children():
            self.visit(child)

    def visit_args(self, node):
        if node.kind in (cindex.CursorKind.INTEGER_LITERAL,
                         cindex.CursorKind.FLOATING_LITERAL,
                         cindex.CursorKind.IMAGINARY_LITERAL,
                         cindex.CursorKind.STRING_LITERAL,
                         cindex.CursorKind.CHARACTER_LITERAL,):
            return [list(node.get_tokens())[0].spelling]
        elif node.kind == cindex.CursorKind.DECL_REF_EXPR:
            return [node.displayname]

        args = []
        for child in node.get_children():
            args.extend(self.visit_args(child))

        return args

    def start_span(self, ws=''):
        return "{0}auto dd_auto_span{1} = tracer->StartSpan(\"resource\");\n".format(ws, self.span_num)

    def tag_span(self, name, ws=''):
        return "{0}dd_auto_span{1}->SetTag(\"function\", \"{2}\");\n".format(ws, self.span_num, name)

    def stop_span(self, ws=''):
        span_num = self.span_num
        self.span_num += 1
        return "\n{0}dd_auto_span{1}->Finish();\n".format(ws, span_num)

    def generate(self):
        inst = Instrumenter()

        with open(self.filename) as fp:
            lines = fp.read().split("\n")

        for idx, args in self.func_calls.items():
            m = self.ws_regex.match(lines[idx])
            ws = m.group(0)
            # lines[idx] = self.start_span(ws) + self.tag_span(args[0], ws) + lines[idx] + self.stop_span(ws)
            start, post, finish = inst.instrument(args, "dd_auto_span{0}".format(self.span_num))
            out = lines[idx]
            if start:
                out = ws + start + "\n" + out + "\n" + ws + post + "\n" + ws + finish + "\n"
                self.span_num += 1

            lines[idx] = out

        return "\n".join(lines)


def parse_directory(dirname, out=None, lib_path=None, args=None):
    out = out or os.path.join(dirname, "out")
    p = subprocess.Popen(["find", dirname, "-name", "*.cpp"], stdout=subprocess.PIPE)
    output, err = p.communicate()
    assert err is None
    filenames = output.decode().strip().split()

    for filename in filenames:
        print("parsing: ", filename)
        parser = Parser(filename, lib_path=lib_path, args=args)
        parser.parse()
        output = os.path.join(out, filename.replace(dirname, '', 1).lstrip('/'))
        outdir = os.path.dirname(output)
        os.makedirs(outdir, exist_ok=True)
        with open(output, "w") as fp:
            fp.write(parser.generate())


def run_example():
    ex_dir = "/Users/taylor.burmeister/hackathon/dd-opentracing-cpp/examples/"
    parser = Parser(
        ex_dir + "cpp-tracing/automated_tracing_curl/tracer_example.cpp",
        "/usr/local/opt/llvm/lib",
        ["-I/usr/local/Cellar/curl/7.65.3/include"]
    )
    parser.parse()
    print(parser.generate())


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("directory")
    parser.add_argument("--out", "-o")
    parser.add_argument("--lib_path", "-L")
    parser.add_argument("--includes", "-I", nargs="*")
    args = parser.parse_args(sys.argv[1:])
    includes = ["-I{0}".format(include) for include in args.includes] if args.includes is not None else None
    parse_directory(args.directory, args.out, args.lib_path, includes)


if __name__ == "__main__":
    """
    Example usage:
    python parser.py ../examples/cpp-tracing/automated_tracing_curl \
        -L /usr/local/opt/llvm/lib -I /usr/local/Cellar/curl/7.65.3/include -o out
    """
    main()
