def finish_span(span_name):
    return '{0}->Finish();'.format(span_name)


curl_easy_perform_resource = ""

def pre_curl_easy_perform(arguments, span_name):
    return 'auto {0} = tracer->StartSpan("curl.request");'.format(span_name)


def post_curl_easy_perform(arguments, span_name):
    # first argument is the functionName
    curl_handle = arguments[1]
    return '{0}->SetTag("resource", "{1}");'.format(span_name, curl_easy_perform_resource)


def pre_curl_easy_setopt(arguments, span_name):
    global curl_easy_perform_resource
    option = arguments[2]
    print(arguments)
    if (option == "CURLOPT_URL"):
        curl_easy_perform_resource = arguments[3]
    return ''


def post_curl_easy_setopt(arguments, span_name):
    return ''


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
            'curl_easy_setopt': {
              pre_curl_easy_setopt,
              post_curl_easy_setopt
            }
        }

    def instrument(self, arguments, span_name):
        function_name = arguments[0]
        pre, post = self.defs.get(function_name, (pre_call, post_call))
        return pre(arguments, span_name), post(arguments, span_name), finish_span(span_name)
