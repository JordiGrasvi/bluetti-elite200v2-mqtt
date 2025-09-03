#!/usr/bin/env python3
"""
Converteix un fitxer de llicència Bluetti (CSV) al format JSON necessari
per a l'aplicació MQTT.

Ús: python convert_license.py bluetti_device_licence.csv [MAC_ADDRESS]
"""

import sys
import json
import os

def convert_license_to_json(license_file, mac_address=None, output_file="encryption_keys.json"):
    """
    Converteix un fitxer de llicència CSV al format JSON
    
    Args:
        license_file: Ruta al fitxer de llicència CSV
        mac_address: Adreça MAC del dispositiu (opcional)
        output_file: Fitxer de sortida JSON
    """
    
    try:
        # Llegeix i normalitza (ignorem línies buides)
        with open(license_file, 'r') as f:
            raw_lines = [l.strip() for l in f.readlines()]

        lines = [l for l in raw_lines if l]

        # Formats acceptats (després de filtrar buides):
        # 4 línies: bluetti, timestamp, md5_key, encryption_key
        # 5+ línies: (legacy) bluetti pot anar precedit d'una línia buida en l'arxiu original
        if len(lines) < 4:
            print("❌ Error: El fitxer de llicència no té el format mínim (4 línies no buides)")
            print("   Format esperat simplificat:")
            print("     1: bluetti")
            print("     2: timestamp")
            print("     3: clau MD5")
            print("     4: clau d'encriptació")
            return False

        # Si hi hagués més línies, agafem les primeres vàlides en ordre
        # (això dóna tolerància a formats futurs amb metadades extra)
        bluetti_marker = lines[0].lower()
        if bluetti_marker != 'bluetti':
            # Algunes variants poden tenir primera línia tipus BOM o text; intentem localitzar 'bluetti'
            try:
                idx = [i for i, v in enumerate(lines) if v.lower() == 'bluetti'][0]
                lines = lines[idx:]
                if len(lines) < 4:
                    raise ValueError("No hi ha prou línies després del marcador bluetti")
            except Exception:
                print("❌ Error: No s'ha trobat el marcador 'bluetti' a la primera línia")
                return False

        timestamp = lines[1].strip()
        md5_key = lines[2].strip()
        encryption_key = lines[3].strip()
        
        print(f"📄 Processant fitxer de llicència:")
        print(f"   Timestamp: {timestamp}")
        print(f"   MD5 Key: {md5_key[:16]}...{md5_key[-16:]}")
        print(f"   Encryption Key: {encryption_key[:32]}...{encryption_key[-32:]}")
        
        # Si no s'ha proporcionat MAC, demana-la
        if not mac_address:
            mac_address = input("\n🔍 Introdueix l'adreça MAC del dispositiu (XX:XX:XX:XX:XX:XX): ").strip()
        
        # Valida el format de la MAC
        if not validate_mac_address(mac_address):
            print("❌ Error: Format d'adreça MAC invàlid")
            return False
        
        # Crea l'estructura JSON
        # Nota: Utilitzem la clau MD5 com a 'key' i la clau d'encriptació com a 'token'
        # Aquest mapatge pot necessitar ajustos segons el protocol específic
        encryption_data = {
            mac_address: {
                "pin": "000000",  # PIN per defecte
                "key": md5_key,
                "token": encryption_key
            }
        }
        
        # Guarda el fitxer JSON
        with open(output_file, 'w') as f:
            json.dump(encryption_data, f, indent=2)
        
        print(f"\n✅ Conversió completada!")
        print(f"   Fitxer generat: {output_file}")
        print(f"   Dispositiu: {mac_address}")
        
        # Mostra instruccions
        print(f"\n📋 Instruccions:")
        print(f"   1. Copia el fitxer {output_file} al directori arrel del projecte")
        print(f"   2. Actualitza el fitxer .env amb BLUETTI_MAC={mac_address}")
        print(f"   3. Executa python tools/verify_keys.py per verificar les claus")
        
        return True
        
    except FileNotFoundError:
        print(f"❌ Error: No s'ha trobat el fitxer {license_file}")
        return False
    except Exception as e:
        print(f"❌ Error processant el fitxer: {e}")
        return False

def validate_mac_address(mac):
    """Valida el format d'una adreça MAC"""
    if not mac:
        return False
    
    parts = mac.split(':')
    if len(parts) != 6:
        return False
    
    for part in parts:
        if len(part) != 2:
            return False
        try:
            int(part, 16)
        except ValueError:
            return False
    
    return True

def main():
    if len(sys.argv) < 2:
        print("Ús: python convert_license.py <fitxer_llicencia.csv> [MAC_ADDRESS]")
        print()
        print("Exemple:")
        print("  python convert_license.py bluetti_device_licence.csv")
        print("  python convert_license.py bluetti_device_licence.csv E4:B3:23:5B:F5:76")
        sys.exit(1)
    
    license_file = sys.argv[1]
    mac_address = sys.argv[2] if len(sys.argv) > 2 else None
    
    print("🔧 Convertidor de llicència Bluetti a JSON")
    print("=" * 50)
    
    if convert_license_to_json(license_file, mac_address):
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()