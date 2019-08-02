#include <assert.h>
#include <curl/curl.h>
#include <datadog/opentracing.h>
#include <iostream>
#include <ostream>
#include <string>

static std::shared_ptr<ot::Tracer> tracer;

void my_curl(void *curl) {
  auto span_c = tracer->StartSpan("C");
  span_c->SetTag("tag", 123);
  curl_easy_setopt(curl, CURLOPT_URL, "https://nytimes.com");

  /* Perform the request, res will get the return code */
  CURLcode res = curl_easy_perform(curl);
  /* Check for errors */
  if (res != CURLE_OK)
    fprintf(stderr, "curl_easy_perform() failed: %s\n", curl_easy_strerror(res));

  span_c->Finish();
}


int main(int argc, char* argv[]) {
  CURL* curl;
  CURLcode res;
  datadog::opentracing::TracerOptions tracer_options{"dd-agent", 8126, "compiled-in example"};
  tracer_options.auto_instrument = true;
  tracer = datadog::opentracing::makeTracer(tracer_options);

  // Create some spans.
  auto span_a = tracer->StartSpan("A");
  span_a->SetTag("tag", 123);
  auto span_b = tracer->StartSpan("B", {opentracing::ChildOf(&span_a->context())});
  span_b->SetTag("tag", "value");

  curl = curl_easy_init();
  if (curl) {
    FILE* devnull = fopen("/dev/null", "w+");

    curl_easy_setopt(curl, CURLOPT_URL, "https://google.com");
    /* example.com is redirected, so we tell libcurl to follow redirection */
    curl_easy_setopt(curl, CURLOPT_FOLLOWLOCATION, 1L);
    curl_easy_setopt(curl, CURLOPT_WRITEDATA, devnull);

    /* Perform the request, res will get the return code */
    res = curl_easy_perform(curl);
    /* Check for errors */
    if (res != CURLE_OK)
      fprintf(stderr, "curl_easy_perform() failed: %s\n", curl_easy_strerror(res));

    curl_easy_setopt(curl, CURLOPT_URL, "https://nytimes.com");

    /* Perform the request, res will get the return code */
    res = curl_easy_perform(curl);
    /* Check for errors */
    if (res != CURLE_OK)
      fprintf(stderr, "curl_easy_perform() failed: %s\n", curl_easy_strerror(res));

    /* Custom function */
    my_curl(curl);

    /* always cleanup */
    curl_easy_cleanup(curl);

    fclose(devnull);
  }

  span_a->Finish();
  span_b->Finish();
  tracer->Close();
  return 0;
}
