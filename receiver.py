import socket
import random
import time

# Configuration
LOSS_PROBABILITY = 0.3
HOST = '127.0.0.1'
PORT = 5001

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((HOST, PORT))

print("Receiver is ready and waiting for frames...\n")

expected_frame = 0

while True:
    try:
        data, addr = sock.recvfrom(1024)
        frame_no = int(data.decode())

        # Simulate frame loss
        if random.random() < LOSS_PROBABILITY:
            print(f"❌ Frame {frame_no} lost (simulated)")
            continue

        print(f"📩 Frame {frame_no} received successfully")

        # Simulate processing delay
        time.sleep(1)

        # Send ACK
        if random.random() < LOSS_PROBABILITY:
            print(f"⚠️  ACK {frame_no} lost (simulated)\n")
            continue

        ack_msg = f"{frame_no}"
        sock.sendto(ack_msg.encode(), addr)
        print(f"✅ ACK {frame_no} sent\n")

        expected_frame += 1

        

    except KeyboardInterrupt:
        print("Receiver shutting down...")
        break
