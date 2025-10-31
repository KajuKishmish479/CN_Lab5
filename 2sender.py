# sender.py
import socket
import time
import random
import argparse

parser = argparse.ArgumentParser(description="Go-Back-N ARQ Sender")
parser.add_argument("--host", default="127.0.0.1")
parser.add_argument("--port", type=int, default=5001)
parser.add_argument("--total", type=int, default=20, help="total frames to send")
parser.add_argument("--window", type=int, default=4, help="window size (N)")
parser.add_argument("--loss", type=float, default=0.2, help="loss prob for frames/acks (used for simulated pre-send loss)")
parser.add_argument("--timeout", type=float, default=2.0, help="timeout (seconds)")
args = parser.parse_args()

HOST = args.host
PORT = args.port
TOTAL = args.total
WINDOW = args.window
LOSS_PROB = args.loss
TIMEOUT = args.timeout

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.settimeout(0.2)  # short recv timeout to check for ACKs frequently

base = 0        # oldest unacked frame
next_seq = 0    # next frame to send
timer_start = None

print(f"Sender -> Sending {TOTAL} frames with window={WINDOW}, loss={LOSS_PROB}, timeout={TIMEOUT}\n")

def send_frame(seq):
    """Send FRAME:seq over UDP (actual send, but we can simulate pre-send loss here)."""
    msg = f"FRAME:{seq}".encode()
    sock.sendto(msg, (HOST, PORT))
    print(f"📤 Sent FRAME {seq}")

try:
    while base < TOTAL:
        # send while window not full and frames remaining
        while next_seq < base + WINDOW and next_seq < TOTAL:
            # Simulate pre-send frame loss: we will *not send* the packet and just print loss
            if random.random() < LOSS_PROB:
                print(f"❌ Frame {next_seq} simulated lost before send.")
                # we still advance next_seq in GBn? NO: in real channel the sender sent but it was lost.
                # To simulate a sent-but-lost packet we will NOT call send_frame but we will behave as if it was sent.
                # For clarity, we'll act like the send happened but the channel lost it (i.e., we do not call sendto).
                # However, to make retransmission logic simple we should still consider it sent: we increment next_seq.
                next_seq += 1
                if timer_start is None:
                    timer_start = time.time()
                continue

            send_frame(next_seq)
            if timer_start is None:
                timer_start = time.time()
            next_seq += 1

        # Try to receive ACKs (non-blocking due to short timeout)
        try:
            data, _ = sock.recvfrom(1024)
            ack_msg = data.decode()
            if ack_msg.startswith("ACK:"):
                ack_num = int(ack_msg.split(":")[1])
                print(f"⬅️  Received {ack_msg}")

                # Cumulative ACK: all frames < ack_num are acknowledged
                if ack_num > base:
                    base = ack_num
                    # restart timer if there are outstanding frames
                    if base == next_seq:
                        timer_start = None
                    else:
                        timer_start = time.time()
                    print(f"🔁 Window slides: base={base}, next_seq={next_seq}\n")
                else:
                    print(f"(duplicate or old ACK {ack_num}, base={base})\n")

        except socket.timeout:
            # no ACK arrived within small recv timeout; fall through to timeout checking
            pass

        # Check timer for oldest unacked frame
        if timer_start is not None and (time.time() - timer_start) >= TIMEOUT:
            # timeout: retransmit all frames from base to next_seq-1
            print(f"⏱️ Timeout occured for base={base}. Retransmitting frames {base} to {next_seq - 1}")
            # retransmit all frames in window [base, next_seq)
            for seq in range(base, next_seq):
                # simulate possibility that retransmitted frame might also be lost BEFORE send (channel)
                if random.random() < LOSS_PROB:
                    print(f"❌ (re)Frame {seq} simulated lost before send.")
                    continue
                send_frame(seq)
            timer_start = time.time()
            print("")
    # done sending all frames
    print("🎉 All frames acknowledged by receiver.")

    # tell receiver to exit
    sock.sendto("EXIT".encode(), (HOST, PORT))
    print("Sent EXIT signal to receiver. Closing sender socket.")

except KeyboardInterrupt:
    print("Sender interrupted by user.")
finally:
    sock.close()