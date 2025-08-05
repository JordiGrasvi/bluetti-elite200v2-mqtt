#!/usr/bin/env python3
"""
Extreu claus d'encriptació des de logs de Bluetooth capturats.
Suporta fitxers btsnoop_hci.log d'Android i altres formats.

Ús: python extract_keys.py <fitxer_log> [MAC_ADDRESS]
"""

import sys
import struct
import json
from pathlib import Path

class BluetoothLogParser:
    """Parser per a logs de Bluetooth per extreure claus Bluetti"""
    
    def __init__(self, log_file, target_mac=None):
        self.log_file = log_file
        self.target_mac = target_mac.upper() if target_mac else None
        self.extracted_keys = {}
        self.packets = []
    
    def parse_btsnoop_hci(self):
        """Parseja un fitxer btsnoop_hci.log d'Android"""
        print(f"📄 Parseant fitxer btsnoop HCI: {self.log_file}")
        
        try:
            with open(self.log_file, 'rb') as f:
                # Llegeix la capçalera btsnoop
                header = f.read(16)
                if header[:8] != b'btsnoop\x00':
                    print("❌ Error: No és un fitxer btsnoop vàlid")
                    return False
                
                print("✅ Fitxer btsnoop vàlid detectat")
                
                packet_count = 0
                while True:
                    # Llegeix la capçalera del paquet
                    packet_header = f.read(24)
                    if len(packet_header) < 24:
                        break
                    
                    # Extreu informació del paquet
                    original_length, included_length, flags, drops, timestamp = struct.unpack('>IIIIQ', packet_header)
                    
                    # Llegeix les dades del paquet
                    packet_data = f.read(included_length)
                    if len(packet_data) < included_length:
                        break
                    
                    packet_count += 1
                    
                    # Analitza el paquet
                    self.analyze_packet(packet_data, packet_count)
                
                print(f"✅ Processats {packet_count} paquets")
                return True
                
        except Exception as e:
            print(f"❌ Error parseant fitxer: {e}")
            return False
    
    def analyze_packet(self, data, packet_num):
        """Analitza un paquet individual"""
        if len(data) < 4:
            return
        
        # Cerca patrons típics de Bluetti
        hex_data = data.hex()
        
        # Patró 1: Missatges que comencen amb 2A2A (signatura Bluetti)
        if '2a2a' in hex_data:
            print(f"🔋 Paquet {packet_num}: Possible missatge Bluetti trobat")
            print(f"   Dades: {hex_data}")
            self.extract_from_bluetti_message(data, packet_num)
        
        # Patró 2: Cerca claus hexadecimals llargues
        self.search_for_keys(hex_data, packet_num)
    
    def extract_from_bluetti_message(self, data, packet_num):
        """Extreu informació de missatges Bluetti"""
        hex_data = data.hex()
        
        # Cerca el patró 2A2A
        start_pos = hex_data.find('2a2a')
        if start_pos == -1:
            return
        
        # Extreu el missatge Bluetti
        bluetti_msg = hex_data[start_pos:]
        
        if len(bluetti_msg) >= 8:
            # Analitza els opcodes
            opcode1 = bluetti_msg[4:6]
            opcode2 = bluetti_msg[6:8]
            
            print(f"   Opcodes: {opcode1} {opcode2}")
            
            # Si és un missatge llarg, pot contenir claus
            if len(bluetti_msg) > 32:
                print(f"   Missatge llarg detectat ({len(bluetti_msg)//2} bytes)")
                
                # Extreu possibles claus
                payload = bluetti_msg[8:]  # Salta signatura i opcodes
                
                if len(payload) >= 32:  # Almenys 16 bytes per a una clau
                    possible_key = payload[:32]  # Primers 16 bytes
                    print(f"   Possible clau: {possible_key}")
                    
                    self.extracted_keys[f"packet_{packet_num}_key"] = possible_key
                
                if len(payload) >= 64:  # Possible token
                    possible_token = payload[32:64]
                    print(f"   Possible token: {possible_token}")
                    
                    self.extracted_keys[f"packet_{packet_num}_token"] = possible_token
    
    def search_for_keys(self, hex_data, packet_num):
        """Cerca patrons de claus en les dades"""
        
        # Cerca strings hexadecimals de 32 caràcters (16 bytes)
        for i in range(0, len(hex_data) - 32, 2):
            candidate = hex_data[i:i+32]
            
            # Verifica que sigui hexadecimal vàlid
            try:
                int(candidate, 16)
                
                # Evita patrons massa repetitius
                if len(set(candidate)) > 4:  # Almenys 5 caràcters diferents
                    if f"key_32_{candidate}" not in self.extracted_keys:
                        self.extracted_keys[f"key_32_{candidate}"] = candidate
                        
            except ValueError:
                continue
        
        # Cerca strings hexadecimals de 64+ caràcters
        for i in range(0, len(hex_data) - 64, 2):
            candidate = hex_data[i:i+64]
            
            try:
                int(candidate, 16)
                
                if len(set(candidate)) > 8:  # Més diversitat per tokens llargs
                    if f"token_64_{candidate[:16]}" not in self.extracted_keys:
                        self.extracted_keys[f"token_64_{candidate[:16]}"] = candidate
                        
            except ValueError:
                continue
    
    def parse_wireshark_text(self):
        """Parseja un fitxer de text exportat des de Wireshark"""
        print(f"📄 Parseant fitxer de text Wireshark: {self.log_file}")
        
        try:
            with open(self.log_file, 'r') as f:
                content = f.read()
            
            # Cerca línies amb dades hexadecimals
            lines = content.split('\n')
            packet_num = 0
            
            for line in lines:
                line = line.strip()
                
                # Cerca línies que semblin dades hex
                if any(c in line.lower() for c in '0123456789abcdef'):
                    # Extreu només els caràcters hexadecimals
                    hex_chars = ''.join(c for c in line.lower() if c in '0123456789abcdef')
                    
                    if len(hex_chars) >= 8:
                        packet_num += 1
                        self.analyze_packet(bytes.fromhex(hex_chars), packet_num)
            
            print(f"✅ Processades {packet_num} línies amb dades")
            return True
            
        except Exception as e:
            print(f"❌ Error parseant fitxer de text: {e}")
            return False
    
    def save_extracted_keys(self, output_file="extracted_keys.json"):
        """Guarda les claus extretes"""
        if not self.extracted_keys:
            print("⚠️  No s'han extret claus")
            return False
        
        # Organitza les claus per tipus
        organized_keys = {
            "possible_keys_32": [],
            "possible_tokens_64": [],
            "bluetti_messages": [],
            "raw_extractions": self.extracted_keys
        }
        
        # Classifica les claus
        for key_id, value in self.extracted_keys.items():
            if "key_32" in key_id and len(value) == 32:
                organized_keys["possible_keys_32"].append(value)
            elif "token_64" in key_id and len(value) >= 64:
                organized_keys["possible_tokens_64"].append(value)
            elif "packet_" in key_id:
                organized_keys["bluetti_messages"].append({
                    "id": key_id,
                    "value": value
                })
        
        # Elimina duplicats
        organized_keys["possible_keys_32"] = list(set(organized_keys["possible_keys_32"]))
        organized_keys["possible_tokens_64"] = list(set(organized_keys["possible_tokens_64"]))
        
        # Guarda el fitxer
        with open(output_file, 'w') as f:
            json.dump(organized_keys, f, indent=2)
        
        print(f"✅ Claus extretes guardades a {output_file}")
        print(f"   Claus de 32 chars: {len(organized_keys['possible_keys_32'])}")
        print(f"   Tokens de 64+ chars: {len(organized_keys['possible_tokens_64'])}")
        print(f"   Missatges Bluetti: {len(organized_keys['bluetti_messages'])}")
        
        # Mostra les millors candidates
        if organized_keys["possible_keys_32"]:
            print("\n🔑 Millors candidates per a claus:")
            for i, key in enumerate(organized_keys["possible_keys_32"][:3]):
                print(f"   {i+1}. {key}")
        
        if organized_keys["possible_tokens_64"]:
            print("\n🎫 Millors candidates per a tokens:")
            for i, token in enumerate(organized_keys["possible_tokens_64"][:3]):
                print(f"   {i+1}. {token[:32]}...{token[-32:]}")
        
        return True
    
    def run_extraction(self):
        """Executa l'extracció completa"""
        print("🔧 Extractor de claus Bluetti")
        print("=" * 50)
        
        # Determina el tipus de fitxer
        file_path = Path(self.log_file)
        
        if not file_path.exists():
            print(f"❌ Error: Fitxer no trobat: {self.log_file}")
            return False
        
        success = False
        
        # Prova diferents parsers segons l'extensió
        if file_path.suffix.lower() in ['.log', '.hci']:
            # Prova primer com btsnoop
            try:
                success = self.parse_btsnoop_hci()
            except:
                # Si falla, prova com text
                success = self.parse_wireshark_text()
        else:
            # Fitxers de text
            success = self.parse_wireshark_text()
        
        if success:
            return self.save_extracted_keys()
        else:
            return False

