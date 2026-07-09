import time
import snap7
from snap7.util import get_bool, set_bool

# Connection details
PLC_IP = "192.168.0.1"  # Target your S7-1200 IP
DB_NUMBER = 1           # DB1 (Python_Bridge)
RACK = 0
SLOT = 1

client = snap7.client.Client()

try:
    client.connect(PLC_IP, RACK, SLOT)
    print("Connected to S7-1200 successfully!")
    print("Monitoring PLC Input (I0.0)... Press Ctrl+C to exit.")
    
    counter = 0
    while True:
        # 1. READ: Read 1 byte from DB1 starting at offset 0 (covers offsets 0.0 to 0.7)
        db_data = client.db_read(DB_NUMBER, 0, 1)
        
        # Extract Button_Status from DB1.DBX0.0
        button_pressed = get_bool(db_data, 0, 0)
        
        if button_pressed:
            print("🟢 PLC Push Button is currently: PRESSED (True)")
        else:
            print("🔴 PLC Push Button is currently: RELEASED (False)")
            
        # 2. WRITE SIMULATION: After 5 seconds of running, Python will send the stop command
        counter += 1
        if counter == 10:  # Roughly 5 seconds (10 loops * 0.5s delay)
            print("\n⚠️ Python sending STOP command to PLC output...")
            
            # Fetch the fresh byte structure first to avoid overwriting other bits
            write_buffer = client.db_read(DB_NUMBER, 0, 1)
            
            # Set Python_Stop_Cmd (DB1.DBX0.1) to True
            set_bool(write_buffer, 0, 1, True)
            
            # Write it back to the PLC
            client.db_write(DB_NUMBER, 0, write_buffer)
            print("🛑 Stop command written to DB1.DBX0.1. PLC output forced OFF.")
            
        time.sleep(0.5)

except KeyboardInterrupt:
    print("\nExiting script...")

except Exception as e:
    print(f"Error: {e}")

finally:
    if client.get_connected():
        # Clean up by resetting the stop command before disconnecting
        try:
            reset_buffer = client.db_read(DB_NUMBER, 0, 1)
            set_bool(reset_buffer, 0, 1, False)
            client.db_write(DB_NUMBER, 0, reset_buffer)
        except:
            pass
        client.disconnect()
        print("Disconnected from PLC.")