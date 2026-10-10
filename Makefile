.PHONY: help test lint assess fmt plan-pair-a plan-pair-b clean

PYTHON ?= python3
TERRAFORM ?= terraform

help:
	@echo "F5 iSeries to rSeries (4x r5900) Automation CLI"
	@echo "Targets:"
	@echo "  test         - Run Python unit test suite for assessment engine"
	@echo "  lint         - Check formatting and lint Terraform modules"
	@echo "  fmt          - Format all Terraform files"
	@echo "  assess       - Run assessment CLI against sample fixture"
	@echo "  plan-pair-a  - Dry-run Terraform plan for Pair-A chassis"
	@echo "  plan-pair-b  - Dry-run Terraform plan for Pair-B chassis"
	@echo "  clean        - Remove temporary artifacts and assessment output"

test:
	$(PYTHON) -m unittest discover -s tests/unit

lint:
	$(TERRAFORM) fmt -check -recursive
	@echo "Terraform formatting check passed."

fmt:
	$(TERRAFORM) fmt -recursive

assess:
	$(PYTHON) tools/assessment/run_assessment.py --config tests/fixtures/legacy_iseries_bigip.conf --model i5800 --output tests/assessment_output

clean:
	rm -rf tests/assessment_output/
	find . -type d -name ".terraform" -exec rm -rf {} +
	find . -type f -name "*.tfstate*" -delete
