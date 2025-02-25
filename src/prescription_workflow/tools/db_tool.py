from typing import Dict, Optional
from datetime import datetime
# from mysql.connector import Error
# import mysql.connector
import logging
from dotenv import load_dotenv
import os

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

class DatabaseTools:
    # def __init__(self):
    #     self.config = {
    #         'host': os.getenv('MYSQL_HOST', 'localhost'),
    #         'user': os.getenv('MYSQL_USER'),
    #         'password': os.getenv('MYSQL_PASSWORD'),
    #         'database': os.getenv('MYSQL_DATABASE')
    #     }
    #     self.initialize_database()

    # def get_connection(self):
    #     """Create and return a database connection."""
    #     try:
    #         connection = mysql.connector.connect(**self.config)
    #         return connection
    #     except Error as e:
    #         logger.error(f"Error connecting to MySQL: {e}")
    #         return None

    # def initialize_database(self):
    #     """Create necessary tables if they don't exist."""
    #     connection = self.get_connection()
    #     if not connection:
    #         return

    #     try:
    #         cursor = connection.cursor()
            
    #         # Create prescriptions table
    #         cursor.execute("""
    #             CREATE TABLE IF NOT EXISTS prescriptions (
    #                 id INT AUTO_INCREMENT PRIMARY KEY,
    #                 message_id VARCHAR(255) UNIQUE,
    #                 patient_name VARCHAR(255),
    #                 dob DATE,
    #                 address TEXT,
    #                 email VARCHAR(255),
    #                 pharmacy_name VARCHAR(255),
    #                 pharmacy_address TEXT,
    #                 blood_pressure VARCHAR(20),
    #                 heart_rate INT,
    #                 medication_name VARCHAR(255),
    #                 strength VARCHAR(50),
    #                 repeats INT,
    #                 status ENUM('pending', 'completed', 'awaiting_response', 'escalated'),
    #                 created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    #                 updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
    #             )
    #         """)
            
    #         # Create follow_ups table
    #         cursor.execute("""
    #             CREATE TABLE IF NOT EXISTS follow_ups (
    #                 id INT AUTO_INCREMENT PRIMARY KEY,
    #                 prescription_id INT,
    #                 reminder_sent_at TIMESTAMP,
    #                 reminder_type ENUM('48_hour', '96_hour'),
    #                 status ENUM('sent', 'responded'),
    #                 FOREIGN KEY (prescription_id) REFERENCES prescriptions(id)
    #             )
    #         """)
            
    #         connection.commit()
    #         logger.info("Database tables initialized successfully")
            
    #     except Error as e:
    #         logger.error(f"Error initializing database: {e}")
    #     finally:
    #         if connection.is_connected():
    #             cursor.close()
    #             connection.close()

    # def save_prescription(self, prescription_data: Dict, message_id: str) -> bool:
    #     """Save prescription data to database."""
    #     connection = self.get_connection()
    #     if not connection:
    #         return False

    #     try:
    #         cursor = connection.cursor()
            
    #         # Convert date string to MySQL date format
    #         dob = datetime.strptime(prescription_data['dob'], '%Y-%m-%d').date()
            
    #         query = """
    #             INSERT INTO prescriptions (
    #                 message_id, patient_name, dob, address, email,
    #                 pharmacy_name, pharmacy_address, blood_pressure,
    #                 heart_rate, medication_name, strength, repeats,
    #                 status
    #             ) VALUES (
    #                 %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
    #             )
    #         """
            
    #         values = (
    #             message_id,
    #             prescription_data['patient_name'],
    #             dob,
    #             prescription_data['address'],
    #             prescription_data['email'],
    #             prescription_data['pharmacy_name'],
    #             prescription_data['pharmacy_address'],
    #             prescription_data['blood_pressure'],
    #             prescription_data['heart_rate'],
    #             prescription_data['medication_name'],
    #             prescription_data['strength'],
    #             prescription_data['repeats'],
    #             'pending'
    #         )
            
    #         cursor.execute(query, values)
    #         connection.commit()
    #         logger.info(f"Prescription saved successfully for patient: {prescription_data['patient_name']}")
    #         return True
            
    #     except Error as e:
    #         logger.error(f"Error saving prescription: {e}")
    #         return False
    #     finally:
    #         if connection.is_connected():
    #             cursor.close()
    #             connection.close()

    # def update_prescription_status(self, message_id: str, status: str) -> bool:
    #     """Update prescription status."""
    #     connection = self.get_connection()
    #     if not connection:
    #         return False

    #     try:
    #         cursor = connection.cursor()
    #         query = "UPDATE prescriptions SET status = %s WHERE message_id = %s"
    #         cursor.execute(query, (status, message_id))
    #         connection.commit()
    #         return True
    #     except Error as e:
    #         logger.error(f"Error updating prescription status: {e}")
    #         return False
    #     finally:
    #         if connection.is_connected():
    #             cursor.close()
    #             connection.close()

    # def save_follow_up(self, prescription_id: int, reminder_type: str) -> bool:
    #     """Save follow-up reminder details."""
    #     connection = self.get_connection()
    #     if not connection:
    #         return False

    #     try:
    #         cursor = connection.cursor()
    #         query = """
    #             INSERT INTO follow_ups (prescription_id, reminder_type, status)
    #             VALUES (%s, %s, 'sent')
    #         """
    #         cursor.execute(query, (prescription_id, reminder_type))
    #         connection.commit()
    #         return True
    #     except Error as e:
    #         logger.error(f"Error saving follow-up: {e}")
    #         return False
    #     finally:
    #         if connection.is_connected():
    #             cursor.close()
    #             connection.close()

    # def get_pending_prescriptions(self) -> list:
    #     """Get all pending prescriptions that need follow-up."""
    #     connection = self.get_connection()
    #     if not connection:
    #         return []

    #     try:
    #         cursor = connection.cursor(dictionary=True)
    #         query = """
    #             SELECT * FROM prescriptions 
    #             WHERE status = 'awaiting_response'
    #             AND updated_at < NOW() - INTERVAL 48 HOUR
    #         """
    #         cursor.execute(query)
    #         return cursor.fetchall()
    #     except Error as e:
    #         logger.error(f"Error fetching pending prescriptions: {e}")
    #         return []
    #     finally:
    #         if connection.is_connected():
    #             cursor.close()
    #             connection.close()
    pass