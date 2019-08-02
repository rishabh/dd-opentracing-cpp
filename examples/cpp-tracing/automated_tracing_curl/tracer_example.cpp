#include <assert.h>
#include <curl/curl.h>
#include <datadog/opentracing.h>
#include <iostream>
#include <ostream>
#include <string>

void function_pt(void* ptr, size_t size, size_t nmemb, void* stream) {}

int main(int argc, char* argv[]) {
  CURL* curl;
  CURLcode res;
  datadog::opentracing::TracerOptions tracer_options{"dd-agent", 8126, "compiled-in example"};
  tracer_options.auto_instrument = true;
  auto tracer = datadog::opentracing::makeTracer(tracer_options);

  // Create some spans.
  auto span_a = tracer->StartSpan("A");
  span_a->SetTag("tag", 123);
  auto span_b = tracer->StartSpan("B", {opentracing::ChildOf(&span_a->context())});
  span_b->SetTag("tag", "value");

  curl = curl_easy_init();
  if (curl) {
    curl_easy_setopt(curl, CURLOPT_URL, "https://google.com");
    /* example.com is redirected, so we tell libcurl to follow redirection */
    curl_easy_setopt(curl, CURLOPT_FOLLOWLOCATION, 1L);
    // pass the result string to a function
    curl_easy_setopt(curl, CURLOPT_WRITEFUNCTION, function_pt);

    /* Perform the request, res will get the return code */
    res = curl_easy_perform(curl);
    /* Check for errors */
    if (res != CURLE_OK)
      fprintf(stderr, "curl_easy_perform() failed: %s\n", curl_easy_strerror(res));

    /* always cleanup */
    curl_easy_cleanup(curl);
  }

  tracer->Close();
  return 0;
}
