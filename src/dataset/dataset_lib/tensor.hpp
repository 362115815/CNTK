#pragma once

#include "dataset.hpp"

#include <string>
#include <vector>

// Performs decompression of the input data described with in_* parameters and stores result in out buffer.
// Caller is responsible for allocating enough memory for out buffer (at least out_channels * out_height * out_width).
void DecompressTensor(
  const char* in,
  int in_size,
  int out_channels,
  int out_height,
  int out_width,
  float* out);

// Reads tensor data from given input file, serializes it to given output file buffer, and populates
// given channelset and channelset instance descriptors accordingly.
void TensorSerialize(
  const std::string& in_file_path,
  std::vector<unsigned char>& file_buffer,
  ChannelSet& channelset_desc,
  ChannelSetInstance& channelset_inst);