#!/bin/bash
set -e

# Get the directory of this script
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd "$DIR"

echo "=================================================="
echo " Building Docker Image (kingsley-sim)"
echo "=================================================="
docker build -t kingsley-sim .

echo ""
echo "=================================================="
echo " Running Kingsley Multiple Embedding Simulation"
echo "=================================================="
# Mount the directory so ./hasil is written back to the host.
docker run --rm -v "$DIR":/app kingsley-sim

echo ""
echo "=================================================="
echo " Simulation Complete! Results in ./hasil:"
echo " - hasil_simulasi.md"
echo " - simulation_result.png, robustness_examples.png"
echo " - stego.png, agreed_stego.png, recovered_secret.png"
echo "=================================================="
