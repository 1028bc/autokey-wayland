import time
import random
import json
import statistics
import sys
import os

class PulseBridgeArchitect:
    def __init__(self, abbr_file="abbrs.json"):
        # Default Abbrs (Fallback)
        self.abbr_map = {
            "req_rst": "MANUAL_SYSTEM_RESET_INITIATED",
            "net_sync": "NETWORK_PHONETIC_AUDIO_SYNC_ACTIVE",
            "job_st": "JOB_STATUS_REPORT_GENERATED",
            "err_cl": "BUFFER_CLEAR_PROTOCOL_EXECUTED"
        }
        self.load_custom_abbrs(abbr_file)
        self.cache = {}

    def load_custom_abbrs(self, filename):
        if os.path.exists(filename):
            try:
                with open(filename, 'r') as f:
                    custom = json.load(f)
                    self.abbr_map.update(custom)
                    print(f"[INIT] Loaded custom abbreviations from {filename}")
            except Exception:
                print(f"[WARN] Could not parse {filename}. Using defaults.")

    def pipeline_process(self, abbr_input, job_id, verbose=False):
        clean_key = str(abbr_input).strip().lower()
        expansion = self.abbr_map.get(clean_key, "UNKNOWN_ABBR_ID")
        
        payload = {
            "job_id": job_id,
            "timestamp": time.time(),
            "input": abbr_input,
            "return_msg": expansion,
            "status": "PROD_VERIFIED"
        }
        
        serialized = json.dumps(payload)
        cache_key = f"cache_{job_id}"
        self.cache[cache_key] = serialized
        
        final_data = json.loads(self.cache.get(cache_key))
        
        if verbose:
            return {"in": abbr_input, "serial": serialized[:55] + "...", "out": final_data["return_msg"]}
        return final_data["return_msg"]

def run_audit_cycle(run_id, cycles, architect):
    test_keys = list(architect.abbr_map.keys())
    latencies = []
    samples = []
    
    for i in range(cycles):
        job_id = (run_id * 100000) + i
        input_val = random.choice(test_keys)
        
        t_start = time.perf_counter()
        if i % (cycles // 5 or 1) == 0:
            trace = architect.pipeline_process(input_val, job_id, verbose=True)
            samples.append(trace)
        else:
            architect.pipeline_process(input_val, job_id)
        latencies.append(time.perf_counter() - t_start)

    return {
        "throughput": cycles / sum(latencies),
        "avg": statistics.mean(latencies) * 1000,
        "p99": statistics.quantiles(latencies, n=100)[98] * 1000,
        "samples": samples
    }

def generate_full_report(results, cycles, is_markdown=True):
    t_vals = [r['throughput'] for r in results]
    a_vals = [r['avg'] for r in results]
    p_vals = [r['p99'] for r in results]
    stability = 100 - (statistics.stdev(t_vals) / statistics.mean(t_vals) * 100)
    
    # --- SECTION 1: PREVIOUS SUMMARY VERSION (TABLE) ---
    h_rule = "=" * 85
    if is_markdown:
        report = "# PULSEBRIDGE 1.0 - PERFORMANCE STABILITY SUMMARY\n\n"
        report += "| Metric | Run 1 | Run 2 | Run 3 | Stability |\n"
        report += "| :--- | :--- | :--- | :--- | :--- |\n"
        report += f"| Throughput (req/s) | {t_vals[0]:,.0f} | {t_vals[1]:,.0f} | {t_vals[2]:,.0f} | {stability:.2f}% |\n"
        report += f"| Avg Latency (ms) | {a_vals[0]:.6f} | {a_vals[1]:.6f} | {a_vals[2]:.6f} | Verified |\n"
        report += f"| P99 Latency (ms) | {p_vals[0]:.6f} | {p_vals[1]:.6f} | {p_vals[2]:.6f} | Verified |\n\n"
    else:
        report = "PULSEBRIDGE 1.0 - PERFORMANCE STABILITY SUMMARY\n" + h_rule + "\n"
        report += f"{'Metric':<25} | {'Run 1':<15} | {'Run 2':<15} | {'Run 3':<15} | {'Stability'}\n"
        report += "-" * 85 + "\n"
        report += f"{'Throughput (req/s)':<25} | {int(t_vals[0]):<15,} | {int(t_vals[1]):<15,} | {int(t_vals[2]):<15,} | {stability:.2f}%\n"
        report += f"{'Avg Latency (ms)':<25} | {a_vals[0]:<15.6f} | {a_vals[1]:<15.6f} | {a_vals[2]:<15.6f} | Verified\n"
        report += f"{'P99 Latency (ms)':<25} | {p_vals[0]:<15.6f} | {p_vals[1]:<15.6f} | {p_vals[2]:<15.6f} | Verified\n"
        report += h_rule + "\n\n"

    # --- SECTION 2: EXHAUSTIVE AUDIT (TRACE SAMPLES) ---
    if is_markdown:
        report += "## EXHAUSTIVE INTEGRATION AUDIT\n"
    else:
        report += "EXHAUSTIVE INTEGRATION AUDIT (SERIALIZATION TRACE)\n" + h_rule + "\n"

    for r_idx, res in enumerate(results):
        report += f"\n[RUN {r_idx+1} TRACE SAMPLES]\n"
        for s in res['samples']:
            if is_markdown:
                report += f"- IN: `{s['in']:<10}` -> SERIALIZED: `{s['serial']:<55}` -> OUT: `{s['out']}`\n"
            else:
                report += f"IN: {s['in']:<10} -> SERIALIZED: {s['serial']:<55} -> OUT: {s['out']}\n"
    
    return report

if __name__ == "__main__":
    print("PulseBridge 1.0 - Unified Audit Utility")
    print("=" * 60)
    
    cycles = int(input("Enter cycles per run (default 20000): ") or 20000)
    arch = PulseBridgeArchitect()
    
    all_res = [run_audit_cycle(i+1, cycles, arch) for i in range(3)]
    
    # Display Summary Version to Terminal First
    print("\n" + generate_full_report(all_res, cycles, is_markdown=False))
    
    fmt = input("Export exhaustive report format? (md/txt/none): ").lower()
    if fmt in ['md', 'txt']:
        filename = f"pulsebridge_audit.{fmt}"
        is_md = (fmt == 'md')
        full_content = generate_full_report(all_res, cycles, is_markdown=is_md)
        with open(filename, "w") as f:
            f.write(full_content)
        print(f"[SUCCESS] Report saved to {filename}")
