def finish_span(span_name):
    return '{0}->Finish();'.format(span_name)


def pre_curl_easy_perform(arguments, span_name):
    return 'auto {0} = tracer->StartSpan("curl.request");'.format(span_name)


def post_curl_easy_perform(arguments, span_name):
    # first argument is the functionName
    curl_handle = arguments[1]
    return '{0}->SetTag("resource", ((Curl_easy*){1})->change.url);'.format(span_name, curl_handle)


def pre_call(arguments, span_name):
    return ''


def post_call(arguments, span_name):
    return ''


class Instrumenter:

    def __init__(self):
        self.defs = {
            'curl_easy_perform': (
                pre_curl_easy_perform,
                post_curl_easy_perform
            ),
        }

    def instrument(self, arguments, span_name):
        function_name = arguments[0]
        pre, post = self.defs.get(function_name, (pre_call, post_call))
        return pre(arguments, span_name), post(arguments, span_name), finish_span(span_name)
