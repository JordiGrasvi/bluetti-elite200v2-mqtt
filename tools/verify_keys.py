#!/usr/bin/env python3
"""
Verifica que les claus d'encriptació siguin correctes provant
una connexió bàsica amb el dispositiu Bluetti.

Ús: python verify_keys.py [MAC_ADDRESS]
"""

import sys
import json
import asyncio
import os
from pathlib import Path

# Afegeix el directori pare al path per importar els mòduls
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from bleak import BleakClient, BleakScanner
except ImportError:
    print("❌ Error: bleak no està instal·lat")
    print("   Executa: pip install bleak")
    sys.exit(1)

class KeyVerifier:
    """Verifica les claus d'encriptació del dispositiu Bluetti"""
    
    # UUIDs estàndard per a dispositius Bluetti
    NOTIFICATION_UUID = "0000ff01-0000-1000-8000-00805f9b34fb"
    WRITE_UUID = "0000ff02-0000-1000-8000-00805f9b34fb"
    
    def __init__(self, mac_address, keys_file="encryption_keys.json"):
        self.mac_address = mac_address
        self.keys_file = keys_file
        self.keys = None
        self.client = None
        
    def load_keys(self):
        """Carrega les claus des del fitxer JSON"""
        try:
            if not os.path.exists(self.keys_file):
                print(f"❌ Error: No s'ha trobat el fitxer {self.keys_file}")
                return False
            
            with open(self.keys_file, 'r') as f:
                all_keys = json.load(f)
            
            if self.mac_address not in all_keys:
                print(f"❌ Error: No s'han trobat claus per al dispositiu {self.mac_address}")
                print(f"   Dispositius disponibles: {list(all_keys.keys())}")
                return False
            
            self.keys = all_keys[self.mac_address]
            
            # Valida que tingui tots els camps necessaris
            required_fields = ['pin', 'key', 'token']
            for field in required_fields:
                if field not in self.keys:
                    print(f"❌ Error: Falta el camp '{field}' a les claus")
                    return False
            
            print("✅ Claus carregades correctament")
            print(f"   PIN: {self.keys['pin']}")
            print(f"   Key: {self.keys['key'][:8]}...{self.keys['key'][-8:]}")
            print(f"   Token: {self.keys['token'][:16]}...{self.keys['token'][-16:]}")
            
            return True
            
        except json.JSONDecodeError as e:
            print(f"❌ Error: El fitxer JSON no és vàlid: {e}")
            return False
        except Exception as e:
            print(f"❌ Error carregant les claus: {e}")
            return False
    
    async def scan_for_device(self):
        """Escaneja per trobar el dispositiu"""
        print(f"🔍 Escaneant dispositius Bluetooth...")
        
        try:
            devices = await BleakScanner.discover(timeout=10)
            
            # Cerca el dispositiu per MAC
            target_device = None
            for device in devices:
                if device.address.upper() == self.mac_address.upper():
                    target_device = device
                    break
            
            if target_device:
                print(f"✅ Dispositiu trobat: {target_device.name or 'Sense nom'} ({target_device.address})")
                return target_device
            else:
                print(f"❌ No s'ha trobat el dispositiu {self.mac_address}")
                print("   Dispositius trobats:")
                for device in devices:
                    print(f"     {device.address}: {device.name or 'Sense nom'}")
                return None
                
        except Exception as e:
            print(f"❌ Error escaneant: {e}")
            return None
    
    async def test_connection(self):
        """Prova la connexió bàsica amb el dispositiu"""
        print(f"🔗 Provant connexió amb {self.mac_address}...")
        
        try:
            self.client = BleakClient(self.mac_address)
            await self.client.connect()
            
            print("✅ Connexió Bluetooth establerta")
            
            # Descobreix serveis
            services = await self.client.get_services()
            
            # Verifica que els serveis necessaris existeixin
            notification_found = False
            write_found = False
            
            for service in services:
                for char in service.characteristics:
                    if char.uuid.lower() == self.NOTIFICATION_UUID.lower():
                        notification_found = True
                    elif char.uuid.lower() == self.WRITE_UUID.lower():
                        write_found = True
            
            if notification_found and write_found:
                print("✅ Serveis Bluetti trobats")
                return True
            else:
                print("❌ Serveis Bluetti no trobats")
                print(f"   Notificació: {'✅' if notification_found else '❌'}")
                print(f"   Escriptura: {'✅' if write_found else '❌'}")
                return False
                
        except Exception as e:
            print(f"❌ Error de connexió: {e}")
            return False
    
    async def test_basic_communication(self):
        """Prova comunicació bàsica (sense encriptació completa)"""
        print("📡 Provant comunicació bàsica...")
        
        try:
            # Configura handler per a notificacions
            received_data = []
            
            def notification_handler(sender, data):
                received_data.append(data)
                print(f"   📨 Rebut: {data.hex()}")
            
            # Inicia notificacions
            await self.client.start_notify(self.NOTIFICATION_UUID, notification_handler)
            print("✅ Notificacions iniciades")
            
            # Espera missatges inicials
            await asyncio.sleep(5)
            
            if received_data:
                print(f"✅ Rebuts {len(received_data)} missatges")
                
                # Analitza els missatges
                for i, data in enumerate(received_data[:3]):  # Mostra només els primers 3
                    print(f"   Missatge {i+1}: {data.hex()}")
                    if len(data) >= 2 and data[0] == 0x2A and data[1] == 0x2A:
                        print(f"     -> Missatge encriptat detectat")
            else:
                print("⚠️  No s'han rebut missatges (pot ser normal)")
            
            # Para notificacions
            await self.client.stop_notify(self.NOTIFICATION_UUID)
            
            return True
            
        except Exception as e:
            print(f"❌ Error en comunicació: {e}")
            return False
    
    async def disconnect(self):
        """Desconnecta del dispositiu"""
        if self.client:
            try:
                await self.client.disconnect()
                print("✅ Desconnectat")
            except:
                pass
    
    async def run_verification(self):
        """Executa la verificació completa"""
        print("🔧 Verificador de claus Bluetti")
        print("=" * 50)
        
        # 1. Carrega les claus
        if not self.load_keys():
            return False
        
        print()
        
        # 2. Escaneja el dispositiu
        device = await self.scan_for_device()
        if not device:
            return False
        
        print()
        
        # 3. Prova la connexió
        if not await self.test_connection():
            return False
        
        print()
        
        # 4. Prova comunicació bàsica
        success = await self.test_basic_communication()
        
        print()
        
        # 5. Desconnecta
        await self.disconnect()
        
        if success:
            print("🎉 Verificació completada amb èxit!")
            print("   Les claus semblen ser correctes.")
            print("   Pots procedir a executar l'aplicació MQTT.")
        else:
            print("⚠️  Verificació parcial.")
            print("   La connexió funciona però cal verificar l'encriptació.")
        
        return success

async def main():
    # Determina l'adreça MAC
    mac_address = None
    
    if len(sys.argv) > 1:
        mac_address = sys.argv[1]
    else:
        # Prova de carregar des del fitxer .env
        env_file = Path(__file__).parent.parent / ".env"
        if env_file.exists():
            with open(env_file, 'r') as f:
                for line in f:
                    if line.startswith('BLUETTI_MAC='):
                        mac_address = line.split('=', 1)[1].strip()
                        break
    
    if not mac_address:
        print("Ús: python verify_keys.py [MAC_ADDRESS]")
        print()
        print("O configura BLUETTI_MAC al fitxer .env")
        sys.exit(1)
    
    # Executa la verificació
    verifier = KeyVerifier(mac_address)
    
    try:
        success = await verifier.run_verification()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⏹️  Verificació cancel·lada per l'usuari")
        await verifier.disconnect()
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error inesperat: {e}")
        await verifier.disconnect()
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())