#!/usr/bin/env python3
"""
Prova la connexió amb el dispositiu Bluetti sense necessitat de claus.
Útil per verificar que el dispositiu és accessible via Bluetooth.

Ús: python test_connection.py [MAC_ADDRESS]
"""

import sys
import asyncio
from pathlib import Path

# Afegeix el directori pare al path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from bleak import BleakClient, BleakScanner
except ImportError:
    print("❌ Error: bleak no està instal·lat")
    print("   Executa: pip install bleak")
    sys.exit(1)

class ConnectionTester:
    """Prova la connexió bàsica amb dispositius Bluetti"""
    
    def __init__(self, mac_address=None):
        self.mac_address = mac_address
        self.client = None
    
    async def scan_all_devices(self):
        """Escaneja tots els dispositius Bluetooth disponibles"""
        print("🔍 Escaneant tots els dispositius Bluetooth...")
        
        try:
            devices = await BleakScanner.discover(timeout=15)
            
            if not devices:
                print("❌ No s'han trobat dispositius Bluetooth")
                return []
            
            print(f"✅ Trobats {len(devices)} dispositius:")
            
            bluetti_devices = []
            
            for device in devices:
                name = device.name or "Sense nom"
                rssi = getattr(device, 'rssi', 'N/A')
                
                # Identifica possibles dispositius Bluetti
                is_bluetti = any(keyword in name.lower() for keyword in 
                               ['bluetti', 'elite', 'ac200', 'ac300', 'eb200', 'eb240'])
                
                marker = "🔋" if is_bluetti else "📱"
                print(f"   {marker} {device.address}: {name} (RSSI: {rssi})")
                
                if is_bluetti:
                    bluetti_devices.append(device)
            
            if bluetti_devices:
                print(f"\n🔋 Dispositius Bluetti detectats: {len(bluetti_devices)}")
            else:
                print("\n⚠️  No s'han detectat dispositius Bluetti pel nom")
                print("   Prova amb una adreça MAC específica si coneixes el dispositiu")
            
            return devices
            
        except Exception as e:
            print(f"❌ Error escaneant: {e}")
            return []
    
    async def test_specific_device(self, mac_address):
        """Prova la connexió amb un dispositiu específic"""
        print(f"🔗 Provant connexió amb {mac_address}...")
        
        try:
            self.client = BleakClient(mac_address)
            
            # Prova de connectar
            await self.client.connect()
            print("✅ Connexió establerta correctament")
            
            # Obté informació del dispositiu
            print(f"   Connectat: {self.client.is_connected}")
            
            # Descobreix serveis
            print("🔍 Descobrint serveis...")
            services = await self.client.get_services()
            
            print(f"✅ Trobats {len(services)} serveis:")
            
            bluetti_services = []
            
            for service in services:
                print(f"   📋 Servei: {service.uuid}")
                
                for char in service.characteristics:
                    properties = ", ".join(char.properties)
                    print(f"      📄 Característica: {char.uuid} ({properties})")
                    
                    # Identifica serveis típics de Bluetti
                    if "ff01" in char.uuid or "ff02" in char.uuid:
                        bluetti_services.append(char)
                        print(f"         🔋 Possible servei Bluetti detectat!")
            
            if bluetti_services:
                print(f"\n🎉 Dispositiu Bluetti confirmat!")
                print(f"   Serveis Bluetti trobats: {len(bluetti_services)}")
                
                # Prova de llegir alguna característica (si és possible)
                await self.test_basic_read(bluetti_services)
            else:
                print(f"\n⚠️  No s'han trobat serveis típics de Bluetti")
                print("   Pot ser un dispositiu Bluetti amb UUIDs diferents")
            
            return True
            
        except Exception as e:
            print(f"❌ Error de connexió: {e}")
            return False
    
    async def test_basic_read(self, bluetti_services):
        """Prova de llegir dades bàsiques (sense encriptació)"""
        print("📖 Provant lectura bàsica...")
        
        for char in bluetti_services[:2]:  # Prova només els primers 2
            try:
                if "read" in char.properties:
                    data = await self.client.read_gatt_char(char.uuid)
                    print(f"   📨 {char.uuid}: {data.hex()} ({len(data)} bytes)")
                elif "notify" in char.properties:
                    print(f"   🔔 {char.uuid}: Suporta notificacions")
                    
                    # Prova d'escoltar notificacions breument
                    received_data = []
                    
                    def handler(sender, data):
                        received_data.append(data)
                        print(f"      📨 Notificació: {data.hex()}")
                    
                    await self.client.start_notify(char.uuid, handler)
                    await asyncio.sleep(3)
                    await self.client.stop_notify(char.uuid)
                    
                    if received_data:
                        print(f"      ✅ Rebudes {len(received_data)} notificacions")
                    else:
                        print(f"      ⚠️  No s'han rebut notificacions")
                        
            except Exception as e:
                print(f"   ❌ Error llegint {char.uuid}: {e}")
    
    async def disconnect(self):
        """Desconnecta del dispositiu"""
        if self.client:
            try:
                await self.client.disconnect()
                print("✅ Desconnectat")
            except:
                pass
    
    async def run_test(self):
        """Executa el test complet"""
        print("🔧 Test de connexió Bluetti")
        print("=" * 50)
        
        try:
            if self.mac_address:
                # Test d'un dispositiu específic
                success = await self.test_specific_device(self.mac_address)
            else:
                # Escaneja tots els dispositius
                devices = await self.scan_all_devices()
                
                # Si hi ha dispositius Bluetti, prova el primer
                bluetti_devices = [d for d in devices if d.name and 
                                 any(keyword in d.name.lower() for keyword in 
                                     ['bluetti', 'elite', 'ac200', 'ac300', 'eb200', 'eb240'])]
                
                if bluetti_devices:
                    print(f"\n🔋 Provant el primer dispositiu Bluetti: {bluetti_devices[0].address}")
                    success = await self.test_specific_device(bluetti_devices[0].address)
                else:
                    print("\n⚠️  No s'han trobat dispositius Bluetti automàticament")
                    print("   Especifica una adreça MAC per provar un dispositiu concret")
                    success = False
            
            return success
            
        finally:
            await self.disconnect()

