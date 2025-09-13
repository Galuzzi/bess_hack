#!/usr/bin/env python3
"""
BESS Data Ingestion Script for TimescaleDB
Handles CSV files with misaligned timestamps and bulk inserts data efficiently.
Fixed for psycopg3 compatibility.
"""

import sys
import logging
import psycopg
from pydantic import BaseModel, Field
from pathlib import Path
from typing import List, Tuple, Optional
import pandas as pd
import argparse

# Configure logging
logging.basicConfig(
    level=logging.WARN,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bess_ingestion.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class DatabaseConfig(BaseModel):
    """Database configuration for TimescaleDB connection"""
    host: str = Field(default="ro9on8kgxj.iw7envwgqa.tsdb.cloud.timescale.com")
    port: int = Field(default=39117)
    database: str = Field(default="tsdb")
    username: str = Field(default="tsdbadmin")
    password: str = Field(default="cy63ab0r15mjn1j7")
    
    def get_connection_string(self) -> str:
        return f"postgresql://{self.username}:{self.password}@{self.host}:{self.port}/{self.database}?sslmode=require"
    


class BESSSystem(BaseModel):
    """BESS System configuration"""
    system_id: int
    system_name: str
    data_folder: Path
    location: Optional[str] = None
    capacity_kwh: Optional[float] = None

class BESSDataIngester:
    """Main class for ingesting BESS CSV data into TimescaleDB"""
    
    def __init__(self, db_config: DatabaseConfig):
        self.db_config = db_config
        self.connection = None
        
        # Create base metric mapping
        base_mapping = {
            # BMS metrics
            'bms1_soc': ('soc', 'BMS'),
            'bms1_soh': ('soh', 'BMS'), 
            'bms1_v': ('total_voltage', 'BMS'),
            'bms1_c': ('total_current', 'BMS'),
            'bms1_cell_ave_v': ('cell_avg_voltage', 'BMS'),
            'bms1_cell_ave_t': ('cell_avg_temp', 'BMS'),
            'bms1_cell_max_v': ('cell_max_voltage', 'BMS'),
            'bms1_cell_min_v': ('cell_min_voltage', 'BMS'),
            'bms1_cell_max_t': ('cell_max_temperature', 'BMS'),
            'bms1_cell_min_t': ('cell_min_temperature', 'BMS'),
            'bms1_cell_v_diff': ('cell_voltage_diff', 'BMS'),
            'bms1_cell_t_diff': ('cell_temp_diff', 'BMS'),
            
            # PCS metrics  
            'pcs1_ap': ('apparent_power', 'PCS'),
            'pcs1_dcc': ('dc_current', 'PCS'),
            'pcs1_dcv': ('dc_voltage', 'PCS'),
            'pcs1_ia': ('ac_current_a', 'PCS'),
            'pcs1_ib': ('ac_current_b', 'PCS'),
            'pcs1_ic': ('ac_current_c', 'PCS'),
            'pcs1_uab': ('ac_voltage_ab', 'PCS'),
            'pcs1_ubc': ('ac_voltage_bc', 'PCS'),
            'pcs1_uca': ('ac_voltage_ca', 'PCS'),
            'pcs1_t_env': ('temp_env', 'PCS'),
            'pcs1_t_a': ('temp_ambient', 'PCS'),
            'pcs1_t_igbt': ('temp_igbt', 'PCS'),
            
            # Auxiliary metrics
            'ac1_outside_t': ('outside_temp', 'AUX'),
            'ac1_outwater_t': ('outwater_temp', 'AUX'),
            'ac1_rtnwater_pre': ('return_water_pressure', 'AUX'),
            'ac1_rtnwater_t': ('return_water_temp', 'AUX'),
            'ac1_outwater_pre': ('outwater_pressure', 'AUX'),
            'aux_m_i': ('motor_current', 'AUX'),
            'aux_m_com_ae': ('common_airflow_energy', 'AUX'),
            'aux_m_neg_ae': ('exhaust_fan_energy', 'AUX'),
            'aux_m_pf': ('motor_power_factor', 'AUX'),
            'aux_m_ap': ('air_pressure', 'AUX'),
            'aux_m_pos_ae': ('supply_fan_energy', 'AUX'),
            
            # Environmental metrics
            'dh1_humi': ('humidity', 'ENV'),
            'dh1_temp': ('temperature', 'ENV'),
        }
        
        # Add per-pack cell voltages and temperatures
        cell_mapping = {}
        
        # Generate cell voltage mappings for 5 packs, 52 cells each
        for pack in range(1, 6):  # packs 1-5
            for cell in range(1, 53):  # cells 1-52
                # Cell voltages
                voltage_key = f'bms1_p{pack}_v{cell}'
                voltage_metric = f'pack{pack}_cell{cell}_voltage'
                cell_mapping[voltage_key] = (voltage_metric, 'BMS')
                
                # Cell temperatures
                temp_key = f'bms1_p{pack}_t{cell}'
                temp_metric = f'pack{pack}_cell{cell}_temp'
                cell_mapping[temp_key] = (temp_metric, 'BMS')

        sensor_mapping = {}

        # Generate mappings for 5 alarms/sensors
        for i in range(1, 6):
            keys = {
                f'fa{i}_errcode': f'fire_alarm{i}_error_code',
                f'fa{i}_level': f'fire_alarm{i}_level',
                f'fa{i}_t1': f'fire_alarm{i}_temperature1',
                f'fa{i}_t2': f'fire_alarm{i}_temperature2',
                f'fa{i}_smokeflag': f'fire_alarm{i}_smoke_flag',
                f'fa{i}_co': f'co_sensor{i}_level',
                f'fa{i}_voc': f'voc_sensor{i}_level' # volatile organic compounds
            }

            # Add all keys to the mapping
            for key, metric in keys.items():
                sensor_mapping[key] = (metric, 'SAFETY')
        
        # Combine base mapping with cell mapping
        self.metric_mapping = {**base_mapping, **cell_mapping, **sensor_mapping}

    def connect(self) -> bool:
        """Establish connection to TimescaleDB"""
        try:
            self.connection = psycopg.connect(
                host=self.db_config.host,
                port=self.db_config.port,
                dbname=self.db_config.database,
                user=self.db_config.username,
                password=self.db_config.password,
                autocommit=False
            )
            logger.info(f"Connected to TimescaleDB at {self.db_config.host}:{self.db_config.port}")
            return True
        except psycopg.Error as e:
            logger.error(f"Failed to connect to database: {e}")
            return False

    def disconnect(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()
            logger.info("Database connection closed")

    def setup_database(self):
        """Create tables if they don't exist"""
        setup_queries = [
            # Create systems table
            """
            CREATE TABLE IF NOT EXISTS bess_systems (
                system_id SERIAL PRIMARY KEY,
                system_name VARCHAR(50) UNIQUE NOT NULL,
                location VARCHAR(100),
                installation_date DATE,
                capacity_kwh DECIMAL(10,2),
                created_at TIMESTAMPTZ DEFAULT NOW()
            );
            """,
            
            # Create main metrics table
            """
            CREATE TABLE IF NOT EXISTS bess_metrics (
                time TIMESTAMPTZ NOT NULL,
                system_id INTEGER NOT NULL REFERENCES bess_systems(system_id),
                metric_name VARCHAR(50) NOT NULL,
                value DOUBLE PRECISION,
                unit VARCHAR(20),
                subsystem VARCHAR(20) NOT NULL,
                CONSTRAINT bess_metrics_pkey PRIMARY KEY (time, system_id, metric_name)
            );
            """,
            
            # Create hypertable if not exists
            """
            SELECT create_hypertable('bess_metrics', 'time', 
                chunk_time_interval => INTERVAL '1 day',
                if_not_exists => TRUE
            );
            """,
            
            # Create indexes
            """
            CREATE INDEX IF NOT EXISTS idx_bess_metrics_system_metric 
            ON bess_metrics (system_id, metric_name, time DESC);
            """,
            
            """
            CREATE INDEX IF NOT EXISTS idx_bess_metrics_subsystem 
            ON bess_metrics (subsystem, time DESC);
            """
        ]
        
        try:
            with self.connection.cursor() as cursor:
                for query in setup_queries:
                    cursor.execute(query)
            self.connection.commit()
            logger.info("Database schema setup completed")
        except psycopg.Error as e:
            logger.error(f"Failed to setup database schema: {e}")
            self.connection.rollback()
            raise

    def register_system(self, system: BESSSystem) -> bool:
        """Register a BESS system in the database"""
        insert_query = """
        INSERT INTO bess_systems (system_name, location, capacity_kwh)
        VALUES (%s, %s, %s)
        ON CONFLICT (system_name) DO NOTHING;
        """
        
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(insert_query, (
                    system.system_name, 
                    system.location, 
                    system.capacity_kwh
                ))
            self.connection.commit()
            logger.info(f"System {system.system_name} registered")
            return True
        except psycopg.Error as e:
            logger.error(f"Failed to register system {system.system_name}: {e}")
            self.connection.rollback()
            return False

    def get_system_id(self, system_name: str) -> Optional[int]:
        """Get system_id for a given system name"""
        query = "SELECT system_id FROM bess_systems WHERE system_name = %s;"
        
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(query, (system_name,))
                result = cursor.fetchone()
                return result[0] if result else None
        except psycopg.Error as e:
            logger.error(f"Failed to get system_id for {system_name}: {e}")
            return None

    def parse_csv_file(self, file_path: Path, system_id: int, metric_name: str, subsystem: str) -> List[Tuple]:
        """Parse CSV file and return list of tuples for bulk insert"""
        data_rows = []
        
        try:
            # Try pandas first for better handling of various CSV formats
            df = pd.read_csv(file_path)
            
            # Ensure we have the expected columns
            if len(df.columns) != 2:
                logger.warning(f"Unexpected number of columns in {file_path}: {len(df.columns)}")
                return []
            
            timestamp_col, value_col = df.columns

            # Drop rows with any nulls
            df = df.dropna(subset=[timestamp_col, value_col])

            if df.empty:
                logger.info(f"No valid data in {file_path}")
                return []

            # Convert timestamp and value
            df[timestamp_col] = pd.to_datetime(df[timestamp_col], errors='coerce')
            df[value_col] = pd.to_numeric(df[value_col], errors='coerce')

            # Drop rows that could not be converted
            df = df.dropna(subset=[timestamp_col, value_col])
            
            # Set timestamp as index for resampling
            df.set_index(timestamp_col, inplace=True)
            
            # Resample to 5-minute intervals (taking mean of values)
            df_resampled = df.resample('5min').mean().dropna()

            # Build list of tuples
            unit = self.get_metric_unit(metric_name)
            data_rows = [
                (timestamp, system_id, metric_name, value, unit, subsystem)
                for timestamp, value in df_resampled[value_col].items()
            ]

            logger.info(f"Parsed and resampled {len(data_rows)} rows from {file_path}")
            return data_rows
            
        except Exception as e:
            logger.error(f"Failed to parse {file_path}: {e}")
            return []

    def get_metric_unit(self, metric_name: str) -> str:
        """Get appropriate unit for metric"""
        unit_mapping = {
            'soc': '%', 'soh': '%',
            'total_voltage': 'V', 'dc_voltage': 'V', 'cell_avg_voltage': 'V',
            'cell_max_voltage': 'V', 'cell_min_voltage': 'V',
            'ac_voltage_ab': 'V', 'ac_voltage_bc': 'V', 'ac_voltage_ca': 'V',
            'total_current': 'A', 'dc_current': 'A',
            'ac_current_a': 'A', 'ac_current_b': 'A', 'ac_current_c': 'A',
            'apparent_power': 'kVA', 'aux_apparent_power': 'kVA',
            'temp_env': '°C', 'temp_ambient': '°C', 'temp_igbt': '°C',
            'cell_avg_temp': '°C', 'cell_temp_diff': '°C',
            'outside_temp': '°C', 'outwater_temp': '°C', 'temperature': '°C',
            'return_water_pressure': 'bar',
            'humidity': '%',
            'aux_power_factor': 'PF',
        }
        
        # Handle per-pack cell voltages and temperatures dynamically
        if 'cell' in metric_name and 'voltage' in metric_name:
            return 'V'
        if 'cell' in metric_name and 'temp' in metric_name:
            return '°C'
        if metric_name.startswith('pack') and 'voltage' in metric_name:
            return 'V'
        if metric_name.startswith('pack') and 'temp' in metric_name:
            return '°C'
        if metric_name.startswith('fire_alarm') and 'temperature' in metric_name:
            return '°C'
        if metric_name.startswith('voc_sensor'):
            return 'ppm'
        if metric_name.startswith('co_sensor'):        
            return 'ppm'
        
        return unit_mapping.get(metric_name, '')

    def bulk_insert_metrics(self, data_rows: List[Tuple]) -> bool:
        """Bulk insert metrics data using executemany for performance in psycopg3"""
        if not data_rows:
            logger.warning("No data to insert")
            return True
            
        insert_query = """
        INSERT INTO bess_metrics (time, system_id, metric_name, value, unit, subsystem)
        VALUES (%s, %s, %s, %s, %s, %s)
        ON CONFLICT (time, system_id, metric_name) DO UPDATE SET
            value = EXCLUDED.value,
            unit = EXCLUDED.unit,
            subsystem = EXCLUDED.subsystem;
        """
        
        try:
            with self.connection.cursor() as cursor:
                # Use executemany for bulk insert in psycopg3
                cursor.executemany(insert_query, data_rows)
            self.connection.commit()
            logger.info(f"Bulk inserted {len(data_rows)} metric records")
            return True
            
        except psycopg.Error as e:
            logger.error(f"Failed to bulk insert metrics: {e}")
            self.connection.rollback()
            return False

    def bulk_insert_metrics_copy(self, data_rows: List[Tuple]) -> bool:
        """Alternative bulk insert using COPY for even better performance"""
        if not data_rows:
            logger.warning("No data to insert")
            return True
            
        try:
            with self.connection.cursor() as cursor:
                # Create a temporary table for the data
                cursor.execute("""
                    CREATE TEMP TABLE temp_bess_metrics (
                        time TIMESTAMPTZ,
                        system_id INTEGER,
                        metric_name VARCHAR(50),
                        value DOUBLE PRECISION,
                        unit VARCHAR(20),
                        subsystem VARCHAR(20)
                    ) ON COMMIT DROP;
                """)
                
                # Use COPY to insert data into temp table
                with cursor.copy("COPY temp_bess_metrics FROM STDIN") as copy:
                    for row in data_rows:
                        # Format the row for COPY
                        formatted_row = f"{row[0]}\t{row[1]}\t{row[2]}\t{row[3]}\t{row[4] or ''}\t{row[5]}\n"
                        copy.write(formatted_row)
                
                # Insert from temp table to main table with conflict resolution
                cursor.execute("""
                    INSERT INTO bess_metrics (time, system_id, metric_name, value, unit, subsystem)
                    SELECT time, system_id, metric_name, value, unit, subsystem
                    FROM temp_bess_metrics
                    ON CONFLICT (time, system_id, metric_name) DO UPDATE SET
                        value = EXCLUDED.value,
                        unit = EXCLUDED.unit,
                        subsystem = EXCLUDED.subsystem;
                """)
                
            self.connection.commit()
            logger.info(f"Bulk inserted {len(data_rows)} metric records using COPY")
            return True
            
        except psycopg.Error as e:
            logger.error(f"Failed to bulk insert metrics using COPY: {e}")
            self.connection.rollback()
            return False

    def process_csv_files(self, system: BESSSystem, use_copy: bool = False) -> bool:
        """Process all CSV files for a given BESS system"""
        system_id = self.get_system_id(system.system_name)
        if not system_id:
            logger.error(f"System {system.system_name} not found in database")
            return False
            
        csv_files = list(system.data_folder.glob("*.csv"))
        if not csv_files:
            logger.warning(f"No CSV files found in {system.data_folder}")
            return False
            
        logger.info(f"Processing {len(csv_files)} CSV files for system {system.system_name}")
        
        total_rows = 0
        processed_files = 0
        
        for csv_file in csv_files:
            # Extract metric name from filename
            file_stem = csv_file.stem.lower()
            
            # Find matching metric mapping
            metric_info = None
            for prefix, info in self.metric_mapping.items():
                if file_stem.startswith(prefix):
                    metric_info = info
                    break
                    
            if not metric_info:
                logger.warning(f"Unknown metric file: {csv_file.name}")
                continue
                
            metric_name, subsystem = metric_info
            logger.info(f"Processing {csv_file.name} -> {metric_name} ({subsystem})")
            
            # Parse and insert data
            data_rows = self.parse_csv_file(csv_file, system_id, metric_name, subsystem)
            if data_rows:
                # Choose insertion method based on use_copy flag
                insert_method = self.bulk_insert_metrics_copy if use_copy else self.bulk_insert_metrics
                
                if insert_method(data_rows):
                    total_rows += len(data_rows)
                    processed_files += 1
                else:
                    logger.error(f"Failed to insert data from {csv_file.name}")
            else:
                logger.warning(f"No valid data found in {csv_file.name}")
                
        logger.info(f"Completed processing {processed_files} files, inserted {total_rows} total rows for system {system.system_name}")
        return processed_files > 0

def main():
    parser = argparse.ArgumentParser(description='Ingest BESS CSV data into TimescaleDB')
    parser.add_argument('--host', default='ro9on8kgxj.iw7envwgqa.tsdb.cloud.timescale.com', help='Database host')
    parser.add_argument('--port', type=int, default=39117, help='Database port')
    parser.add_argument('--database', default='tsdb', help='Database name')
    parser.add_argument('--username', default='tsdbadmin', help='Database username')
    parser.add_argument('--password', default='cy63ab0r15mjn1j7', help='Database password')
    parser.add_argument('--data-dir', required=True, help='Root directory containing BESS system folders')
    parser.add_argument('--setup-db', action='store_true', help='Setup database schema')
    parser.add_argument('--use-copy', action='store_true', help='Use COPY method for faster bulk inserts')
    
    args = parser.parse_args()
    
    # Database configuration
    db_config = DatabaseConfig(
        host=args.host,
        port=args.port,
        database=args.database,
        username=args.username,
        password=args.password
    )
    
    # Initialize ingester
    ingester = BESSDataIngester(db_config)
    
    try:
        # Connect to database
        if not ingester.connect():
            sys.exit(1)
            
        # Setup database schema if requested
        if args.setup_db:
            logger.info("Setting up database schema...")
            ingester.setup_database()
            
        # Define BESS systems (modify as needed)
        data_root = Path(args.data_dir)
        systems = [
            BESSSystem(
                system_id=1, 
                system_name="BESS-001", 
                data_folder=data_root / "ZHPESS232A230002", 
                location="Site A", 
                capacity_kwh=482.0
            ),
            # BESSSystem(
            #     system_id=2, 
            #     system_name="BESS-002", 
            #     data_folder=data_root / "ZHPESS232A230003", 
            #     location="Site B", 
            #     capacity_kwh=482.0
            # ),
            # BESSSystem(
            #     system_id=3, 
            #     system_name="BESS-003", 
            #     data_folder=data_root / "ZHPESS232A230007", 
            #     location="Site C", 
            #     capacity_kwh=482.0
            # ),
        ]
        
        # Process each system
        for system in systems:
            if not system.data_folder.exists():
                logger.warning(f"System folder not found: {system.data_folder}")
                continue
                
            logger.info(f"Processing system: {system.system_name}")
            
            # Register system
            ingester.register_system(system)
            
            # Process CSV files
            ingester.process_csv_files(system, use_copy=args.use_copy)
            
        logger.info("Data ingestion completed successfully")
        
    except Exception as e:
        logger.error(f"Data ingestion failed: {e}")
        sys.exit(1)
        
    finally:
        ingester.disconnect()

if __name__ == "__main__":
    main()