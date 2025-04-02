.PHONY: convert-to-geotiff

default: help

convert-to-geotiff:  ## Convert ISCE2 results to GeoTIFF
	python src/convert_to_geotiff.py \
	--input-dir ${INPUT_DIR} \
	$(if ${OUTPUT_DIR}, --output-dir ${OUTPUT_DIR})

help:  ## Display this help message
	@echo "Usage: make <target>"
	@echo "Targets:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

