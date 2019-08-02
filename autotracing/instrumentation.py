
def finishSpan (spanName):
  return '{0}->Finish()\n'.format(spanName)


def pre_curl_easy_perform (arguments, spanName):
  return 'auto {0} = tracer->startSpan("curl.request");\n'.format(spanName)

def post_curl_easy_perform (arguments, spanName):
  # first argument is the functionName
  curlHandle = arguments[1]
  postCall = '\n{0}->setTag("resource", {1}->change.url);\n'.format(spanName, curlHandle, fin)
  return postCall


class Instrumenter:

  def __init__(self):
    self.instrumentations = {
      'curl_easy_perform': {
        preCall: pre_curl_easy_perform,
        postCall: post_curl_easy_perform
      },
    }

  def instrument(self, arguments, spanName):
    functionName = arguments[0]
    patcher = self.instrumentations[functionName]
    return patcher.preCall(arguments, spanName), (patcher.postCall(arguments, spanName) + finishSpan(spanName))
