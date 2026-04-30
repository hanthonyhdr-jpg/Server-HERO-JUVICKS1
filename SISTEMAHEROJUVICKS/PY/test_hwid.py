import hashlib
import subprocess

def get_hwid():
    serial = ""
    try:
        cmd_mb = "wmic baseboard get serialnumber"
        output = subprocess.check_output(cmd_mb, shell=True).decode().split('\n')
        if len(output) > 1: serial = output[1].strip()
        
        if not serial or "To be filled" in serial or "None" in serial:
            cmd_disk = "wmic diskdrive get serialnumber"
            output_d = subprocess.check_output(cmd_disk, shell=True).decode().split('\n')
            if len(output_d) > 1: serial = output_d[1].strip()
            
        if not serial or "None" in serial:
            import uuid
            serial = str(uuid.getnode())

        raw_hwid = hashlib.sha256(serial.encode()).hexdigest().upper()[:12]
        return f"{raw_hwid[:4]}-{raw_hwid[4:8]}-{raw_hwid[8:]}"
    except Exception as e:
        print(f"Error in get_hwid: {e}")
        import uuid
        node = str(uuid.getnode())
        raw_hwid = hashlib.sha256(node.encode()).hexdigest().upper()[:12]
        return f"{raw_hwid[:4]}-{raw_hwid[4:8]}-{raw_hwid[8:]}"

print(get_hwid())
