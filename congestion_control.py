import random
import math
import matplotlib.pyplot as plt

def simulate_tcp_cwnd(
    rounds=100,
    loss_prob=0.02,
    initial_cwnd=1.0,
    initial_ssthresh=32.0,
    seed=None,
    verbose=False
):
    if seed is not None:
        random.seed(seed)

    cwnd = float(initial_cwnd)
    ssthresh = float(initial_ssthresh)
    mode = "slow_start"  # or "cong_avoid" (congestion avoidance)

    cwnd_history = []
    ssthresh_history = []
    mode_history = []
    rounds_list = []

    for r in range(1, rounds + 1):
        rounds_list.append(r)
        cwnd_history.append(cwnd)
        ssthresh_history.append(ssthresh)
        mode_history.append(mode)

        if verbose:
            print(f"Round {r:3d}: cwnd={cwnd:.3f}, ssthresh={ssthresh:.3f}, mode={mode}")

        # In one RTT the sender can send roughly floor(cwnd) packets (MSS units).
        # Simulate packet-by-packet loss in that RTT.
        # If any packet in the window is lost during that RTT, treat as packet loss event.
        packets_to_send = max(1, int(math.floor(cwnd)))  # at least 1 packet
        loss_happened = False

        # Simulate each packet's chance of being lost
        for p in range(packets_to_send):
            if random.random() < loss_prob:
                loss_happened = True
                break

        if loss_happened:
            prev_cwnd = cwnd
            ssthresh = max(2.0, prev_cwnd / 2.0)  # ssthresh at least 2 MSS to avoid zero
            cwnd = 1.0
            mode = "slow_start"
            if verbose:
                print(
                    f"  >>> Packet loss detected (round {r}). "
                    f"ssthresh <- {ssthresh:.3f}, cwnd <- {cwnd:.3f} (timeout reaction)\n"
                )
            # move to next round after timeout
            continue

        if mode == "slow_start":
            cwnd += packets_to_send  # additive per-ACK -> exponential growth per RTT
            # Condition to move to congestion avoidance: cwnd >= ssthresh
            if cwnd >= ssthresh:
                mode = "cong_avoid"
        else:
            cwnd += 1.0

        # keep cwnd reasonable (avoid extremely large numbers)
        cwnd = min(cwnd, 1e6)

    return rounds_list, cwnd_history, ssthresh_history, mode_history

def plot_cwnd(rounds, cwnd, ssthresh=None, filename="plot.png", show=False):
    """
    Plot cwnd vs rounds and save to filename.
    """
    plt.figure(figsize=(10, 5))
    plt.plot(rounds, cwnd, linewidth=2)
    if ssthresh is not None:
        # plot ssthresh as horizontal/step line for reference
        # convert ssthresh history to a line
        plt.plot(rounds, ssthresh, linestyle='dashed', linewidth=1)
        plt.legend(["cwnd", "ssthresh"])
    else:
        plt.legend(["cwnd"])
    plt.xlabel("Transmission Round (RTT)")
    plt.ylabel("Congestion Window (MSS units)")
    plt.title("TCP Congestion Window Evolution (Slow Start & Congestion Avoidance)")
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(filename)
    if show:
        plt.show()
    plt.close()
    print(f"Plot saved as {filename}")

if __name__ == "__main__":
    # --- PARAMETERS (tweak these) ---
    TOTAL_ROUNDS = 120
    LOSS_PROBABILITY = 0.03   # 3% packet loss probability per packet
    INITIAL_CWND = 1.0
    INITIAL_SSTHRESH = 32.0
    RANDOM_SEED = 42
    VERBOSE = False
    # -------------------------------

    rounds, cwnd_hist, ssthresh_hist, mode_hist = simulate_tcp_cwnd(
        rounds=TOTAL_ROUNDS,
        loss_prob=LOSS_PROBABILITY,
        initial_cwnd=INITIAL_CWND,
        initial_ssthresh=INITIAL_SSTHRESH,
        seed=RANDOM_SEED,
        verbose=VERBOSE
    )

    # Save plot
    plot_cwnd(rounds, cwnd_hist, ssthresh=ssthresh_hist, filename="plot.png", show=False)

    # Optional: print a small textual summary
    print("\nSimulation summary (last values):")
    print(f"  rounds simulated : {TOTAL_ROUNDS}")
    print(f"  final cwnd       : {cwnd_hist[-1]:.3f}")
    print(f"  final ssthresh   : {ssthresh_hist[-1]:.3f}")
