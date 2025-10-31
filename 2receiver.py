# receiver.py
import socket
import random
import time
import argparse

parser = argparse.ArgumentParser(description="Go-Back-N ARQ Receiver")
parser.add_argument("--host", default="127.0.0.1")
parser.add_argument("--port", type=int, default=5001)
parser.add_argument("--loss", type=float, default=0.2, help="loss probability for frames/acks")
args = parser.parse_args()

HOST = args.host
PORT = args.port
LOSS_PROB = args.loss

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((HOST, PORT))
print(f"Receiver listening on {HOST}:{PORT}  (loss={LOSS_PROB})\n")

expected = 0  # next expected frame number

try:
    while True:
        data, addr = sock.recvfrom(1024)
        msg = data.decode()

        if msg == "EXIT":
            print("🚪 Exit signal received. Shutting down receiver.")
            break

        # incoming frame assumed to be "FRAME:<seq>"
        if not msg.startswith("FRAME:"):
            continue

        seq = int(msg.split(":")[1])

        # Simulate frame loss
        if random.random() < LOSS_PROB:
            print(f"❌ Frame {seq} lost (simulated).")
            # drop the frame: do not update expected and do not send ACK
            continue

        # Received frame
        if seq == expected:
            print(f"📥 Frame {seq} received in order. Delivering to upper layer.")
            expected += 1
        else:
            print(f"📥 Frame {seq} received but out-of-order (expected {expected}). Discarding.")

        # Prepare cumulative ACK = expected (meaning all frames < expected received)
        ack_msg = f"ACK:{expected}"

        # Simulate ACK loss
        if random.random() < LOSS_PROB:
            print(f"⚠️  ACK {expected} lost (simulated).")
            continue

        sock.sendto(ack_msg.encode(), addr)
        print(f"✅ Sent cumulative {ack_msg}\n")

except KeyboardInterrupt:
    print("Receiver interrupted, shutting down.")
finally:
    sock.close()
