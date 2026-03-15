"""
Dependency Injection Container

This module configures the dependency injection container using the
dependency-injector library. It wires all dependencies and enforces
the Dependency Inversion Principle.

SOLID Principles:
- DIP: Binds interfaces to implementations
- SRP: Each provider creates one type of object
- OCP: New implementations can be added without modifying existing code
"""

from dependency_injector import containers, providers
from app.config import config


class Container(containers.DeclarativeContainer):
    """
    Dependency Injection Container
    
    This container manages all application dependencies and their lifecycles.
    It ensures loose coupling between layers and enables easy testing through
    dependency substitution.
    
    Layer Organization:
    1. Configuration and Infrastructure
    2. Domain Layer (repositories, services)
    3. Application Layer (use cases)
    4. Presentation Layer (API routes, UI components)
    """
    
    # ============================================
    # Configuration
    # ============================================
    
    # Configuration is provided as a singleton
    app_config = providers.Singleton(lambda: config)
    
    # ============================================
    # Infrastructure Layer - Database
    # ============================================
    
    # Database connection will be implemented in task 5
    # database = providers.Singleton(
    #     DatabaseConnection,
    #     connection_string=app_config.provided.database.connection_string
    # )
    
    # ============================================
    # Infrastructure Layer - Repository Implementations
    # ============================================
    
    # Repositories will be implemented in task 5
    # user_repository = providers.Factory(
    #     PostgresUserRepository,
    #     db_connection=database
    # )
    
    # report_repository = providers.Factory(
    #     PostgresReportRepository,
    #     db_connection=database
    # )
    
    # parameter_repository = providers.Factory(
    #     PostgresParameterRepository,
    #     db_connection=database
    # )
    
    # normalized_parameter_repository = providers.Factory(
    #     PostgresNormalizedParameterRepository,
    #     db_connection=database
    # )
    
    # ============================================
    # Infrastructure Layer - External Service Adapters
    # ============================================
    
    # Adapters will be implemented in task 6
    # lab_report_parser = providers.Factory(
    #     LabReportParserAdapter
    # )
    
    # normalize_lab_data_tool = providers.Factory(
    #     NormalizeLabDataAdapter
    # )
    
    # google_oauth_client = providers.Factory(
    #     GoogleOAuthAdapter,
    #     client_id=app_config.provided.oauth.client_id,
    #     client_secret=app_config.provided.oauth.client_secret,
    #     redirect_uri=app_config.provided.oauth.redirect_uri
    # )
    
    # file_storage_service = providers.Factory(
    #     FileStorageService,
    #     upload_path=app_config.provided.storage.upload_path,
    #     max_file_size_mb=app_config.provided.storage.max_file_size_mb,
    #     allowed_extensions=app_config.provided.storage.allowed_extensions
    # )
    
    # pdf_exporter_service = providers.Factory(
    #     PDFExporterService
    # )
    
    # translation_service = providers.Factory(
    #     TranslationService,
    #     supported_languages=app_config.provided.i18n.supported_languages
    # )
    
    # ============================================
    # Domain Layer - Domain Services
    # ============================================
    
    # Domain services will be implemented in task 4
    # report_processing_service = providers.Factory(
    #     ReportProcessingService,
    #     report_repository=report_repository,
    #     parameter_repository=parameter_repository,
    #     parser_adapter=lab_report_parser,
    #     normalizer_adapter=normalize_lab_data_tool
    # )
    
    # risk_analysis_service = providers.Factory(
    #     RiskAnalysisService,
    #     parameter_repository=parameter_repository,
    #     normalized_parameter_repository=normalized_parameter_repository
    # )
    
    # trend_calculation_service = providers.Factory(
    #     TrendCalculationService,
    #     parameter_repository=parameter_repository,
    #     normalized_parameter_repository=normalized_parameter_repository
    # )
    
    # recommendation_service = providers.Factory(
    #     RecommendationService,
    #     risk_analysis_service=risk_analysis_service,
    #     translation_service=translation_service
    # )
    
    # ============================================
    # Application Layer - Use Cases
    # ============================================
    
    # Use cases will be implemented in task 8
    # upload_report_use_case = providers.Factory(
    #     UploadReportUseCase,
    #     file_storage=file_storage_service,
    #     user_repository=user_repository
    # )
    
    # process_report_use_case = providers.Factory(
    #     ProcessReportUseCase,
    #     report_processing_service=report_processing_service,
    #     report_repository=report_repository
    # )
    
    # retrieve_history_use_case = providers.Factory(
    #     RetrieveHistoryUseCase,
    #     report_repository=report_repository,
    #     user_repository=user_repository
    # )
    
    # generate_trends_use_case = providers.Factory(
    #     GenerateTrendsUseCase,
    #     trend_calculation_service=trend_calculation_service,
    #     parameter_repository=parameter_repository
    # )
    
    # calculate_risk_use_case = providers.Factory(
    #     CalculateRiskUseCase,
    #     risk_analysis_service=risk_analysis_service
    # )
    
    # export_report_use_case = providers.Factory(
    #     ExportReportUseCase,
    #     pdf_exporter=pdf_exporter_service,
    #     report_repository=report_repository,
    #     translation_service=translation_service
    # )


# Global container instance
container = Container()
