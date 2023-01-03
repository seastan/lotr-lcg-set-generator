#!/bin/bash
cd "$(dirname "$0")"
./env_test.sh || exit
rclone copy "ALePIcons:/" "Renderer/Icons/"
rclone copy "ALePGeneratedImages:/" "Renderer/GeneratedImages/"
