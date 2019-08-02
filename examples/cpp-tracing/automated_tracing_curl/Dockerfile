FROM ubuntu:18.04

RUN apt-get update && \
  apt-get -y install build-essential cmake wget libcurl4-openssl-dev git clang python3 python3-pip

# Download and install dd-opentracing-cpp library.
RUN git clone https://github.com/rishabh/dd-opentracing-cpp.git && \
  mkdir -p dd-opentracing-cpp/.build && \
  cd dd-opentracing-cpp/.build && \
  # Download and install the correct version of opentracing-cpp, & other deps.
  ../scripts/install_dependencies.sh && \
  cmake .. && \
  make && \
  make install

RUN mkdir src
COPY tracer_example.cpp src
COPY parser.py .

RUN ln -s /usr/lib/llvm-6.0/lib/libclang.so.1 /usr/lib/llvm-6.0/lib/libclang.so
RUN pip3 install clang && python3 parser.py src -o traced -L /usr/lib/llvm-6.0/lib

RUN g++ -std=c++14 -o tracer_example traced/tracer_example.cpp -ldd_opentracing -lopentracing -lcurl
# Add /usr/local/lib to LD_LIBRARY_PATH
RUN ldconfig

# RUN objdump -x tracer_example

CMD sleep 5 && ./tracer_example && sleep 25
