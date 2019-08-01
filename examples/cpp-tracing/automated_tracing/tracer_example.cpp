#include <assert.h>
#include <datadog/opentracing.h>
#include <boost/crc.hpp>
#include <boost/cstdint.hpp>
#include <iostream>
#include <ostream>
#include <string>

int main(int argc, char* argv[]) {
  datadog::opentracing::TracerOptions tracer_options{"dd-agent", 8126, "compiled-in example"};
  auto tracer = datadog::opentracing::makeTracer(tracer_options);

  // Create some spans.
  {
    auto span_a = tracer->StartSpan("A");
    span_a->SetTag("tag", 123);
    auto span_b = tracer->StartSpan("B", {opentracing::ChildOf(&span_a->context())});
    span_b->SetTag("tag", "value");
  }

  using boost::augmented_crc;
  using boost::uint16_t;

  uint16_t data[6] = {2, 4, 31, 67, 98, 0};
  uint16_t const init_rem = 0x123;

  uint16_t crc1 = augmented_crc<16, 0x8005>(data, sizeof(data), init_rem);

  uint16_t const zero = 0;
  uint16_t const new_init_rem = augmented_crc<16, 0x8005>(&zero, sizeof(zero));

  boost::crc_basic<16> crc2(0x8005, new_init_rem);
  crc2.process_block(data, &data[5]);

  assert(crc2.checksum() == crc1);

  std::cout << "All tests passed." << std::endl;

  tracer->Close();

  return 0;
}