def load_mac_from_env():
    """Carrega l'adreça MAC des del fitxer .env"""
    env_file = Path(__file__).parent.parent / ".env"
    if env_file.exists():
        with open(env_file, 'r') as f:
            for line in f:
                if line.startswith('BLUETTI_MAC='):
                    return line.split('=', 1)[1].strip()
    return None

async def main():
    mac_address = None
    
    if len(sys.argv) > 1:
        mac_address = sys.argv[1]
    else:
        # Prova de carregar des del .env
        mac_address = load_mac_from_env()
        if mac_address:
            print(f"📋 Utilitzant MAC des de .env: {mac_address}")
    
    tester = ConnectionTester(mac_address)
    
    try:
        success = await tester.run_test()
        
        if success:
            print("\n🎉 Test completat amb èxit!")
            print("   El dispositiu és accessible via Bluetooth")
            if mac_address:
                print("   Pots procedir a configurar les claus d'encriptació")
        else:
            print("\n❌ Test fallit")
            print("   Verifica que:")
            print("   - El dispositiu estigui encès i a prop")
            print("   - L'adreça MAC sigui correcta")
            print("   - No hi hagi altres aplicacions connectades")
        
        sys.exit(0 if success else 1)
        
    except KeyboardInterrupt:
        print("\n⏹️  Test cancel·lat per l'usuari")
        await tester.disconnect()
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error inesperat: {e}")
        await tester.disconnect()
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] in ['-h', '--help']:
        print("Test de connexió per a dispositius Bluetti")
        print()
        print("Ús:")
        print("  python test_connection.py                    # Escaneja tots els dispositius")
        print("  python test_connection.py XX:XX:XX:XX:XX:XX  # Prova un dispositiu específic")
        print()
        print("Aquest script no necessita claus d'encriptació, només prova la connexió Bluetooth bàsica.")
        sys.exit(0)
    
    asyncio.run(main())