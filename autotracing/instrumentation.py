def finishSpan(spanName):
    return '{0}->Finish();'.format(spanName)


def pre_curl_easy_perform(arguments, spanName):
    return 'auto {0} = tracer->startSpan("curl.request");'.format(spanName)


def post_curl_easy_perform(arguments, spanName):
    # first argument is the functionName
    curlHandle = arguments[1]
    postCall = '{0}->setTag("resource", {1}->change.url);'.format(spanName, curlHandle)
    return postCall


def pre_call(arguments, span_name):
    return ''


def post_call(arguments, span_name):
    return ''


class Instrumenter:

    def __init__(self):
        self.instrumentations = {
            'curl_easy_perform': (
                pre_curl_easy_perform,
                post_curl_easy_perform
            ),
        }

    def instrument(self, arguments, spanName):
        functionName = arguments[0]
        pre, post = self.instrumentations.get(functionName, (pre_call, post_call))
        return pre(arguments, spanName), post(arguments, spanName), finishSpan(spanName)
