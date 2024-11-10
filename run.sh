#!/bin/bash

# Run npm run dev in the background
npm run dev &

# Run python3 api/main.py in the background
python3 api/main.py &

# Wait for both processes to finish
wait

echo "Both processes have finished"