# T-CTRL / ISCI — reproducible entry points
# The validated method runs from one command. Heavy raw data stays outside Git;
# the locked result is reproduced from committed rankings + the isci-controllership skill.

PY ?= python

.PHONY: reproduce-core dashboard cci tensor hackathon-package hackathon-check clean-cache help

help:
	@echo "make reproduce-core  - run the CCI test across the dataset registry + build the dashboard"
	@echo "make cci             - run isci/run_cci.py over config/datasets.yaml (writes outputs/<id>/cci_result.json)"
	@echo "make dashboard       - regenerate outputs/dashboard/ (HTML + static forest plot) from committed results"
	@echo "make hackathon-package - rebuild and validate the complete offline stage package"
	@echo "make hackathon-check   - run automated package readiness gates only"

# One command: run the validated CCI method across all registered datasets, then visualize.
reproduce-core: cci dashboard
	@echo ""
	@echo "Core reproduced. Locked anchor: Marson CD4+ PASS (authoritative M->M+C gain +0.357, result_lock.md)."
	@echo "Cross-system matched comparator: dAUPRC +0.229 [0.072,0.405]."
	@echo "Method smoke-test: outputs/marson_cd4/cci_method_check.json ; dashboard: outputs/dashboard/"

tensor:
	$(PY) isci/run_layer.py

cci:
	$(PY) isci/run_cci.py

dashboard:
	$(PY) isci/build_dashboard.py

hackathon-package:
	$(PY) scripts/build_hackathon_claim_manifest.py
	$(PY) scripts/capture_hackathon_screenshots.py
	$(PY) scripts/build_hackathon_demo.py
	$(PY) scripts/build_hackathon_video.py
	$(PY) scripts/check_hackathon_readiness.py

hackathon-check:
	$(PY) scripts/check_hackathon_readiness.py

clean-cache:
	find isci -name __pycache__ -type d -prune -exec rm -rf {} +
