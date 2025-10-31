import socket
import time
import random

# Configuration
FRAME_COUNT = 5
LOSS_PROBABILITY = 0.3
TIMEOUT = 3
HOST = '127.0.0.1'
PORT = 5001

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.settimeout(TIMEOUT)

frame_no = 0

print("Sender started...\n")

while frame_no < FRAME_COUNT:
    print(f"📤 Sending Frame {frame_no}...")
    
    # Simulate frame loss before sending
    if random.random() < LOSS_PROBABILITY:
        print(f"❌ Frame {frame_no} lost before sending (simulated)")
        time.sleep(1)
        continue

    # Send frame
    sock.sendto(str(frame_no).encode(), (HOST, PORT))

    try:
        ack, _ = sock.recvfrom(1024)
        ack_no = int(ack.decode())

        if ack_no == frame_no:
            print(f"✅ ACK {ack_no} received. Moving to next frame.\n")
            frame_no += 1
        else:
            print(f"⚠️ Wrong ACK {ack_no}, retransmitting Frame {frame_no}...\n")

    except socket.timeout:
        print(f"⏱️ Timeout! Retransmitting Frame {frame_no}...\n")

print("🎉 All frames transmitted successfully with Stop-and-Wait ARQ!")
# After finishing all frames
sock.sendto("EXIT".encode(), (HOST, PORT))
print("Sender sent EXIT signal. Closing socket.")
sock.close()

