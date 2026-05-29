#!/bin/bash
set -e

# Get the directory of this script
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd "$DIR"

echo "=================================================="
echo " Building Docker Image (stego-sim)"
echo "=================================================="
docker build -t stego-sim .

echo ""
echo "=================================================="
echo " Running Steganography Simulation"
echo "=================================================="
# We mount the current directory as /app so output files (stego.png, simulation_result.png) are written back to the host.
# Because the source files are already in the image, this volume mount will allow Python to write output images directly to the host directory.
docker run --rm -v "$DIR":/app stego-sim

echo ""
echo "=================================================="
echo " Simulation Complete!"
echo " Results written to host directory:"
echo " - stego.png"
echo " - simulation_result.png"
echo "=================================================="
