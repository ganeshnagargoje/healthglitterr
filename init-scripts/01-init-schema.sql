-- Medical Health Review System Database Schema
-- PostgreSQL initialization script

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create enum types
CREATE TYPE user_role AS ENUM ('patient', 'caregiver', 'doctor', 'lab_admin');
CREATE TYPE validation_status AS ENUM ('valid', 'invalid', 'pending_review');
CREATE TYPE normalization_status AS ENUM ('pending', 'normalized', 'failed', 'flagged');
CREATE TYPE trend_direction AS ENUM ('increasing', 'decreasing', 'stable');
CREATE TYPE risk_level AS ENUM ('low', 'medium', 'high', 'critical');
CREATE TYPE workflow_stage AS ENUM ('gathering', 'analyzing', 'applying_policy', 'proposing_resolution', 'human_approval');
CREATE TYPE stage_status AS ENUM ('in_progress', 'completed', 'paused', 'failed');
CREATE TYPE approval_status AS ENUM ('pending', 'approved', 'rejected', 'modified');
CREATE TYPE normalization_operation AS ENUM ('unit_conversion', 'name_mapping', 'range_alignment');
CREATE TYPE operation_status AS ENUM ('success', 'failed', 'flagged');

-- Users table
CREATE TABLE users (
    user_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    role user_role NOT NULL,
    preferred_language VARCHAR(10) DEFAULT 'en',
    consent_status BOOLEAN DEFAULT FALSE,
    consent_timestamp TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Medical reports table
CREATE TABLE medical_reports (
    report_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    upload_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    report_date TIMESTAMP NOT NULL,
    file_path TEXT NOT NULL,
    lab_name VARCHAR(255),
    patient_id_on_report VARCHAR(100),
    validation_status validation_status DEFAULT 'pending_review',
    validation_errors TEXT[],
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Health parameters table
CREATE TABLE health_parameters (
    parameter_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    parameter_name VARCHAR(255) NOT NULL,
    value DECIMAL(10, 4) NOT NULL,
    unit VARCHAR(50),
    timestamp TIMESTAMP NOT NULL,
    source VARCHAR(20) CHECK (source IN ('report', 'manual')),
    report_id UUID REFERENCES medical_reports(report_id) ON DELETE SET NULL,
    confidence DECIMAL(3, 2) CHECK (confidence >= 0 AND confidence <= 1),
    normalization_status normalization_status DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Normalized parameters table
CREATE TABLE normalized_parameters (
    normalized_parameter_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    original_parameter_id UUID NOT NULL REFERENCES health_parameters(parameter_id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    canonical_name VARCHAR(255) NOT NULL,
    original_value DECIMAL(10, 4) NOT NULL,
    original_unit VARCHAR(50),
    normalized_value DECIMAL(10, 4) NOT NULL,
    standard_unit VARCHAR(50) NOT NULL,
    conversion_factor DECIMAL(10, 6),
    reference_range_min DECIMAL(10, 4),
    reference_range_max DECIMAL(10, 4),
    normalized_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    normalization_confidence DECIMAL(3, 2) CHECK (normalization_confidence >= 0 AND normalization_confidence <= 1)
);

-- Normalization audit log table
CREATE TABLE normalization_audit_logs (
    audit_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    parameter_id UUID NOT NULL REFERENCES health_parameters(parameter_id) ON DELETE CASCADE,
    normalized_parameter_id UUID REFERENCES normalized_parameters(normalized_parameter_id) ON DELETE SET NULL,
    operation normalization_operation NOT NULL,
    status operation_status NOT NULL,
    original_value DECIMAL(10, 4) NOT NULL,
    original_unit VARCHAR(50),
    original_name VARCHAR(255) NOT NULL,
    normalized_value DECIMAL(10, 4),
    standard_unit VARCHAR(50),
    canonical_name VARCHAR(255),
    conversion_factor DECIMAL(10, 6),
    failure_reason TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Trends table
CREATE TABLE trends (
    trend_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    parameter_name VARCHAR(255) NOT NULL,
    direction trend_direction NOT NULL,
    start_date TIMESTAMP NOT NULL,
    end_date TIMESTAMP NOT NULL,
    slope DECIMAL(10, 6),
    confidence DECIMAL(3, 2) CHECK (confidence >= 0 AND confidence <= 1),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Risk flags table
CREATE TABLE risk_flags (
    risk_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    parameter_name VARCHAR(255) NOT NULL,
    risk_level risk_level NOT NULL,
    description TEXT,
    trend_id UUID REFERENCES trends(trend_id) ON DELETE SET NULL,
    detected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    requires_human_approval BOOLEAN DEFAULT FALSE
);

-- Workflow states table
CREATE TABLE workflow_states (
    workflow_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    current_stage workflow_stage NOT NULL,
    stage_status stage_status DEFAULT 'in_progress',
    input_data JSONB,
    stage_outputs JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Approval requests table
CREATE TABLE approval_requests (
    approval_request_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    workflow_id UUID NOT NULL REFERENCES workflow_states(workflow_id) ON DELETE CASCADE,
    findings JSONB NOT NULL,
    reviewer_id UUID REFERENCES users(user_id) ON DELETE SET NULL,
    status approval_status DEFAULT 'pending',
    decision_timestamp TIMESTAMP,
    modifications JSONB,
    rejection_reason TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Access grants table
CREATE TABLE access_grants (
    grant_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    patient_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    grantee_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    granted_role user_role NOT NULL CHECK (granted_role IN ('caregiver', 'doctor')),
    granted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    revoked_at TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    CONSTRAINT different_users CHECK (patient_id != grantee_id)
);

-- Audit logs table
CREATE TABLE audit_logs (
    log_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(user_id) ON DELETE SET NULL,
    action VARCHAR(100) NOT NULL,
    resource_type VARCHAR(100) NOT NULL,
    resource_id UUID,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ip_address INET,
    details JSONB
);

-- Create indexes for better query performance
CREATE INDEX idx_medical_reports_user_id ON medical_reports(user_id);
CREATE INDEX idx_medical_reports_report_date ON medical_reports(report_date);
CREATE INDEX idx_health_parameters_user_id ON health_parameters(user_id);
CREATE INDEX idx_health_parameters_parameter_name ON health_parameters(parameter_name);
CREATE INDEX idx_health_parameters_timestamp ON health_parameters(timestamp);
CREATE INDEX idx_normalized_parameters_user_id ON normalized_parameters(user_id);
CREATE INDEX idx_normalized_parameters_canonical_name ON normalized_parameters(canonical_name);
CREATE INDEX idx_normalization_audit_logs_parameter_id ON normalization_audit_logs(parameter_id);
CREATE INDEX idx_trends_user_id ON trends(user_id);
CREATE INDEX idx_trends_parameter_name ON trends(parameter_name);
CREATE INDEX idx_risk_flags_user_id ON risk_flags(user_id);
CREATE INDEX idx_workflow_states_user_id ON workflow_states(user_id);
CREATE INDEX idx_approval_requests_workflow_id ON approval_requests(workflow_id);
CREATE INDEX idx_access_grants_patient_id ON access_grants(patient_id);
CREATE INDEX idx_access_grants_grantee_id ON access_grants(grantee_id);
CREATE INDEX idx_audit_logs_user_id ON audit_logs(user_id);
CREATE INDEX idx_audit_logs_timestamp ON audit_logs(timestamp);

-- Create function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create triggers for updated_at
CREATE TRIGGER update_users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_workflow_states_updated_at
    BEFORE UPDATE ON workflow_states
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Grant permissions (adjust as needed)
-- GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO medical_health_app;
-- GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO medical_health_app;
