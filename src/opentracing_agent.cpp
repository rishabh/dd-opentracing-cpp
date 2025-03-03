// Implementation of the exposed makeTracer function.
// This is kept separately to isolate the AgentWriter and its cURL dependency.
// Users of the library that do not use this tracer are able to avoid the
// additional dependency and implementation details.

#include <datadog/opentracing.h>
#include "agent_writer.h"
#include "instrumenter.h"
#include "sample.h"
#include "stdio.h"
#include "tracer.h"
#include "tracer_options.h"

namespace ot = opentracing;

namespace datadog {
namespace opentracing {

static std::shared_ptr<ot::Tracer> tracer_auto_instrument = nullptr;

std::shared_ptr<ot::Tracer> makeTracer(const TracerOptions &options) {
  static bool auto_tracer = false;
  auto maybe_options = applyTracerOptionsFromEnvironment(options);
  if (!maybe_options) {
    std::cerr << "Error applying TracerOptions from environment variables: "
              << maybe_options.error() << std::endl
              << "Tracer will be started without options from the environment" << std::endl;
    maybe_options = options;
  }
  TracerOptions opts = maybe_options.value();

  std::shared_ptr<SampleProvider> sampler = sampleProviderFromOptions(opts);
  auto writer = std::shared_ptr<Writer>{
      new AgentWriter(opts.agent_host, opts.agent_port,
                      std::chrono::milliseconds(llabs(opts.write_period_ms)), sampler)};
  auto tracer = std::shared_ptr<ot::Tracer>{new Tracer{opts, writer, sampler}};

  if (opts.auto_instrument) {
    if (auto_tracer) {
      throw "Can only set up one instrumenter";
    }
    // datadog::opentracing::setupInstrumenter(tracer);
    auto_tracer = true;
  }

  return tracer;
}
}  // namespace opentracing
}  // namespace datadog