def main():
    if len(sys.argv) < 2:
        print("Extractor de claus d'encriptació Bluetti")
        print()
        print("Ús:")
        print("  python extract_keys.py <fitxer_log> [MAC_ADDRESS]")
        print()
        print("Fitxers suportats:")
        print("  - btsnoop_hci.log (Android)")
        print("  - Exports de text de Wireshark")
        print("  - Logs de captura Bluetooth")
        print()
        print("Exemples:")
        print("  python extract_keys.py btsnoop_hci.log")
        print("  python extract_keys.py capture.txt E4:B3:23:5B:F5:76")
        sys.exit(1)
    
    log_file = sys.argv[1]
    mac_address = sys.argv[2] if len(sys.argv) > 2 else None
    
    extractor = BluetoothLogParser(log_file, mac_address)
    
    try:
        success = extractor.run_extraction()
        
        if success:
            print("\n🎉 Extracció completada!")
            print("   Revisa el fitxer extracted_keys.json per veure els resultats")
            print("   Utilitza les claus candidates per crear encryption_keys.json")
        else:
            print("\n❌ Extracció fallida")
            print("   Verifica que el fitxer sigui un log de Bluetooth vàlid")
        
        sys.exit(0 if success else 1)
        
    except KeyboardInterrupt:
        print("\n⏹️  Extracció cancel·lada per l'usuari")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error inesperat: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()