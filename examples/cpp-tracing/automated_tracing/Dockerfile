FROM ubuntu:18.04

WORKDIR /usr/container

RUN apt-get update && \
  apt-get -y install build-essential cmake wget libboost-all-dev git

# Download and install dd-opentracing-cpp library.
RUN git clone https://github.com/rishabh/dd-opentracing-cpp.git && \
  mkdir -p dd-opentracing-cpp/.build && \
  cd dd-opentracing-cpp/.build && \
  # Download and install the correct version of opentracing-cpp, & other deps.
  ../scripts/install_dependencies.sh && \
  cmake .. && \
  make && \
  make install

COPY tracer_example.cpp .

RUN g++ -std=c++14 -o tracer_example tracer_example.cpp -ldd_opentracing -lopentracing
# Add /usr/local/lib to LD_LIBRARY_PATH
RUN ldconfig

CMD sleep 5 && ./tracer_example && sleep 25
