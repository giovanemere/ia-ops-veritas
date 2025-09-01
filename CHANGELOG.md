# Changelog

All notable changes to this project will be documented in this file.

## [1.0.0] - 2025-09-01

### Added
- **Main Portal** (port 8845): Unified dashboard for all services
- **Complete service architecture**: All 5 services now fully implemented
- **Docker containers**: Individual Dockerfiles for each service
- **Management scripts**:
  - `logs.sh`: View logs from all services
  - `show-urls.sh`: Display all service URLs
  - `status.sh`: Check service health
  - `stop.sh`: Stop all services
  - `test-demo.sh`: Run demonstration tests
- **HTML templates**: User interfaces for all services
- **Enhanced APIs**: Improved functionality for all endpoints

### Changed
- Updated `docker-compose.yml` with all service definitions
- Enhanced `start.sh` script with better service management
- Improved `test_manager.py` and `test_execution_engine.py` APIs

### Services
- **Main Portal** (8845): Central dashboard and navigation
- **Test Manager** (8870): Test case management
- **Test Execution Engine** (8871): Test execution and automation
- **Quality Analytics** (8872): Quality metrics and analysis
- **Evidence Manager** (8873): Evidence storage and reporting

### Integration
- Full integration with IA-Ops ecosystem
- MinIO storage for evidence and reports
- Dev Core API connections
- Centralized logging and monitoring
