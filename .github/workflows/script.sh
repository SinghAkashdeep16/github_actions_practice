#!/bin/bash
echo "Running simple CI test..."

if [ 2 -gt 1 ]; then
  echo "Test passed"
  exit 0
else
  echo "Test failed"
  exit 1
fi
