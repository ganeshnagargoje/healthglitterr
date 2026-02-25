"""
Lab Data Normalizer

Core normalization logic for lab parameters including:
- Parameter name standardization
- Unit conversion
- Reference range alignment
"""

from typing import Tuple, Optional, List, Dict, Any
import uuid


class LabDataNormalizer:
    """Core normalization logic for lab parameters"""
    
    def __init__(self, db_connection):
        """
        Initialize normalizer with database connection
        
        Args:
            db_connection: DatabaseConnection instance
        """
        self.db = db_connection
        self.operations_log: List[Dict[str, Any]] = []
    
    def normalize_parameter_name(self, original_name: str, parameter_id: str) -> Tuple[Optional[str], float]:
        """
        Map parameter name to canonical form using parameter_name_mappings table
        
        Args:
            original_name: Original parameter name from lab report
            parameter_id: UUID of the health parameter
        
        Returns:
            Tuple of (canonical_name, confidence_score)
            Returns (None, 0.0) if no mapping found
        """
        try:
            # Query parameter_name_mappings table
            self.db.cursor.execute("""
                SELECT canonical_name, confidence_score
                FROM parameter_name_mappings
                WHERE LOWER(variant_name) = LOWER(%s)
                ORDER BY confidence_score DESC
                LIMIT 1
            """, (original_name,))
            
            result = self.db.cursor.fetchone()
            
            if result:
                canonical_name = result['canonical_name']
                confidence = float(result['confidence_score'])
                
                # Log successful operation
                self._log_operation(
                    parameter_id=parameter_id,
                    operation='name_mapping',
                    status='success',
                    original_name=original_name,
                    canonical_name=canonical_name
                )
                
                return canonical_name, confidence
            else:
                # No mapping found - flag for review
                self._log_operation(
                    parameter_id=parameter_id,
                    operation='name_mapping',
                    status='flagged',
                    original_name=original_name,
                    failure_reason=f"No canonical mapping found for '{original_name}'"
                )
                return None, 0.0
                
        except Exception as e:
            self._log_operation(
                parameter_id=parameter_id,
                operation='name_mapping',
                status='failed',
                original_name=original_name,
                failure_reason=str(e)
            )
            return None, 0.0
    
    def convert_unit(
        self, 
        value: float, 
        original_unit: Optional[str], 
        canonical_name: str,
        parameter_id: str
    ) -> Tuple[Optional[float], Optional[str], Optional[float], float]:
        """
        Convert value to standard unit using unit_conversion_rules table
        
        Args:
            value: Original measured value
            original_unit: Original unit from lab report
            canonical_name: Canonical parameter name
            parameter_id: UUID of the health parameter
        
        Returns:
            Tuple of (normalized_value, standard_unit, conversion_factor, confidence)
            Returns (None, None, None, 0.0) if conversion fails
        """
        if not original_unit:
            # No unit provided - use value as-is but flag
            self._log_operation(
                parameter_id=parameter_id,
                operation='unit_conversion',
                status='flagged',
                original_value=value,
                original_unit=None,
                failure_reason="No unit provided in source data"
            )
            return value, None, None, 0.5
        
        try:
            # Query unit_conversion_rules table
            self.db.cursor.execute("""
                SELECT target_unit, conversion_factor, confidence_score
                FROM unit_conversion_rules
                WHERE canonical_parameter_name = %s
                  AND LOWER(source_unit) = LOWER(%s)
                LIMIT 1
            """, (canonical_name, original_unit))
            
            result = self.db.cursor.fetchone()
            
            if result:
                target_unit = result['target_unit']
                conversion_factor = float(result['conversion_factor'])
                confidence = float(result['confidence_score'])
                normalized_value = value * conversion_factor
                
                # Log successful operation
                self._log_operation(
                    parameter_id=parameter_id,
                    operation='unit_conversion',
                    status='success',
                    original_value=value,
                    original_unit=original_unit,
                    normalized_value=normalized_value,
                    standard_unit=target_unit,
                    conversion_factor=conversion_factor
                )
                
                return normalized_value, target_unit, conversion_factor, confidence
            else:
                # Check if original unit IS the standard unit
                self.db.cursor.execute("""
                    SELECT target_unit
                    FROM unit_conversion_rules
                    WHERE canonical_parameter_name = %s
                    LIMIT 1
                """, (canonical_name,))
                
                standard_result = self.db.cursor.fetchone()
                
                if standard_result and standard_result['target_unit'].lower() == original_unit.lower():
                    # Already in standard unit
                    self._log_operation(
                        parameter_id=parameter_id,
                        operation='unit_conversion',
                        status='success',
                        original_value=value,
                        original_unit=original_unit,
                        normalized_value=value,
                        standard_unit=original_unit,
                        conversion_factor=1.0
                    )
                    return value, original_unit, 1.0, 1.0
                else:
                    # No conversion rule found
                    self._log_operation(
                        parameter_id=parameter_id,
                        operation='unit_conversion',
                        status='flagged',
                        original_value=value,
                        original_unit=original_unit,
                        failure_reason=f"No conversion rule for '{original_unit}' to standard unit"
                    )
                    return None, None, None, 0.0
                    
        except Exception as e:
            self._log_operation(
                parameter_id=parameter_id,
                operation='unit_conversion',
                status='failed',
                original_value=value,
                original_unit=original_unit,
                failure_reason=str(e)
            )
            return None, None, None, 0.0
    
    def align_reference_range(
        self,
        canonical_name: str,
        standard_unit: str,
        parameter_id: str
    ) -> Tuple[Optional[float], Optional[float], float]:
        """
        Get standard reference range for parameter using standard_reference_ranges table
        
        Args:
            canonical_name: Canonical parameter name
            standard_unit: Standard unit for the parameter
            parameter_id: UUID of the health parameter
        
        Returns:
            Tuple of (range_min, range_max, confidence)
            Returns (None, None, 0.5) if no range found
        """
        try:
            # Query standard_reference_ranges table
            self.db.cursor.execute("""
                SELECT range_min, range_max, confidence_score
                FROM standard_reference_ranges
                WHERE canonical_parameter_name = %s
                  AND standard_unit = %s
                LIMIT 1
            """, (canonical_name, standard_unit))
            
            result = self.db.cursor.fetchone()
            
            if result:
                range_min = float(result['range_min']) if result['range_min'] else None
                range_max = float(result['range_max']) if result['range_max'] else None
                confidence = float(result['confidence_score'])
                
                # Log successful operation
                self._log_operation(
                    parameter_id=parameter_id,
                    operation='range_alignment',
                    status='success',
                    canonical_name=canonical_name,
                    standard_unit=standard_unit
                )
                
                return range_min, range_max, confidence
            else:
                # No reference range found
                self._log_operation(
                    parameter_id=parameter_id,
                    operation='range_alignment',
                    status='flagged',
                    canonical_name=canonical_name,
                    failure_reason=f"No reference range found for '{canonical_name}' in unit '{standard_unit}'"
                )
                return None, None, 0.5
                
        except Exception as e:
            self._log_operation(
                parameter_id=parameter_id,
                operation='range_alignment',
                status='failed',
                canonical_name=canonical_name,
                failure_reason=str(e)
            )
            return None, None, 0.0
    
    def _log_operation(
        self,
        parameter_id: str,
        operation: str,
        status: str,
        original_value: Optional[float] = None,
        original_unit: Optional[str] = None,
        original_name: Optional[str] = None,
        normalized_value: Optional[float] = None,
        standard_unit: Optional[str] = None,
        canonical_name: Optional[str] = None,
        conversion_factor: Optional[float] = None,
        failure_reason: Optional[str] = None
    ):
        """
        Log normalization operation to in-memory buffer
        
        Args:
            parameter_id: UUID of the health parameter
            operation: Type of operation (name_mapping, unit_conversion, range_alignment)
            status: Operation status (success, failed, flagged)
            original_value: Original measured value
            original_unit: Original unit
            original_name: Original parameter name
            normalized_value: Normalized value
            standard_unit: Standard unit
            canonical_name: Canonical parameter name
            conversion_factor: Unit conversion factor
            failure_reason: Reason for failure if status is failed or flagged
        """
        self.operations_log.append({
            'parameter_id': parameter_id,
            'operation': operation,
            'status': status,
            'original_value': original_value,
            'original_unit': original_unit,
            'original_name': original_name,
            'normalized_value': normalized_value,
            'standard_unit': standard_unit,
            'canonical_name': canonical_name,
            'conversion_factor': conversion_factor,
            'failure_reason': failure_reason
        })
    
    def save_audit_logs(self):
        """
        Persist all operation logs to normalization_audit_logs table
        
        This should be called after all normalization operations are complete
        to ensure audit trail is saved to database
        """
        for log in self.operations_log:
            try:
                self.db.cursor.execute("""
                    INSERT INTO normalization_audit_logs (
                        parameter_id, operation, status,
                        original_value, original_unit, original_name,
                        normalized_value, standard_unit, canonical_name,
                        conversion_factor, failure_reason
                    ) VALUES (
                        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                    )
                """, (
                    log['parameter_id'],
                    log['operation'],
                    log['status'],
                    log['original_value'],
                    log['original_unit'],
                    log['original_name'],
                    log['normalized_value'],
                    log['standard_unit'],
                    log['canonical_name'],
                    log['conversion_factor'],
                    log['failure_reason']
                ))
            except Exception as e:
                print(f"Error saving audit log: {e}")
