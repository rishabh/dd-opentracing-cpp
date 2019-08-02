import clang.cindex as cindex
import re


class Parser(object):

    ws_regex = re.compile(r"\s*")

    def __init__(self, filename, lib_path=None, args=None):
        self.filename = filename
        if lib_path is not None:
            cindex.Config.set_library_path(lib_path)
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
            # clang 1-indexes the source files
            self.func_calls[node.location.line - 1] = node.displayname

        for child in node.get_children():
            self.visit(child)

    def start_span(self, ws=''):
        return "{0}auto dd_auto_span{1} = tracer->StartSpan(\"resource\");\n".format(ws, self.span_num)

    def tag_span(self, name, ws=''):
        return "{0}dd_auto_span{1}->SetTag(\"function\", \"{2}\");\n".format(ws, self.span_num, name)

    def stop_span(self, ws=''):
        span_num = self.span_num
        self.span_num += 1
        return "\n{0}dd_auto_span{1}->Finish();\n".format(ws, span_num)

    def generate(self):
        with open(self.filename) as fp:
            lines = fp.read().split("\n")

        for idx, name in self.func_calls.items():
            m = self.ws_regex.match(lines[idx])
            ws = m.group(0)
            lines[idx] = self.start_span(ws) + self.tag_span(name, ws) + lines[idx] + self.stop_span(ws)

        return "\n".join(lines)


if __name__ == "__main__":
    ex_dir = "/Users/taylor.burmeister/hackathon/dd-opentracing-cpp/examples/"
    parser = Parser(
        ex_dir + "cpp-tracing/automated_tracing_curl/tracer_example.cpp",
        "/usr/local/opt/llvm/lib",
        ["-I/usr/local/Cellar/curl/7.65.3/include"]
    )
    parser.parse()
    print(parser.generate())
