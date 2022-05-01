#!/bin/bash
cd "$(dirname "$0")"
rclone copy "ALePIcons:/" "Renderer/Icons/"
rclone copy "ALePGeneratedImages:/" "Renderer/GeneratedImages/"
