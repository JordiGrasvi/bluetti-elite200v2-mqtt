"""
Tests per a les eines d'ajuda del projecte
"""

import pytest
import json
import tempfile
import os
from pathlib import Path
import sys

# Afegeix el directori arrel al path
sys.path.insert(0, str(Path(__file__).parent.parent))

from tools.convert_license import convert_license_to_json, validate_mac_address


class TestConvertLicense:
    """Tests per a l'eina de conversió de llicències"""
    
    def test_validate_mac_address_valid(self):
        """Test validació d'adreces MAC vàlides"""
        valid_macs = [
            "E4:B3:23:5B:F5:76",
            "00:11:22:33:44:55",
            "FF:FF:FF:FF:FF:FF",
            "aa:bb:cc:dd:ee:ff",
        ]
        
        for mac in valid_macs:
            assert validate_mac_address(mac), f"MAC {mac} hauria de ser vàlida"
    
    def test_validate_mac_address_invalid(self):
        """Test validació d'adreces MAC invàlides"""
        invalid_macs = [
            "E4:B3:23:5B:F5",  # Massa curta
            "E4:B3:23:5B:F5:76:77",  # Massa llarga
            "G4:B3:23:5B:F5:76",  # Caràcter invàlid
            "E4-B3-23-5B-F5-76",  # Separador incorrecte
            "",  # Buida
            None,  # None
        ]
        
        for mac in invalid_macs:
            assert not validate_mac_address(mac), f"MAC {mac} hauria de ser invàlida"
    
    def test_convert_license_to_json_success(self):
        """Test conversió exitosa de llicència a JSON"""
        # Crea un fitxer de llicència temporal
        license_content = """
bluetti
1745826744092
4a942a522abf710b3c8e61973e3aa17a
45b31b6c213dfcc16059010bb107746aa4dbb51589e9192e1b37dd0422e7e30d0cc071dcdbd3fd720928d65ee0ef8e1a"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write(license_content)
            license_file = f.name
        
        try:
            # Crea fitxer de sortida temporal
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
                output_file = f.name
            
            # Converteix
            result = convert_license_to_json(
                license_file, 
                "E4:B3:23:5B:F5:76", 
                output_file
            )
            
            assert result, "La conversió hauria d'haver tingut èxit"
            
            # Verifica el fitxer JSON generat
            with open(output_file, 'r') as f:
                data = json.load(f)
            
            assert "E4:B3:23:5B:F5:76" in data
            device_data = data["E4:B3:23:5B:F5:76"]
            assert device_data["pin"] == "000000"
            assert device_data["key"] == "4a942a522abf710b3c8e61973e3aa17a"
            assert "45b31b6c213dfcc16059010bb107746aa4dbb51589e9192e1b37dd0422e7e30d0cc071dcdbd3fd720928d65ee0ef8e1a" in device_data["token"]
            
        finally:
            # Neteja fitxers temporals
            os.unlink(license_file)
            if os.path.exists(output_file):
                os.unlink(output_file)
    
    def test_convert_license_invalid_format(self):
        """Test conversió amb format de llicència invàlid"""
        # Crea un fitxer amb format incorrecte
        license_content = "contingut_invalid"
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write(license_content)
            license_file = f.name
        
        try:
            result = convert_license_to_json(license_file, "E4:B3:23:5B:F5:76")
            assert not result, "La conversió hauria d'haver fallat amb format invàlid"
            
        finally:
            os.unlink(license_file)
    
    def test_convert_license_file_not_found(self):
        """Test conversió amb fitxer inexistent"""
        result = convert_license_to_json("fitxer_inexistent.csv", "E4:B3:23:5B:F5:76")
        assert not result, "La conversió hauria d'haver fallat amb fitxer inexistent"


class TestUtilities:
    """Tests per a utilitats generals"""
    
    def test_hex_validation(self):
        """Test validació de strings hexadecimals"""
        valid_hex = "4a942a522abf710b3c8e61973e3aa17a"
        invalid_hex = "4a942a522abf710b3c8e61973e3aa17g"  # 'g' no és hex
        
        # Test que es pot convertir a int base 16
        try:
            int(valid_hex, 16)
            valid = True
        except ValueError:
            valid = False
        
        assert valid, "String hexadecimal vàlid hauria de convertir-se"
        
        try:
            int(invalid_hex, 16)
            invalid = False
        except ValueError:
            invalid = True
        
        assert invalid, "String hexadecimal invàlid hauria de fallar"


if __name__ == "__main__":
    pytest.main([__file__])