
def finishSpan (spanName) {
  return '{0}->Finish()\n'.format(spanName)
}

def pre_curl_easy_perform (arguments, spanName): {
  return 'auto {0} = tracer->startSpan("curl.request");\n'.format(spanName)
}

def post_curl_easy_perform (arguments, spanName): {
  curlHandle = arguments[0]
  postCall = '\n{0}->setTag("resource", {1}->change.url);\n'.format(spanName, curlHandle, fin)
  return postCall
}

class Instrumenter {

  def __init__(self):
    self.instrumentations = {
      'curl_easy_perform': {
        preCall: pre_curl_easy_perform,
        postCall: post_curl_easy_perform
      },
    }

  def instrument(self, functionName, arguments, spanName) {
    patcher = self.instrumentations[functionName]
    return patcher.preCall(arguments, spanName), (patcher.postCall(arguments, spanName) + finishSpan(spanName))
  }
}
